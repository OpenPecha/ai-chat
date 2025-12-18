from chat_api.config import get
import requests

def get_chat_stream(email: str, query: str):
    input_data = {
        "messages": [
          {
            "role": "user",
            "content": query
          }
        ]
    }

    url = get("OPENPECHA_AI_URL")
    response = requests.post(url, json=input_data, stream=True)

    # Stream the response chunks
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            yield chunk