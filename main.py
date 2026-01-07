"""
Główny punkt wejścia aplikacji - Single Responsibility Principle
"""
from bot.discord_bot import DiscordBot
from utils.logger import log_bot_start


def main():
    """Główna funkcja uruchamiająca aplikację"""
    # Inicjalizacja logowania
    log_bot_start()

    # Utwórz i uruchom bota
    bot = DiscordBot()
    bot.run_bot()


if __name__ == "__main__":
    main()