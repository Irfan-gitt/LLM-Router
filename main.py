from ftouter import chat, general, reasoning, tool_call
from dotenv import load_dotenv
load_dotenv()


result = chat.complete([{"role": "user", "content": "Say hi in 5 words"}])
print(result["choices"][0]["message"]["content"])

result = general.complete([{"role": "user", "content": "Say hi in 5 words"}])
print(result["choices"][0]["message"]["content"])

result = reasoning.complete([{"role": "user", "content": "Say hi in 5 words"}])
print(result["choices"][0]["message"]["content"])

result = tool_call.complete([{"role": "user", "content": "Say hi in 5 words"}])
print(result["choices"][0]["message"]["content"])
