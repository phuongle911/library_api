import os

INTERNAL_API_TOKEN = os.getenv(
    "INTERNAL_API_TOKEN",
    "dev-internal-token",
)

def get_internal_headers():
    return {
        "X-Internal-Token": INTERNAL_API_TOKEN,
    }
