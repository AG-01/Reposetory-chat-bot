import streamlit as st
import requests
import os
from dotenv import load_dotenv
from .constants import *



def credentials():
    # Load environment variables
    load_dotenv()

    with st.sidebar:
        st.title("Model Selection", help=AUTHENTICATION_HELP)
        model_option = st.selectbox('Choose GROQ Model', ['LLaMA2-70b-4096', 'Mixtral-8x7b-32768'])
        
        with st.form("model_selection"):
            submit_selection = st.form_submit_button("Submit")
    
    if submit_selection:
        with st.spinner("Validating credentials..."):
            al_token = os.getenv('ACTIVELOOP_TOKEN')
            groq_api_key = os.getenv('GROQ_API_KEY')
            
            if not al_token or not groq_api_key:
                st.error("Missing API keys in environment file. Please check your .env file.")
                st.stop()
            
            if check_al(al_token) and check_groq(groq_api_key):
                st.session_state["al_token"] = al_token
                st.session_state["groq_api_key"] = groq_api_key
                st.session_state["model_option"] = model_option
                st.session_state["auth_ok"] = True
                st.success("Credentials validated. You can now enter the GitHub Repository Link.")
    
    return model_option
def check_al(al_token):
    headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {al_token}"
    }
    response = requests.get("https://app.activeloop.ai/api/user/profile", headers=headers)
    profile_data = response.json()

    if profile_data["name"] != "public":
        al_org_name = profile_data["name"]
        st.session_state["al_org_name"] = al_org_name
        return True
    st.error("Enter valid Activeloop token")
    st.stop()
    
def check_groq(groq_api_key):
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "mixtral-8x7b-32768",
        "messages": [
            {"role": "user", "content": "Hello, are you there?"}
        ]
    }
    
    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            st.error(f"GROQ API returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to GROQ API: {e}")
        return False