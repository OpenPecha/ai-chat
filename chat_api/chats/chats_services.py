from chat_api.config import get
import httpx

async def get_chat_stream(email: str, query: str):
    input_data = {
        "messages": [
          {
            "role": "user",
            "content": query
          }
        ]
    }

    url = get("OPENPECHA_AI_URL")
    
    async with httpx.AsyncClient() as client:
        async with client.stream("POST", url, json=input_data) as response:
            # Stream the response chunks
            async for chunk in response.aiter_bytes():
                if chunk:
                    yield chunk