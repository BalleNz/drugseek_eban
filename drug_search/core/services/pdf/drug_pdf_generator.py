"""Генерация PDF-карточки препарата в фирменном бело-синем стиле."""

from __future__ import annotations

import io
import math
import re
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer

from drug_search.core.schemas import DrugSchema

FONT_REGULAR = "DrugSearchRegular"
FONT_BOLD = "DrugSearchBold"

COLOR_PRIMARY = colors.HexColor("#0066CC")
COLOR_PRIMARY_LIGHT = colors.HexColor("#E8F4FD")
COLOR_PRIMARY_SOFT = colors.HexColor("#B3D9FF")
COLOR_TEXT = colors.HexColor("#1A2B4A")
COLOR_MUTED = colors.HexColor("#5A7299")
COLOR_WHITE = colors.white

SYRINGE_POSITIONS: tuple[tuple[float, float, float, float], ...] = (
    (1.2 * cm, A4[1] - 1.8 * cm, 25, 0.12),
    (5.5 * cm, A4[1] - 2.6 * cm, -18, 0.10),
    (10.0 * cm, A4[1] - 1.5 * cm, 35, 0.11),
    (14.5 * cm, A4[1] - 2.8 * cm, -8, 0.09),
    (17.5 * cm, A4[1] - 1.6 * cm, 42, 0.13),
    (2.0 * cm, 1.4 * cm, 160, 0.08),
    (8.0 * cm, 2.0 * cm, 200, 0.07),
    (14.0 * cm, 1.2 * cm, 135, 0.09),
)


def _strip_html(text: str | None) -> str:
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return cleaned.replace("&nbsp;", " ").strip()


def _register_fonts() -> None:
    if FONT_REGULAR in pdfmetrics.getRegisteredFontNames():
        return

    assets_dir = Path(__file__).resolve().parents[2] / "assets" / "fonts"
    candidates = [
        (assets_dir / "DejaVuSans.ttf", assets_dir / "DejaVuSans-Bold.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")),
        (Path("/Library/Fonts/Arial Unicode.ttf"), Path("/Library/Fonts/Arial Unicode.ttf")),
        (Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
         Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")),
    ]

    for regular, bold in candidates:
        if regular.exists():
            pdfmetrics.registerFont(TTFont(FONT_REGULAR, str(regular)))
            bold_path = bold if bold.exists() else regular
            pdfmetrics.registerFont(TTFont(FONT_BOLD, str(bold_path)))
            return

    raise RuntimeError("Не найден шрифт с поддержкой кириллицы для PDF")


def _draw_syringe(canvas, x: float, y: float, angle_deg: float, scale: float, alpha: float) -> None:
    canvas.saveState()
    canvas.setFillColorRGB(0, 0.4, 0.8, alpha=alpha)
    canvas.setStrokeColorRGB(0, 0.35, 0.75, alpha=alpha * 1.2)
    canvas.setLineWidth(0.6 * scale)
    canvas.translate(x, y)
    canvas.rotate(angle_deg)

    barrel_w = 34 * scale
    barrel_h = 7 * scale
    canvas.roundRect(0, 0, barrel_w, barrel_h, 2 * scale, fill=1, stroke=0)

    plunger_w = 14 * scale
    canvas.rect(-plunger_w, 1.5 * scale, plunger_w, 4 * scale, fill=1, stroke=0)

    canvas.setFillColorRGB(0.75, 0.88, 1.0, alpha=alpha * 0.9)
    canvas.rect(4 * scale, 1.5 * scale, barrel_w * 0.55, 4 * scale, fill=1, stroke=0)

    canvas.setStrokeColorRGB(0.5, 0.65, 0.85, alpha=alpha)
    canvas.line(barrel_w, barrel_h / 2, barrel_w + 14 * scale, barrel_h / 2)

    for tick in range(4):
        tick_x = barrel_w * 0.25 + tick * 5 * scale
        canvas.line(tick_x, barrel_h, tick_x, barrel_h + 2.5 * scale)

    canvas.restoreState()


def _draw_page_decorations(canvas, doc) -> None:  # noqa
    width, height = A4

    canvas.saveState()
    canvas.setFillColor(COLOR_PRIMARY_LIGHT)
    canvas.rect(0, height - 3.2 * cm, width, 3.2 * cm, fill=1, stroke=0)

    canvas.setFillColor(COLOR_PRIMARY)
    canvas.rect(0, height - 3.25 * cm, width, 0.12 * cm, fill=1, stroke=0)

    for x, y, angle, scale in SYRINGE_POSITIONS:
        _draw_syringe(canvas, x, y, angle, scale, alpha=0.22)

    canvas.setFillColor(COLOR_PRIMARY_SOFT)
    for i in range(6):
        canvas.circle(
            width - 1.5 * cm - i * 0.35 * cm,
            height - 1.6 * cm + math.sin(i) * 0.2 * cm,
            0.08 * cm,
            fill=1,
            stroke=0,
        )

    canvas.setFillColor(COLOR_PRIMARY)
    canvas.setFont(FONT_BOLD, 9)
    canvas.drawString(1.5 * cm, 1.0 * cm, doc.footer_text)

    canvas.setFillColor(COLOR_MUTED)
    canvas.setFont(FONT_REGULAR, 8)
    canvas.drawRightString(width - 1.5 * cm, 1.0 * cm, f"DrugSearch · стр. {canvas.getPageNumber()}")

    canvas.restoreState()


class DrugPdfGenerator:
    """Создаёт брендированный PDF-dossier по препарату."""

    def __init__(self):
        _register_fonts()

    def generate(
            self,
            drug: DrugSchema,
            referral_url: str | None = None,
            bot_username: str = "drugseek_bot",
    ) -> bytes:
        buffer = io.BytesIO()
        footer = (
            f"Разобрать любой препарат → t.me/{bot_username}"
            if not referral_url
            else f"Мой бот → {referral_url}"
        )

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=1.8 * cm,
            rightMargin=1.8 * cm,
            topMargin=3.6 * cm,
            bottomMargin=2.0 * cm,
            title=f"{drug.name_ru or drug.name} — DrugSearch",
            author="DrugSearch Bot",
        )
        doc.footer_text = footer

        styles = self._build_styles()
        story = []

        display_name = drug.name_ru or drug.name
        story.extend(self._build_cover(styles, drug, display_name))
        story.append(Spacer(1, 0.4 * cm))

        for title, body in self._build_sections(drug):
            if not body:
                continue
            story.append(Paragraph(title, styles["section"]))
            story.append(HRFlowable(width="100%", thickness=1, color=COLOR_PRIMARY_SOFT, spaceAfter=8))
            story.append(Paragraph(body, styles["body"]))
            story.append(Spacer(1, 0.35 * cm))

        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("DrugSearch Pharma Card", styles["footer_title"]))
        story.append(
            Paragraph(
                f"Полная база препаратов, викторина и AI-ассистент — "
                f"<b>t.me/{bot_username}</b>",
                styles["footer"],
            )
        )
        if referral_url:
            story.append(
                Paragraph(
                    f"Пригласи друга и получи токены: {referral_url}",
                    styles["footer_muted"],
                )
            )

        doc.build(
            story,
            onFirstPage=_draw_page_decorations,
            onLaterPages=_draw_page_decorations,
        )
        return buffer.getvalue()

    def _build_styles(self) -> dict[str, ParagraphStyle]:
        base = getSampleStyleSheet()
        return {
            "cover_title": ParagraphStyle(
                "CoverTitle",
                parent=base["Title"],
                fontName=FONT_BOLD,
                fontSize=24,
                leading=28,
                textColor=COLOR_PRIMARY,
                alignment=TA_CENTER,
                spaceAfter=6,
            ),
            "cover_sub": ParagraphStyle(
                "CoverSub",
                parent=base["Normal"],
                fontName=FONT_REGULAR,
                fontSize=11,
                leading=14,
                textColor=COLOR_MUTED,
                alignment=TA_CENTER,
                spaceAfter=4,
            ),
            "cover_tag": ParagraphStyle(
                "CoverTag",
                parent=base["Normal"],
                fontName=FONT_BOLD,
                fontSize=10,
                textColor=COLOR_WHITE,
                backColor=COLOR_PRIMARY,
                alignment=TA_CENTER,
                borderPadding=6,
                spaceBefore=8,
                spaceAfter=12,
            ),
            "section": ParagraphStyle(
                "Section",
                parent=base["Heading2"],
                fontName=FONT_BOLD,
                fontSize=13,
                textColor=COLOR_PRIMARY,
                spaceBefore=10,
                spaceAfter=4,
            ),
            "body": ParagraphStyle(
                "Body",
                parent=base["Normal"],
                fontName=FONT_REGULAR,
                fontSize=10,
                leading=14,
                textColor=COLOR_TEXT,
                alignment=TA_JUSTIFY,
            ),
            "footer_title": ParagraphStyle(
                "FooterTitle",
                parent=base["Normal"],
                fontName=FONT_BOLD,
                fontSize=11,
                textColor=COLOR_PRIMARY,
                alignment=TA_CENTER,
            ),
            "footer": ParagraphStyle(
                "Footer",
                parent=base["Normal"],
                fontName=FONT_REGULAR,
                fontSize=9,
                textColor=COLOR_TEXT,
                alignment=TA_CENTER,
                spaceBefore=4,
            ),
            "footer_muted": ParagraphStyle(
                "FooterMuted",
                parent=base["Normal"],
                fontName=FONT_REGULAR,
                fontSize=8,
                textColor=COLOR_MUTED,
                alignment=TA_CENTER,
                spaceBefore=6,
            ),
        }

    def _build_cover(
            self,
            styles: dict[str, ParagraphStyle],
            drug: DrugSchema,
            display_name: str,
    ) -> list:
        latin = drug.latin_name or drug.name
        classification = _strip_html(drug.classification) or "Фармакология"

        return [
            Spacer(1, 0.6 * cm),
            Paragraph("DRUGSEARCH PHARMA CARD", styles["cover_tag"]),
            Paragraph(display_name, styles["cover_title"]),
            Paragraph(f"{drug.name} · {latin}", styles["cover_sub"]),
            Paragraph(classification, styles["cover_sub"]),
            Spacer(1, 0.2 * cm),
        ]

    def _build_sections(self, drug: DrugSchema) -> Iterable[tuple[str, str]]:
        if drug.description:
            yield "Описание", self._escape(_strip_html(drug.description))

        if drug.clinical_effects:
            yield "Клинические эффекты", self._escape(_strip_html(drug.clinical_effects))

        if drug.primary_action:
            mechanism = _strip_html(drug.primary_action)
            if drug.secondary_actions:
                mechanism += f"\n\nВторичные действия: {_strip_html(drug.secondary_actions)}"
            yield "Механизм действия", self._escape(mechanism)

        if drug.dosages:
            lines = []
            for dosage in drug.dosages[:8]:
                line = f"• {dosage.route}: {dosage.per_time or dosage.method or '—'}"
                if dosage.max_day:
                    line += f" (макс. {dosage.max_day}/день)"
                lines.append(line)
            yield "Дозировки", self._escape("\n".join(lines))

        if drug.combinations:
            good, bad = [], []
            for combo in drug.combinations[:6]:
                entry = f"• {combo.substance}: {_strip_html(combo.effect)}"
                if combo.combination_type.value == "good":
                    good.append(entry)
                else:
                    bad.append(entry + f" — {_strip_html(combo.risks)}")
            combo_text = ""
            if good:
                combo_text += "Синергия:\n" + "\n".join(good)
            if bad:
                combo_text += "\n\nРиски:\n" + "\n".join(bad)
            if combo_text:
                yield "Комбинации", self._escape(combo_text)

        if drug.fact:
            yield "Интересный факт", self._escape(_strip_html(drug.fact))

        if drug.analogs:
            analog_lines = [
                f"• {a.analog_name} ({a.percent}% сходства)"
                for a in drug.analogs[:5]
            ]
            yield "Аналоги", self._escape("\n".join(analog_lines))

    @staticmethod
    def _escape(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>")
        )
