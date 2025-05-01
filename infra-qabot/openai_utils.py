import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_openai(service_name, cpu_usage):
    prompt = f"""
Service Name: {service_name}
Current CPU Usage: {cpu_usage}%

Provide a short health summary and recommendation.
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response['choices'][0]['message']['content']
