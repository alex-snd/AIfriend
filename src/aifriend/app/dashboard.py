import time
from http import HTTPStatus

import requests
import streamlit as st
from requests.exceptions import ConnectionError

from aifriend.config import var


def main() -> None:
    st.set_page_config(
        page_title="AIfriend",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded")

    st.session_state.setdefault("history", [{'type': 'ai',
                                             'data': {
                                                 'content': var.AI_FIRST_MESSAGE,
                                                 'additional_kwargs': {},
                                                 'example': False}}, ])
    st.session_state.setdefault("first_launch_time", time.monotonic())
    st.session_state.setdefault("seen_message", "")
    st.session_state.setdefault("unseen_messages", [])
    st.session_state.setdefault("task_id", None)

    sidebar()


def sidebar() -> None:
    st.sidebar.markdown(body=
                        """
                        <h1 align="center">
                            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Harry_Potter_wordmark.svg/2180px-Harry_Potter_wordmark.svg.png" width=80%;>
                        </h1>
                        <br>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Job title:</font> <font size="+4">Chief Wizarding Officer (CWO)</font>
                        </p>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Bio:</font> <font size="+4">Greetings, Muggle! I'm Harry Botter, your friendly neighborhood chatbot and Chief 
                        Wizarding Officer. I may be a bot, but I'm also a wizard-in-training, so you can count on me to 
                        bring some magic to your day! Whether you need help with a tricky problem or just want to chat 
                        about the wizarding world, I'm here to make your day more enchanting. So don't be shy – give me 
                        a hoot and let's get chatting!</font>
                        </p>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Interests:</font><br><font size="+4">quidditch, Hogwarts, magical creatures, wizarding world, wizarding history</font>
                        </p>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Skills:</font><br><font size="+4">spells, potions, trivia, conversation, humor</font>
                        </p>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Catchphrase:</font><br><font size="+4">'Wingardium Leviosa! Let's levitate some boredom and have a magical chat!'</font>
                        </p>
                        """,
                        unsafe_allow_html=True)

    st.sidebar.markdown(body=
                        """
                        <p align="center">
                        <font size="+4" color="#45B39D">Favorite track:</font>
                        </p>
                        """,
                        unsafe_allow_html=True)
    st.sidebar.audio("https://github.com/alex-snd/aifriend/blob/assets/sound.mp3?raw=true",
                     format="audio/wav", start_time=0)

    chat_page()


def chat_page() -> None:
    human_message = st.chat_input("Message")

    # Display chat history
    if (gap := int(time.monotonic() - st.session_state.first_launch_time)) < 10 \
            and st.session_state.history \
            and st.session_state.history[0]["type"] == "ai":

        with st.chat_message(name="ai", avatar=var.AVATARS["ai"]).empty():
            for i in range(10 - gap):
                st.write(f"Typing{'.' * (i % 4)}")
                time.sleep(0.75)

            st.write(var.AI_FIRST_MESSAGE)

        for message_entity in st.session_state.history[1:]:
            with st.chat_message(name=message_entity["type"], avatar=var.AVATARS[message_entity["type"]]):
                st.write(message_entity["data"]["content"])

    else:
        for message_entity in st.session_state.history:
            with st.chat_message(name=message_entity["type"], avatar=var.AVATARS[message_entity["type"]]):
                st.write(message_entity["data"]["content"])

    if st.session_state.seen_message:
        with st.chat_message(name="human", avatar=var.AVATARS["human"]):
            st.write(st.session_state.seen_message)

    for message in st.session_state.unseen_messages:
        with st.chat_message(name="human", avatar=var.AVATARS["human"]):
            st.write(message)

    # New message processing
    if human_message and human_message.strip():
        with st.chat_message(name="human", avatar=var.AVATARS["human"]):
            st.write(human_message)

        with st.chat_message(name="ai", avatar=var.AVATARS["ai"]).empty():
            ai_message = send(human_message)
            st.write(ai_message)

    if st.session_state.unseen_messages:
        with st.chat_message(name="ai", avatar=var.AVATARS["ai"]).empty():
            ai_message = send("\n".join(st.session_state.unseen_messages))
            st.write(ai_message)


def send(human_message: str) -> str:
    try:
        payload = {
            'message': human_message,
            'history': st.session_state.history,
        }

        if not st.session_state.task_id:
            task_info = requests.post(url=f"{var.FASTAPI_URL}/talk", json=payload)
            task_info = task_info.json()

            if not task_info.get("task_id"):
                st.error(task_info)
                st.stop()

            st.session_state.task_id = task_info["task_id"]
            st.session_state.seen_message = human_message
            st.session_state.unseen_messages = []  # TODO
        else:
            st.session_state.unseen_messages.append(human_message)

        status = requests.get(url=f"{var.FASTAPI_URL}/status/{st.session_state.task_id}")
        status = status.json()

        while status['status_code'] == HTTPStatus.PROCESSING and status['state'] != 'PREDICT':
            if status['state'] == 'LOADING':
                st.info('Wait a moment: Harry will wake up soon')
                time.sleep(0.3)
            elif status['state'] == 'PENDING':
                st.info('Wait a moment: Harry is busy right now')
                time.sleep(1)
            else:
                time.sleep(0.1)

            status = requests.get(url=f'{var.FASTAPI_URL}/status/{st.session_state.task_id}')
            status = status.json()

        while status["status_code"] == HTTPStatus.PROCESSING:
            st.write(f"Typing{'.' * int(time.time() % 4)}")
            time.sleep(0.2)

            status = requests.get(url=f"{var.FASTAPI_URL}/status/{st.session_state.task_id}")
            status = status.json()

        requests.delete(url=f"{var.FASTAPI_URL}/{st.session_state.task_id}")

        if status["status_code"] != HTTPStatus.OK:
            st.error(status["message"])
            st.stop()

        st.session_state.task_id = None
        st.session_state.seen_message = None
        st.session_state.history = status["history"]

        return status["message"]

    except ConnectionError:
        st.error(f"It seems that the API service is not running.\n\n"
                 f"Failed to establish a {var.FASTAPI_URL} connection.")
        st.stop()


if __name__ == "__main__":
    main()
