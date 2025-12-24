"""
Główny punkt wejścia aplikacji
"""
from bot.discord_bot import DiscordBot


def main():
    """Główna funkcja uruchamiająca aplikację"""
    # Utwórz i uruchom bota
    bot = DiscordBot()
    bot.run_bot()


if __name__ == "__main__":
    main()
