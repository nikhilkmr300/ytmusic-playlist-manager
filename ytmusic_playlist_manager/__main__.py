import logging

from .authorization import retrieve_credentials, find_client_secrets_file

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    credentials = retrieve_credentials(find_client_secrets_file())

    print(credentials.to_json())
