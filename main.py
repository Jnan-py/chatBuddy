import streamlit as st 
# import torch 
# from transformers import pipeline , AutoModel , AutoTokenizer
# from huggingface_hub import login
# login("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")
# tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct')
# model = AutoModel.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
# pipe = pipeline('text-generation',model = model ,torch_dtype=torch.bfloat16,device_map = 'auto',use_auth_token='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')

import google.generativeai as genai 
from dotenv import load_dotenv
import os 

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.title("ChatBuddy")
st.subheader("Your chatting partner")

if 'messages' not in st.session_state:
        st.session_state.messages = []

        st.session_state.messages.append(
            {
                'role':'model',
                'parts':"""Welcome !! Explain in brief about the character of who you want to chat and start talking !! """
            }
        )
system_instruction = st.text_input("Describe the character of your chatbot")

for message in st.session_state.messages:
        row = st.columns(2)
        if message['role']=='user':
            row[1].chat_message(message['role']).markdown(message['parts'])
        else:
            row[0].chat_message(message['role']).markdown(message['parts'])


if system_instruction:
    model = genai.GenerativeModel(
        model_name='gemini-1.5-pro',
        system_instruction=system_instruction)

    chat = model.start_chat(
    history=st.session_state.messages
    )

    def resp(query,chat):
        response = chat.send_message(query)
        return response.text

    # for message in st.session_state.messages:
    #     row = st.columns(2)
    #     if message['role']=='user':
    #         row[1].chat_message(message['role']).markdown(message['parts'])
    #     else:
    #         row[0].chat_message(message['role']).markdown(message['parts'])

    try:
        user_question = st.chat_input("Enter your query here !!")

        if user_question:
            row_u = st.columns(2)
            row_u[1].chat_message('user').markdown(user_question)
            st.session_state.messages.append(
                {'role':'user',
                'parts':user_question}
            )

            resp = resp(user_question,chat)
            
            row_a = st.columns(2)
            row_a[0].chat_message('model').markdown(resp)
            st.session_state.messages.append(
                {'role':'model',
                'parts':resp}
            )

    except Exception as e:
        st.warning("""There is an error within the model, try to send the same message again (no information will be lost) 
        Or please try reloading the page after some time,
        {The information will be lost after reloading the page}""")
        

