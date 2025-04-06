from fastapi import FastAPI
from pydantic import BaseModel
import openai
import requests
import os
from datetime import datetime, timedelta

app = FastAPI()

# Set your API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DT_API_TOKEN = os.getenv("DT_API_TOKEN")
DT_ENV_URL = os.getenv("DT_ENV_URL")  # Example: "https://abc.live.dynatrace.com"

openai.api_key = OPENAI_API_KEY

class QueryRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_ai(request: QueryRequest):
    user_question = request.question

    # Step 1: Use OpenAI to translate natural language to Dynatrace API call
    system_prompt = """
    You are an assistant that converts SRE natural language questions into Dynatrace API call details.
    Respond ONLY with:
    1. The Dynatrace API endpoint (e.g., /api/v2/metrics/query)
    2. Query parameters in JSON format
    3. A short explanation of what you're doing

    Use this mapping:
    - CPU usage -> builtin:kubernetes.pod.cpu.usage or builtin:host.cpu.usage
    - Memory usage -> builtin:kubernetes.pod.memory.usage or builtin:host.mem.usage
    - Restart count -> builtin:kubernetes.container.restarts

    Entity types:
    - Pod -> KUBERNETES_POD
    - Deployment -> KUBERNETES_DEPLOYMENT
    - DaemonSet -> KUBERNETES_DAEMONSET
    - Node -> KUBERNETES_NODE
    - Host/VM -> HOST
    - Process -> PROCESS_GROUP_INSTANCE

    Time should be relative ISO timestamps like now-30m, now-1h
    """

    ai_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
    )

    parsed = ai_response.choices[0].message.content
    # Simple parsing logic (in production, use a structured approach)
    import json, re
    try:
        endpoint = re.search(r"endpoint\":\s*\"(.*?)\"", parsed).group(1)
        params_str = re.search(r"params\":\s*({.*})", parsed, re.DOTALL).group(1)
        params = json.loads(params_str)
    except:
        return {"error": "Failed to parse OpenAI response", "raw": parsed}

    # Step 2: Call Dynatrace with parsed endpoint and params
    headers = {
        "Authorization": f"Api-Token {DT_API_TOKEN}"
    }

    dynatrace_url = f"{DT_ENV_URL}{endpoint}"
    response = requests.get(dynatrace_url, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": "Dynatrace API error", "status_code": response.status_code, "details": response.text}

    dt_data = response.json()

    # Step 3: Summarize Dynatrace data using OpenAI
    prompt_summary = f"""
    You are an SRE assistant. Below is a response from Dynatrace about infrastructure metrics.
    Summarize key insights, and if possible, list the top resource consumers:

    {dt_data}
    """

    completion = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert SRE assistant."},
            {"role": "user", "content": prompt_summary}
        ]
    )

    summary = completion.choices[0].message.content
    return {
        "question": user_question,
        "dynatrace_api_called": dynatrace_url,
        "query_params": params,
        "openai_summary": summary
    }
