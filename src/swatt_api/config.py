# The single source of truth of reading value from env memory block.
# Please use uv run --with-file .env to bring .env file values to env memory block.
# This project does not have dotenv.
from os import getenv

# TODO: Raise when value is not valid.
postgresql_url = getenv("POSTGRESQL_URL")
