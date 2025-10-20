import json
import os
import textwrap
import time

from api.sysp import system_prompt
from google import genai
from google.genai.types import Content, GenerateContentConfig, Part, Tool

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = 'gemini-2.5-flash'

try:
    client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print("Error %s" % e)

sys_prompt = textwrap.dedent(system_prompt).strip()

config = GenerateContentConfig(
    system_instruction=sys_prompt,
    temperature=0.3,
)

result = []
with open('quant_eval_questions.json') as q:
    questions = json.load(q)

    for question in questions:
        resp = client.models.generate_content(model=MODEL_NAME, config=config, contents=question)
        print(f"Question: {question}\nAnswer: {resp.text}\n\n")
        result.append((question, resp.text))
        time.sleep(1)
with open('quant_responses.json', 'w+') as out:
    json.dump(result, out)


