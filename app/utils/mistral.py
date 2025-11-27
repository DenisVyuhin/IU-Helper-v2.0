import os
import dotenv

from mistralai import Mistral
from openai import AsyncOpenAI


dotenv.load_dotenv()


# Оциальная асихронная функция от Mistral AI
async def mistral_ai(prompt: str) -> str:
   async with Mistral(
      api_key=os.getenv("MISTRAL_API_KEY", ""),
   ) as mistral:
      res = await mistral.chat.complete_async(model="mistral-large-latest", messages=[
         {
            "content": prompt,
            "role": "user",
         },
      ], stream=False)
      
      return res.choices[0].message.content


# API with DeepSeek
client = AsyncOpenAI(
   base_url="https://openrouter.ai/api/v1",
   api_key=os.getenv("DEEPSEEK_API_KEY", "")
)

async def deepseek_ai(prompt: str) -> str:
   completion = await client.chat.completions.create(
      extra_body={},
      model="mistralai/ministral-8b",
      messages=[
         {
            "role": "user",
            "content": str(prompt)
      }
      ]
   )
   return completion.choices[0].message.content