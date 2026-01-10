from bot.discord_bot import DiscordBot
from utils.logger import setup_logging, log_info


def main():
    # Inicjalizacja logowania
    setup_logging()

    # Logi startu
    log_info('main', "Discord Channel Cleaner - Uruchamianie")

    # Utwórz i uruchom bota
    bot = DiscordBot()
    bot.run_bot()


if __name__ == "__main__":
    main()