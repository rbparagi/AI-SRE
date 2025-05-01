import pandas as pd

def fake_openai_response(prompt):
    return f"🛠️ Suggestion based on: '{prompt}' → Check CPU load, restart application services, monitor scaling."

# 3. Load Server Metrics Data
data = {
    'Server': ['app-01', 'app-02', 'db-01', 'cache-01', 'web-01'],
    'CPU_Usage': [55, 92, 67, 45, 91],
    'Memory_Usage': [70, 65, 80, 50, 90],
    'Status': ['Healthy', 'Unhealthy', 'Unhealthy', 'Healthy', 'Unhealthy']
}

df = pd.DataFrame(data)

critical_servers = df[(df['CPU_Usage'] > 80) | (df['Status'] == 'Unhealthy')]

prompts = []
for index, row in critical_servers.iterrows():
    prompt = f"Server {row['Server']} has high CPU usage of {row['CPU_Usage']}% and status {row['Status']}. What should I do?"
    prompts.append(prompt)

# 4. Use OpenAI to get suggestions
suggestions = []
for prompt in prompts:
    suggestion = fake_openai_response(prompt)
    suggestions.append(suggestion)

# 5. Display suggestions
for server, suggestion in zip(critical_servers['Server'], suggestions):
    print(f"Suggestion for {server}: {suggestion}")

