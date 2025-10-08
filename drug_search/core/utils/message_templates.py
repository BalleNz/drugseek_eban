class MessageTemplates:
    # ASSISTANT
    ASSISTANT_ANSWER_DRUGS = (
        "{answer}\n\n"
        "<b>Список препаратов, которые вам помогут:</b>"
        "{drugs_section}"
    )

    # ARQ
    DRUG_CREATED_JOB_FINISHED = (
        "<b>Препарат {name_ru} теперь доступен в вашей базе!</b>"
    )
