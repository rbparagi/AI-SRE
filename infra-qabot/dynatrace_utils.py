import requests
import os

DYNATRACE_URL = "https://<your_env>.live.dynatrace.com"
DYNATRACE_API_TOKEN = os.getenv("DYNATRACE_API_TOKEN")

def get_entity_id(service_name):
    url = f"{DYNATRACE_URL}/api/v2/entities"
    params = {
        "entitySelector": f"type(SERVICE),entityName.contains(\"{service_name}\")",
        "pageSize": 1
    }
    headers = {
        "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"
    }
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    return data["entities"][0]["entityId"] if data["entities"] else None

def get_cpu_usage(entity_id):
    url = f"{DYNATRACE_URL}/api/v2/metrics/query"
    params = {
        "metricSelector": "builtin:service.cpu.usage:avg:merge(0):avg",
        "entitySelector": f"entityId({entity_id})",
        "resolution": "5m",
        "from": "now-10m",
        "to": "now"
    }
    headers = {
        "Authorization": f"Api-Token {DYNATRACE_API_TOKEN}"
    }
    r = requests.get(url, headers=headers, params=params)
    data = r.json()
    try:
        val = data["result"][0]["data"][0]["values"][0]
        return round(val, 2)
    except:
        return None
