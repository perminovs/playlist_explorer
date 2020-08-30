from pydantic import ValidationError

from deezer.auth import DeezerAuthenticator
from deezer.client import DeezerClient
from deezer.settings import DeezerSettings


def main():
    try:
        settings = DeezerSettings()
    except ValidationError:
        settings = DeezerSettings(_env_file='.env')

    deezer_auth = DeezerAuthenticator(settings)
    deezer_auth.ensure_auth()

    client = DeezerClient(settings=settings, authenticator=deezer_auth)
    client.get_playlist_info('_2019')


if __name__ == '__main__':
    main()
