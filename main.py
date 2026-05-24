from bot.client import VCTBot
from bot.config import load_settings


def main() -> None:
    settings = load_settings()
    bot = VCTBot(settings)
    bot.run(settings.discord_token)


if __name__ == "__main__":
    main()
