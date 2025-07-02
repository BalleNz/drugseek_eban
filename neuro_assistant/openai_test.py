from openai import OpenAI

client = OpenAI(api_key="sk-e4b9f0ecdbb14ca486bdc73f2a4a128f", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Ты — помощник, который предоставляет информацию о дозировках препаратов. "
                                      "Ты должен вернуть ответ в строгом формате JSON. "
                                      "Формат: {\"dosages\": {\"peroral\": {\"per_time\": \"<доза>\", \"max_day\": \"<доза>\"}, \"parental\": {\"per_time\": \"<доза>\", \"max_day\": \"<доза>\"}}}. "
                                      "Если информация по какому-то пути введения отсутствует, укажи None. "
                                      "Используй только данные с авторитетных источников, например drugs.com и drugbank.com."
                                      "Если дозировки в разных источниках разные, возьми средний показатель."
                                      ""},
        {"role": "user", "content": "небиволол"}],
    response_format={"type": "json_object"},
    temperature=0.3,
)

if __name__ == "__main__":
    print(response.choices[0].message.content.model_d)