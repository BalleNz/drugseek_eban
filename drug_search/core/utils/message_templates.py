class MessageTemplates:
    # ASSISTANT
    ASSISTANT_ANSWER_DRUGS = (
        "{answer}\n\n"
        "{drugs_section}"
    )

    # ARQ
    DRUG_CREATED_NOTIFICATION = (
        "<b>Препарат {name_ru} теперь доступен в вашей базе!</b>"
    )

    DRUG_UPDATED_NOTIFICATION = (
        "<b>Препарат {name_ru} успешно обновлен!</b>"
    )
