import os

from dotenv import load_dotenv

# Ładuje zmienne środowiskowe z pliku .env
load_dotenv()


class EnvTokenManager:

    def __init__(self, env_name: str = "DISCORD_BOT_TOKEN"):
        self.env_name = env_name

    def load_token(self) -> str:
        token = os.getenv(self.env_name)

        if not token:
            return ""

        return token.strip()

    def has_token(self) -> bool:
        token = self.load_token()
        return bool(token and token.strip())


# Dla kompatybilności wstecznej
TokenManager = EnvTokenManager
