from src.core.gcp.pubsub.listener import run_pubsub_subscriber
from src.core.logger.base import setup_logging


def main():
    setup_logging()
    run_pubsub_subscriber()


if __name__ == "__main__":
    main()
