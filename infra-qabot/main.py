import streamlit as st
import os
from dynatrace_utils import get_entity_id, get_cpu_usage
from openai_utils import ask_openai

st.title("🧠 Infra Q&A Bot - Dynatrace + GPT")

service = st.text_input("Enter Kubernetes service name:")

if st.button("Check CPU Health"):
    with st.spinner("Getting entity ID..."):
        entity_id = get_entity_id(service)

    if entity_id:
        with st.spinner("Fetching CPU data..."):
            cpu = get_cpu_usage(entity_id)

        if cpu is not None:
            with st.spinner("Asking GPT for summary..."):
                result = ask_openai(service, cpu)
                st.success(result)
        else:
            st.error("Could not fetch CPU usage.")
    else:
        st.error("Service not found in Dynatrace.")
