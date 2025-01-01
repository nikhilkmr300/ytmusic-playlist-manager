import logging
import os
from glob import glob
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

CACHE_DIR = Path.home() / ".ytmusic_playlist_manager"
CREDENTIALS_FILEPATH = CACHE_DIR / "credentials.json"
LOGGER = logging.getLogger(__name__)


def cache_credentials(credentials):
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    with open(CREDENTIALS_FILEPATH, "w") as f:
        f.write(f"{credentials.to_json()}\n")
    LOGGER.info(
        f"Cached credentials for account {credentials.account} to {CREDENTIALS_FILEPATH}."
    )


def clear_cached_credentials():
    if os.path.exists(CREDENTIALS_FILEPATH):
        os.remove(CREDENTIALS_FILEPATH)


def refresh_credentials(client_secrets_file):
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        scopes=["https://www.googleapis.com/auth/youtube.readonly"],
    )
    flow.run_local_server(
        host="localhost",
        port=8080,
        open_browser=True,
        prompt="consent",
        authorization_prompt_message="",
    )
    credentials = flow.credentials

    LOGGER.info(f"Retrieved new credentials.")

    cache_credentials(credentials)

    return credentials


def retrieve_credentials(client_secrets_file):
    credentials = None

    if os.path.exists(CREDENTIALS_FILEPATH):
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILEPATH)
        LOGGER.info(f"Found cached credentials.")

        if credentials.expired:
            LOGGER.info(f"Cached credentials are expired. Refreshing...")
            credentials = refresh_credentials(client_secrets_file)

    else:
        credentials = refresh_credentials(client_secrets_file)

    return credentials


def find_client_secrets_file():
    wildcard = "client_secret*.json"
    matches = glob(wildcard)

    if len(matches) < 1:
        raise FileNotFoundError(
            f'Could not find a client secrets file matching wildcard "{wildcard}".'
        )
    elif len(matches) > 1:
        matches.sort(key=os.path.getctime)
        LOGGER.warning(
            f'Found {len(matches)} client secrets files matching wildcard "{wildcard}". Defaulting to using "{matches[0]}", which was modified last.'
        )
        return matches[0]

    LOGGER.info(f'Using client secrets file "{matches[0]}."')

    return matches[0]
