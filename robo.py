import os
from dotenv import load_dotenv
import openai
import streamlit as st

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("api_key")

# Function to get exactly three emojis from the AI
def get_emojis_from_ai(description, character):
    prompt = f"Respond with exactly three emojis that best represent this character description: '{description}' or just the character: '{character}'. Only respond with the three emojis and nothing else."
    retries = 3
    for _ in range(retries):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0.5
        )
        emojis = response['choices'][0]['message']['content'].strip()
        if len(emojis) <= 40:  # Simplified validation
            return emojis
    return "🤖🤖🤖"  # Fallback

# Default values
default_character = "Character"
default_character_description = "An assistant with a unique personality"

# Initialize session state
if "character" not in st.session_state:
    st.session_state.character = default_character
if "character_description" not in st.session_state:
    st.session_state.character_description = default_character_description
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": f"You are {st.session_state.character}, {st.session_state.character_description}."}
    ]
if "emojis" not in st.session_state:
    # Generate emojis only on first load
    st.session_state.emojis = get_emojis_from_ai(default_character_description, default_character)


# App title with persisted emojis
st.title(f"Chat with {st.session_state.character} {st.session_state.emojis}")

# Toggle for character input
if "show_character_inputs" not in st.session_state:
    st.session_state.show_character_inputs = False

if st.button("Set AI"):
    st.session_state.show_character_inputs = not st.session_state.show_character_inputs

# Character input fields
if st.session_state.show_character_inputs:
    new_character = st.text_input("Enter the character:", value=st.session_state.character)
    new_character_description = st.text_area("Describe the character:", value=st.session_state.character_description)

    if st.button("Update"):
        st.session_state.character = new_character
        st.session_state.character_description = new_character_description
        # Update emojis only when character or description changes
        st.session_state.emojis = get_emojis_from_ai(new_character_description, new_character)
        st.session_state.messages = [
            {"role": "system", "content": f"You are {st.session_state.character}, {st.session_state.character_description}. Give long responses that display your personality."}
        ]
        st.session_state.show_character_inputs = False
        st.experimental_rerun()

# Handle user input
def on_input_submit():
    user_input = st.session_state.user_input
    if user_input:
        assistant_response = generate_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.session_state.user_input = ""

# Generate AI response
def generate_response(user_input):
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        max_tokens=300,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

# User input box
st.text_input("Ask away:", key="user_input", on_change=on_input_submit)

# Display latest response
if len(st.session_state.messages) > 1:
    latest_response = st.session_state.messages[-1]['content']
    st.write("### Latest Response")
    st.write(f"**{st.session_state.character}:** {latest_response}")

# Display conversation history
st.write("### Conversation History")
for message in reversed(st.session_state.messages[:-1]):
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    elif message["role"] == "assistant":
        st.write(f"**{st.session_state.character}:** {message['content']}")