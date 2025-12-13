def escape_lt_gt_outside_tags_simple(text: str) -> str:
    """
    Простая и эффективная реализация с использованием конечного автомата.
    Заменяет символы '<' и '>' на '&lt;' и '&gt;' только в обычном тексте.

    Args:
        text: Текст для обработки

    Returns:
        str: Обработанный текст с экранированными символами вне тегов
    """
    result = []
    i = 0
    n = len(text)
    inside_tag = False
    inside_comment = False

    while i < n:
        char = text[i]

        if not inside_tag and not inside_comment:
            # Мы находимся в обычном тексте
            if char == '<':
                # Проверяем, начинается ли тег или комментарий
                if i + 3 < n and text[i:i + 4] == '<!--':
                    # Начинается комментарий
                    inside_comment = True
                    result.append('<!--')
                    i += 4
                    continue
                elif i + 8 < n and text[i:i + 9].upper() == '<!DOCTYPE':
                    # Начинается DOCTYPE
                    # Ищем конец DOCTYPE
                    end_pos = text.find('>', i)
                    if end_pos != -1:
                        result.append(text[i:end_pos + 1])
                        i = end_pos + 1
                        continue
                    else:
                        # Не нашли закрывающий >, добавляем как есть
                        result.append(text[i:])
                        break
                else:
                    # Возможно, начинается тег
                    # Проверяем следующие символы
                    j = i + 1
                    is_tag = False

                    while j < n and j < i + 50:  # Ограничиваем длину проверки
                        next_char = text[j]
                        if next_char == '>':
                            # Нашли закрывающую скобку - это тег
                            is_tag = True
                            break
                        elif next_char == '<' or next_char.isspace() and j > i + 20:
                            # Начался новый тег или слишком много пробелов - не тег
                            break
                        j += 1

                    if is_tag:
                        inside_tag = True
                        result.append('<')
                        i += 1
                        continue
                    else:
                        # Не тег, заменяем на &lt;
                        result.append('&lt;')
                        i += 1
                        continue
            elif char == '>':
                # В обычном тексте '>' заменяем
                result.append('&gt;')
                i += 1
                continue
            else:
                # Обычный символ
                result.append(char)
                i += 1
                continue

        elif inside_comment:
            # Мы внутри комментария
            result.append(char)

            # Проверяем, не заканчивается ли комментарий
            if char == '-' and i + 2 < n and text[i:i + 3] == '-->':
                result.append(text[i + 1:i + 3])  # добавляем '->'
                inside_comment = False
                i += 3
                continue

            i += 1
            continue

        elif inside_tag:
            # Мы внутри тега
            result.append(char)

            if char == '>':
                # Конец тега
                inside_tag = False

            i += 1
            continue

    return ''.join(result)
