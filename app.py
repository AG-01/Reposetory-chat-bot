import streamlit as st
import os
from dotenv import load_dotenv

from repochat.utils import init_session_state
from repochat.credentials import credentials
from repochat.git import git_form
from repochat.db import vector_db, load_to_db
from repochat.models import groq_embeddings, groq_llm
from repochat.chain import response_chain

# Load environment variables
load_dotenv()

init_session_state()

st.set_page_config(
    page_title="RepoChat",
    page_icon="💻",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "No need to worry if you can't understand GitHub code or repositories anymore! Introducing RepoChat, where you can effortlessly chat and discuss all things related to GitHub repositories."
    }
)

st.markdown(
    "<h1 style='text-align: center;'>RepoChat</h1>",
    unsafe_allow_html=True
)

model_option = credentials()

if st.session_state["auth_ok"]:
    try:
        db_name, st.session_state['git_form'] = git_form(st.session_state['repo_path'])

        if st.session_state['git_form']:
            st.session_state["db_path"] = f"hub://{st.session_state['al_org_name']}/{db_name}"

            groq_api_key = os.getenv('GROQ_API_KEY')
            st.session_state['embeddings'] = groq_embeddings(groq_api_key)
            st.session_state['llm'] = groq_llm(groq_api_key, model_option)

            with st.spinner('Loading the contents to database. This may take some time...'):
                st.session_state["deeplake_db"] = vector_db(
                    st.session_state['embeddings'],
                    load_to_db(st.session_state['repo_path'])
                )

            st.session_state["db_loaded"] = True
    except TypeError:
        pass

if st.session_state["db_loaded"]:
    st.session_state["qa"] = response_chain( 
        db=st.session_state["deeplake_db"],
        llm=st.session_state['llm']
    )
    
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Enter your query"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            with st.spinner("Generating response..."):
                result = st.session_state["qa"]({"question": prompt, "chat_history": st.session_state['messages']})
                st.write(result['answer'])
        st.session_state["messages"].append({"role": "assistant", "content": result['answer']})