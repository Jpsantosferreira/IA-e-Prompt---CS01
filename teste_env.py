from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv(override=True)  # força o .env a vencer qualquer env var do sistema
chave = os.getenv("OPENAI_API_KEY")
print("Tamanho da chave lida:", len(chave) if chave else None)
print("Começa com sk-proj-:", chave.startswith("sk-proj-") if chave else None)

client = OpenAI(api_key=chave)
resp = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "oi"}],
)
print(repr(chave))