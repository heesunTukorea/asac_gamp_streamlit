import streamlit as st
import random
import time
from secrets_1 import *
import os
import sys
# sys.path.append(os.environ["VECTOR_DB_PATH"])
sys.path.append("home/ec2-user/workspace/workspace/vectorDB") 

from retriever_module import Retriever

review_retriever=Retriever("review")
meta_retriever=Retriever("meta")

m_test=meta_retriever.search("Please recommend a good park to visit with the family in California.")
r_test=review_retriever.search("Please recommend a California restaurant with good service")


# Streamed response emulator
def response_generator():
    # response = random.choice(
    #     [
    #         "Hello there! How can I assist you today?",
    #         "Hi, human! Is there anything I can help you with?",
    #         "Do you need help?",
    #     ]
    # )
    response=[m_test,r_test]
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Chat Bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})