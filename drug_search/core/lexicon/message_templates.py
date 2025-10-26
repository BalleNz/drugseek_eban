class MessageTemplates:
    # ASSISTANT
    ASSISTANT_ANSWER_DRUGS = (
        "{answer}\n\n"
        "{drugs_section}"
    )

    # ARQ
    DRUG_CREATED_NOTIFICATION = (
        "<i>Препарат {name_ru} теперь доступен в вашей базе!</i>"
    )

    DRUG_UPDATED_NOTIFICATION = (
        "<i>Препарат {name_ru} успешно обновлен!</i>"
    )

    USER_DESCRIPTION_UPDATED = "<i>В вашем профиле появилось новое описание!</i>"
