import base64
from ftouter import vision
from ftouter import chat, general, reasoning, tool_call
from dotenv import load_dotenv
load_dotenv()


with open("example.jpg", "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

result = vision.complete([
    {
        "role": "user",
        "content": [
            {"type": "text", "text": "what's in this image?"},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}"
                }
            }
        ]
    }
])
print(result["choices"][0]["message"]["content"])
