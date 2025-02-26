import streamlit as st
import sqlite3
import bcrypt
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
import os
from streamlit_option_menu import option_menu

load_dotenv()
genai.configure(api_key = os.getenv("GOOGLE_API_KEY"))

def get_db_connection():
    conn = sqlite3.connect('chatbuddy.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chatbots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            instructions TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chatbot_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            role TEXT CHECK(role IN ('user', 'bot')) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chatbot_id) REFERENCES chatbots (id)
        )
    ''')

    conn.execute('''
        CREATE TABLE IF NOT EXISTS creative_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chatbot_id INTEGER NOT NULL,
            context TEXT CHECK(context IN ('post', 'story')) NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (chatbot_id) REFERENCES chatbots (id)
        )
    ''')

    conn.commit()
    conn.close()

create_tables()

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def sign_up(username, password):
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)',
                     (username, hash_password(password)))
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()
        create_default_chatbots(user_id)

def log_in(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user and verify_password(password, user['password_hash']):
        return user['id']
    return None

def create_default_chatbots(user_id):
    default_bots = [
        ('Travel Guide Bot', 'You are a knowledgeable travel guide providing information about destinations, itineraries, and cultural tips.'),
        ('Motivational Coach Bot', 'You are an enthusiastic motivational coach helping users achieve their goals with positive reinforcement.')
    ]
    conn = get_db_connection()
    for name, instructions in default_bots:
        conn.execute('INSERT INTO chatbots (user_id, name, instructions) VALUES (?, ?, ?)',
                    (user_id, name, instructions))
    conn.commit()
    conn.close()

def get_user_chatbots(user_id):
    conn = get_db_connection()
    chatbots = conn.execute('SELECT * FROM chatbots WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return [dict(chatbot) for chatbot in chatbots]

def create_chatbot(user_id, name, instructions):
    conn = get_db_connection()
    conn.execute('INSERT INTO chatbots (user_id, name, instructions) VALUES (?, ?, ?)',
                (user_id, name, instructions))
    conn.commit()
    conn.close()

def save_message(chatbot_id, content, role):
    conn = get_db_connection()
    conn.execute('INSERT INTO messages (chatbot_id, content, role) VALUES (?, ?, ?)',
                (chatbot_id, content, role))
    conn.commit()
    conn.close()

def get_chat_history(chatbot_id):
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT * FROM messages 
        WHERE chatbot_id = ? 
        ORDER BY created_at ASC
    ''', (chatbot_id,)).fetchall()
    conn.close()
    return messages

def save_creative_message(chatbot_id, context, prompt, response):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO creative_messages (chatbot_id, context, prompt, response)
        VALUES (?, ?, ?, ?)
    ''', (chatbot_id, context, prompt, response))
    conn.commit()
    conn.close()

def get_creative_history(chatbot_id, context):
    conn = get_db_connection()
    records = conn.execute('''
        SELECT * FROM creative_messages
        WHERE chatbot_id = ? AND context = ?
        ORDER BY created_at DESC
    ''', (chatbot_id, context)).fetchall()
    conn.close()
    return [dict(record) for record in records]


def main():
    st.set_page_config(page_title="ChatBuddy", layout="wide")
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'active_chatbot' not in st.session_state:
        st.session_state.active_chatbot = None
    if 'messages' not in st.session_state:
        st.session_state.messages = {}

    if not st.session_state.user_id:
        st.title("ChatBuddy Login")
        with st.sidebar:
            st.markdown("Login to access Chatbots")
            auth_type = st.radio("Choose Action", ["Login", "Sign Up"], horizontal=True)

        if auth_type == "Login":
            st.header("Login")
        
        else:
            st.header("Sign Up")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Submit"):
            if auth_type == "Login":
                user_id = log_in(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            else:
                if sign_up(username, password):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error("Username already exists")
        return

    st.title("ChatBuddy")
    st.sidebar.title("ChatBuddy")

    with st.sidebar:
        st.header("Your Chatbots")

        if 'show_new_chatbot_form' not in st.session_state:
            st.session_state.show_new_chatbot_form = False

        if st.button("+ Create New Chatbot"):
            st.session_state.show_new_chatbot_form = True

        if st.session_state.show_new_chatbot_form:
            with st.form("new_chatbot"):
                name = st.text_input("Chatbot Name")
                instructions = st.text_area("Instructions")
                submitted = st.form_submit_button("Create")
                if submitted:
                    create_chatbot(st.session_state.user_id, name, instructions)
                    st.success("Chatbot created!")
                    st.session_state.show_new_chatbot_form = False

        chatbots = get_user_chatbots(st.session_state.user_id)
        selected_chatbot = st.selectbox(
            "Select Chatbot",
            chatbots,
            format_func=lambda x: x['name'],
            index=0,
            key="chatbot_selector"
        )
        if selected_chatbot:
            st.session_state.active_chatbot = selected_chatbot['id']


    if st.session_state.active_chatbot:
        option = option_menu(menu_title=None,options = ["Chat", "Create Posts", "Tell a Story"], orientation = "horizontal")
    
        if option == "Chat":
            if st.session_state.active_chatbot not in st.session_state.messages:
                st.session_state.messages[st.session_state.active_chatbot] = []
                for msg in get_chat_history(st.session_state.active_chatbot):
                    st.session_state.messages[st.session_state.active_chatbot].append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            for msg in st.session_state.messages.get(st.session_state.active_chatbot, []):
                with st.chat_message(msg['role']):
                    st.write(msg['content'])
            
            prompt = st.chat_input("Type your message...")

            if prompt:
                with st.chat_message("user"):
                    st.write(prompt)
                st.session_state.messages[st.session_state.active_chatbot].append(
                    {'role': 'user', 'content': prompt}
                )
                save_message(st.session_state.active_chatbot, prompt, 'user')

                conn = get_db_connection()
                chatbot = conn.execute('SELECT * FROM chatbots WHERE id = ?', (st.session_state.active_chatbot,)).fetchone()
                conn.close()
                
                try:
                    model = genai.GenerativeModel('gemini-2.0-flash', 
                                                system_instruction=chatbot['instructions'])

                    chat_history = []
                    for msg in get_chat_history(st.session_state.active_chatbot):
                        role = 'user' if msg['role'] == 'user' else 'model'
                        chat_history.append({'role': role, 'parts': [msg['content']]})

                    chat = model.start_chat(history=chat_history)
                    with st.spinner("Thinking.."):
                        response = chat.send_message(prompt)
                        
                    bot_response = response.text

                    with st.chat_message("bot"):
                        st.write(bot_response)
                    st.session_state.messages[st.session_state.active_chatbot].append(
                        {'role': 'bot', 'content': bot_response}
                    )
                    save_message(st.session_state.active_chatbot, bot_response, 'bot')

                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")

        elif option == "Create Posts":
            with st.form("post_form"):
                topic = st.text_input("Post Topic")
                tone = st.selectbox("Tone", ["Formal", "Casual", "Humorous"])
                length = st.selectbox("Length", ["Short", "Medium", "Long"])
                submitted = st.form_submit_button("Generate Post")
            
            if submitted:
                try:
                    conn = get_db_connection()
                    chatbot = conn.execute('SELECT * FROM chatbots WHERE id = ?', (st.session_state.active_chatbot,)).fetchone()
                    conn.close()

                    model = genai.GenerativeModel('gemini-2.0-flash', 
                                                system_instruction=chatbot['instructions'])
                    
                    prompt_text = f"Create a {tone.lower()} post about {topic}. The length should be {length.lower()}."
                    response = model.generate_content(prompt_text)
                    
                    if response.text:
                        st.subheader("Generated Post")
                        st.write(response.text)
                        save_creative_message(st.session_state.active_chatbot, 'post', prompt_text, response.text)

                    else:
                        st.error("Failed to generate post")
                except Exception as e:
                    st.error(f"Error generating post: {str(e)}")
        
            with st.expander("Show Previous Posts"):
                history = get_creative_history(st.session_state.active_chatbot, 'post')
                if history:
                    for record in history:
                        st.write(f"**Prompt:** {record['prompt']}")
                        st.write(f"**Response:** {record['response']}")
                        st.write(f"_(Created at: {record['created_at']})_")
                        st.markdown("---")
                else:
                    st.write("No previous posts found.")
            
        elif option == "Tell a Story":
            with st.form("story_form"):
                genre = st.selectbox("Genre", ["Fantasy", "Mystery", "Sci-Fi"])
                characters = st.text_input("Main Characters")
                plot = st.text_area("Plot Elements")
                length = st.selectbox("Length", ["Short", "Medium", "Long"])
                submitted = st.form_submit_button("Generate Story")
            
            if submitted:
                try:
                    conn = get_db_connection()
                    chatbot = conn.execute('SELECT * FROM chatbots WHERE id = ?', (st.session_state.active_chatbot,)).fetchone()
                    conn.close()
                    
                    model = genai.GenerativeModel('gemini-2.0-flash', 
                                                system_instruction=chatbot['instructions'])
                    
                    prompt_text = f"Generate a {length.lower()} {genre.lower()} story featuring {characters}. Plot elements: {plot}"
                    response = model.generate_content(prompt_text)
                    
                    if response.text:
                        st.subheader("Generated Story")
                        st.write(response.text)
                        save_creative_message(st.session_state.active_chatbot, 'story', prompt_text, response.text)

                    else:
                        st.error("Failed to generate story")

                except Exception as e:
                    st.error(f"Error generating story: {str(e)}")
            
            with st.expander("Show Previous Stories"):
                history = get_creative_history(st.session_state.active_chatbot, 'story')
                if history:
                    for record in history:
                        st.write(f"**Prompt:** {record['prompt']}")
                        st.write(f"**Response:** {record['response']}")
                        st.write(f"_(Created at: {record['created_at']})_")
                        st.markdown("---")
                else:
                    st.write("No previous stories found.")

    else:
        st.info("Please select or create a chatbot from the sidebar")

if __name__ == "__main__":
    main()