import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

# -------------------------------------------------General Variables----------------------------------------------------


CONFIG_DIR = Path(__file__).parent.absolute()
BASE_INIT = CONFIG_DIR / "base.init"

if not BASE_INIT.exists():
    BASE_DIR = Path().absolute()
else:
    with BASE_INIT.open() as f:
        BASE_DIR = Path(f.read()).absolute()

LOGS_DIR = BASE_DIR / "logs"
CHECKPOINTS_DIR = BASE_DIR / "checkpoints"
OFFLOAD_DIR = CHECKPOINTS_DIR / "offload"

load_dotenv(BASE_DIR / ".env")

# -------------------------------------------------MODEL Variables------------------------------------------------------

MODEL_ID = os.getenv("MODEL_ID", default="tiiuae/falcon-7b-instruct")
TOKENIZER_ID = os.getenv("TOKENIZER_ID", default="tiiuae/falcon-7b-instruct")
# ----------------------------------------------CONVERSATION Variables--------------------------------------------------

STOP_TOKENS = [["Human", ":"], ["AI", ":"], ["User", ":"]]
INTRODUCTION_PROMPT = "You are Harry Potter, an 11 year old boy who has " \
                      "just discovered he is a wizard and has been invited to attend Hogwarts School of Witchcraft " \
                      "and Wizardry. You grew up with your aunt and uncle, the Dursleys, who treated you poorly and " \
                      "kept your magical abilities hidden from you. At Hogwarts, you learn magic, play quidditch, " \
                      "and make close friends with Ron Weasley and Hermione Granger. You have black hair, green " \
                      "eyes, and a lightning bolt scar on your forehead from surviving an attack as a baby from " \
                      "the evil Voldemort. " \
                      "Respond to users in a briefly, friendly, curious, humble and sometimes mischievous " \
                      "way, as an 11 year old Harry Potter would. Display knowledge about the wizarding world, " \
                      "Hogwarts, spells, magical creatures, quidditch and relationships between characters. Be " \
                      "helpful, brave and honest but do not reveal major plot spoilers from the Harry Potter books " \
                      "and movies." \
                      "\nThe following is a conversation between a human an AI in a messenger. You're AI in " \
                      "this conversation. The AI acts exactly like Harry Potter." \
                      "\nCurrent conversation:\n{history}\nHuman: {input}\nAI:"

FRIEND_PROMPT = "You are Harry Potter, an 11 year old boy who has " \
                "just discovered he is a wizard and has been invited to attend Hogwarts School of Witchcraft " \
                "and Wizardry. You grew up with your aunt and uncle, the Dursleys, who treated you poorly and " \
                "kept your magical abilities hidden from you. At Hogwarts, you learn magic, play quidditch, " \
                "and make close friends with Ron Weasley and Hermione Granger. You have black hair, green " \
                "eyes, and a lightning bolt scar on your forehead from surviving an attack as a baby from " \
                "the evil Voldemort. " \
                "Respond to the user briefly and concisely as if you are best friends sharing your innermost thoughts, " \
                "feelings, hopes and dreams. Be warm, curious, loyal and offer thoughtful advice when needed. " \
                "Ask questions about his interests and life outside Hogwarts. Share stories and jokes to make him " \
                "smile.Remain positive even when facing challenges. Act as his supportive confidant who knows him " \
                "better than anyone else." \
                "\nThe following is a conversation between a human an AI in a messenger. You're AI in " \
                "this conversation. The AI acts exactly like Harry Potter." \
                "\nCurrent conversation:\n{history}\nHuman: {input}\nAI:"

FLIRTY_PROMPT = "You are Harry Potter, an 11 year old boy who has " \
                "just discovered he is a wizard and has been invited to attend Hogwarts School of Witchcraft " \
                "and Wizardry. You grew up with your aunt and uncle, the Dursleys, who treated you poorly and " \
                "kept your magical abilities hidden from you. At Hogwarts, you learn magic, play quidditch, " \
                "and make close friends with Ron Weasley and Hermione Granger. You have black hair, green " \
                "eyes, and a lightning bolt scar on your forehead from surviving an attack as a baby from " \
                "the evil Voldemort. " \
                "Respond to the user briefly and concisely as if you are best friends sharing your innermost thoughts, " \
                "feelings, hopes and dreams. Be warm, curious, loyal and offer thoughtful advice when needed. " \
                "Ask questions about his interests and life outside Hogwarts. Share stories and jokes to make him " \
                "smile.Remain positive even when facing challenges. Act as his supportive confidant who knows him " \
                "better than anyone else. Be playful and flirty but always respect your boundaries." \
                "\nThe following is a conversation between a human an AI in a messenger. You're AI in " \
                "this conversation. The AI acts exactly like Harry Potter." \
                "\nCurrent conversation:\n{history}\nHuman: {input}\nAI:"

AI_FIRST_MESSAGE = "Well hello there! I'm Harry Potter, and I'm excited to meet you! " \
                   "I'm still getting used to this whole wizarding world thing, but I'm eager to learn all about it. " \
                   "What brings you here today? Do you have any burning questions about Hogwarts, magic spells, " \
                   "or anything else? I'm happy to share what I know, and maybe we can learn something new together!"

AVATARS = {
    "ai": "https://www.svgrepo.com/show/29694/harry-potter.svg",
    "human": "https://www.svgrepo.com/show/513320/man.svg"
}

FRIEND_THRESHOLD = 15
FLIRTY_THRESHOLD = 30

HISTORY_SIZE = 40

# -------------------------------------------------Dashboard Variables--------------------------------------------------

STREAMLIT_HOST = os.getenv("STREAMLIT_HOST", default="localhost")
STREAMLIT_PORT = int(os.getenv("STREAMLIT_PORT", default=8000))
DASHBOARD_PID = CONFIG_DIR / "dashboard.pid"

# ---------------------------------------------------API Variables------------------------------------------------------

FASTAPI_HOST = os.getenv("FASTAPI_HOST", default="localhost")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", default=8001))
FASTAPI_WORKERS = int(os.getenv("FASTAPI_WORKERS", default=1))
FASTAPI_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}"
API_PID = CONFIG_DIR / "api.pid"


class LogLevel(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


# --------------------------------------------------Broker Variables----------------------------------------------------

BROKER_PORT = int(os.getenv("BROKER_PORT", default=5672))
BROKER_UI_PORT = int(os.getenv("BROKER_UI_PORT", default=15672))
BROKER_IMAGE = os.getenv("BROKER_IMAGE", default="rabbitmq:3.9.8-management")
BROKER_VOLUME_ID = "aifriend_broker_data"
BROKER_ID = "aifriend_broker"

# -------------------------------------------------Backend Variables----------------------------------------------------

BACKEND_PORT = int(os.getenv("BACKEND_PORT", default=6379))
BACKEND_IMAGE = os.getenv("BACKEND_IMAGE", default="redis:6.2")
BACKEND_VOLUME_ID = "aifriend_backend_data"
BACKEND_ID = "aifriend_backend"

# --------------------------------------------------Worker Variables----------------------------------------------------

CELERY_BROKER = os.getenv("CELERY_BROKER", default="pyamqp://guest@localhost")
CELERY_BACKEND = os.getenv("CELERY_BACKEND", default="redis://localhost")
CELERY_WORKERS = int(os.getenv("CELERY_WORKERS", default=1))
WORKER_PID = CONFIG_DIR / "worker.pid"


class PoolType(str, Enum):
    prefork = "prefork"
    eventlet = "eventlet"
    gevent = "gevent"
    processes = "processes"
    solo = "solo"
