class MessageTemplates:
    # [ ASSISTANT ]
    ASSISTANT_ANSWER_DRUGS = (
        "{answer}\n\n"
        "{drugs_section}"
    )

    ASSISTANT_ANSWER = (
        "<b>{header_with_emoji}</b>\n\n"
        "{content}"
        "<blockquote>"
        "💡 {conclusion_section}"
        "</blockquote>"
    )

    # [ ARQ ]
    DRUG_CREATED_NOTIFICATION = (
        "<i>{name_ru} теперь в вашей базе!</i>"
    )

    DRUG_UPDATED_NOTIFICATION = (
        "<i>Обновление {name_ru} завершено!</i>"
    )

    USER_DESCRIPTION_UPDATED = "<i>В вашем профиле появилось новое описание!</i>"
