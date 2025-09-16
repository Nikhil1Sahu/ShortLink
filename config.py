import os
from typing import List

API_ID = os.environ.get("API_ID", "18466881")
API_HASH = os.environ.get("API_HASH", "8c8ca14ad8e416ce4e6ea717db7ec6af")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7866010374:AAGicQKgFVHJoA8ZSNtI9tYnB4KDzKm-R34")

ADMIN = int(os.environ.get("ADMIN", "5565120414"))
PICS = (os.environ.get("PICS", "https://envs.sh/uCZ.jpeg https://envs.sh/uCL.jpeg https://envs.sh/uC5.jpeg")).split()

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002731391701"))

DB_URI = os.environ.get("DB_URI", "mongodb+srv://nikhilsahu7j:dTQKfvo0jABOYKOu@cluster0.n2csgvi.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DB_NAME = os.environ.get("DB_NAME", "Cluster0")

IS_FSUB = os.environ.get("IS_FSUB", "False").lower() == "true"  # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002807337111").split())) # Add Multiple channel ids

# ------------------ NEW DEFAULT THUMBNAIL ------------------ #
# Global fallback thumbnail (used if user has not set one)
DEFAULT_THUMB = os.environ.get(
    "DEFAULT_THUMB",
    "https://envs.sh/ZwU.png"  # 👈 put your default thumbnail URL here
)
