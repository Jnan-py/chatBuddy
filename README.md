# ChatBuddy: Character Chatbot

ChatBuddy is a Streamlit-based character chatbot application that allows users to sign up, log in, and interact with custom chatbots. The app supports three main functionalities:

- **Chat**: Engage in conversation with your chosen chatbot.
- **Create Posts**: Generate creative posts based on a topic, tone, and length.
- **Tell a Story**: Generate a story by specifying genre, characters, and plot elements.

Additionally, ChatBuddy uses Google’s Generative AI (Gemini-2.0-flash) to generate responses and creative content, while storing conversation and creative histories in a local SQLite database.

## Features

- **User Authentication**: Secure sign-up and login using SQLite and bcrypt.
- **Custom Chatbots**: Create and manage multiple chatbots with custom instructions.
- **Conversational Chat**: Enjoy real-time interactions with your chatbot.
- **Creative Content Generation**: Generate creative posts and stories using a generative AI model.
- **Data Persistence**: All chat histories, creative content, and chatbot configurations are stored locally in a SQLite database (`chatbuddy.db`).

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/Jnan-py/chatBuddy.git
   cd chatBuddy
   ```

2. **Create a Virtual Environment (Recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root and add your Google API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   ```

## Usage

1. **Run the Application**

   ```bash
   streamlit run main.py
   ```

2. **Authentication**

   - Use the login form to sign in.
   - If you are a new user, sign up to create an account.  
     _Note:_ Upon signing up, default chatbots (e.g., "Travel Guide Bot" and "Motivational Coach Bot") are automatically created.

3. **Interact with ChatBuddy**
   - **Chat**: Select a chatbot from the sidebar and start a conversation.
   - **Create Posts / Tell a Story**: Use the provided forms to generate creative posts or stories. Generated content will be saved and can be reviewed later using the expanders.

## Project Structure

```
chatbuddy/
│
├── app.py                 # Main Streamlit application
├── chatbuddy.db           # SQLite database file (auto-generated)
├── .env                   # Environment variables (create this file)
├── requirements.txt       # Project dependencies
├── README.md              # Project documentation
```

## Technologies Used

- **Python** with Streamlit for the web interface
- **SQLite** for local data storage
- **bcrypt** for secure password hashing
- **Google Generative AI** for content generation
- **streamlit-option-menu** for sidebar navigation

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests with improvements or bug fixes.
