from langchain.embeddings import GroqEmbeddings
from langchain.llms import Groq

def groq_embeddings(groq_api_key):
    return GroqEmbeddings(
        groq_api_key=groq_api_key
    )

def groq_llm(groq_api_key, model_name):
    return Groq(
        groq_api_key=groq_api_key,
        model_name=model_name
    )