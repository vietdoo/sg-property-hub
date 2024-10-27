import os

ROTATING_PROXY_ENDPOINT = os.environ.get('ROTATING_PROXY_ENDPOINT')

PROXY = {
    "http": ROTATING_PROXY_ENDPOINT,
    "https": ROTATING_PROXY_ENDPOINT
}

MAX_RETRIES = 3
TIME_OUT_NO_PROXY = 8
TIME_OUT_PROXY = 20