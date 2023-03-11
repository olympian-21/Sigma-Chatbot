"""
official open-ai module to make api calls
"""
import base64
from io import BytesIO

import openai
import speech_recognition as s_r
import streamlit as st
from gtts import gTTS
from streamlit_chat import message

openai.api_key = st.secrets["openai-api-key"]

# Storing the chat
if "user" not in st.session_state:
    st.session_state.user = []

if "bot" not in st.session_state:
    st.session_state.bot = []

if "audio_recorded" not in st.session_state:
    st.session_state.audio_recorded = False

if "text_received" not in st.session_state:
    st.session_state.text_received = False


@st.cache
def generate_response(prompt: str = "I have no question", creativity: float = 5):
    """
    Args:
        prompt (str): user input prompt

    Returns:
        str: response of chatgpt
    """
    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=creativity / 10,
    )
    return completions.choices[0].text


def get_text():
    """
    Returns:
        str: user input text
    """
    st.session_state.text_received = True
    return st.text_input("You: ", "Hello, how are you?", key="input")


def get_speech():
    """
    Returns:
        str: user input text
    """
    # st.write()
    r = s_r.Recognizer()
    mics = s_r.Microphone.list_microphone_names()
    choice = st.selectbox("Select the microphone", ["None"] + mics)
    if choice != "None":
        device_index = mics.index(choice)
        my_mic = s_r.Microphone(
            device_index=device_index
        )  # my device index is 1, you have to put your device index
        speak = st.button("Speak")
        user_input = ""
        if speak:
            with my_mic as source:
                st.write("Say now!!!!")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)  # take voice input from the microphone
                user_input = r.recognize_google(audio)
                st.write(user_input)
                st.session_state.audio_recorded = True
        return user_input


def add_bg_from_local(background_file, sidebar_background_file):
    with open(background_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    with open(sidebar_background_file, "rb") as image_file:
        sidebar_encoded_string = base64.b64encode(image_file.read())

    page = f"""<style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string.decode()});
            background-size: cover;
        }}

        section[data-testid="stSidebar"] div[class="css-6qob1r e1fqkh3o3"] {{
            background-image: url(data:image/png;base64,{sidebar_encoded_string.decode()});
            background-size: 400px 800px;
        }}

    </style>"""

    st.markdown(page, unsafe_allow_html=True)


def main():
    st.set_page_config(
        page_title="🤖 ChatBot",
        page_icon="🤖",
        # layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": "https://github.com/olympian-21",
            "Report a bug": None,
            "About": "This is a chat bot for university students",
        },
    )

    add_bg_from_local("data/main.png", "data/sidebar.png")

    st.sidebar.markdown(
        "<center><h3>Configurations for ChatBot</h3></center> <br> <br>",
        unsafe_allow_html=True,
    )
    creativity = st.sidebar.slider(
        "How much creativity do you want in your chatbot?",
        min_value=0,
        max_value=10,
        value=5,
        help="10 is maximum creativity and 0 is no creativity.",
    )
    st.sidebar.markdown("<br> " * 15, unsafe_allow_html=True)
    st.sidebar.write("Developed by Hüseyin Pekkan Ata Turhan")

    st.markdown(
        "<center><h1>Sigma ChatBot</h1></center> <br> <br>", unsafe_allow_html=True
    )
    user_input = ""

    chosen_way = st.radio("How do you want to ask the questions?", ("Text", "Speech"))
    if chosen_way == "Text":
        user_input = get_text()
    elif chosen_way == "Speech":
        user_input = get_speech()

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col5:
        answer = st.button("Answer")
    try:
        if answer and (st.session_state.text_received or st.session_state.audio_recorded):
            st.session_state.text_received, st.session_state.audio_recorded = False, False
            output = generate_response(user_input, creativity)
            # store the output
            st.session_state.user.append(user_input)
            st.session_state.bot.append(output)

        sound_file = BytesIO()
        if st.session_state["bot"]:
            st.markdown("<br><br>", unsafe_allow_html=True)
            for i in range(len(st.session_state["bot"])):
                message(st.session_state["user"][i], is_user=True, key=f"{str(i)}_user")
                message(st.session_state["bot"][i], key=str(i))
                tts = gTTS(st.session_state["bot"][i], lang="en")
                tts.write_to_fp(sound_file)
                st.audio(sound_file)
    except Exception as e:
        st.write("An error occurred: " + type(e).__name__)
        st.write("\nPleae wait while we are solving the problem. Thank you ;]")


if __name__ == "__main__":
    main()
