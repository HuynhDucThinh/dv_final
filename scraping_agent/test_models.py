import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

models = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'llama-3.3-70b-versatile', 'llama-3.1-8b-instant']
for model in models:
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{'role': 'user', 'content': 'Return only valid JSON: {"result": "hello"}'}],
            response_format={'type': 'json_object'},
            max_tokens=50
        )
        print(f'OK json_object: {model}')
    except Exception as e:
        print(f'FAIL json_object: {model} -> {str(e)[:80]}')
