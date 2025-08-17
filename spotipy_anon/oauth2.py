# -*- coding: utf-8 -*-

__all__ = ["SpotifyAnon"]

import hashlib
import hmac
import logging
import time
import warnings

import requests

from spotipy.cache_handler import MemoryCacheHandler, CacheHandler
from spotipy.oauth2 import SpotifyAuthBase

logger = logging.getLogger(__name__)


def hmac_function(algorithm, key, data):
    if algorithm == 'sha1':
        return hmac.new(key, data, hashlib.sha1).digest()
    elif algorithm == 'sha256':
        return hmac.new(key, data, hashlib.sha256).digest()
    elif algorithm == 'sha512':
        return hmac.new(key, data, hashlib.sha512).digest()
    else:
        raise ValueError('Unsupported algorithm')


def counter_to_bytes(counter):
    result = bytearray(8)
    for i in range(7, -1, -1):
        result[i] = counter & 0xff
        counter >>= 8
    return bytes(result)


def generate(secret, algorithm='sha1', digits=6, counter=0):
    hmac_result = hmac_function(algorithm, secret, counter_to_bytes(counter))
    offset = hmac_result[-1] & 0xf
    binary = ((hmac_result[offset] & 0x7f) << 24 |
              (hmac_result[offset + 1] & 0xff) << 16 |
              (hmac_result[offset + 2] & 0xff) << 8 |
              (hmac_result[offset + 3] & 0xff))

    otp = binary % (10 ** digits)
    return str(otp).zfill(digits)

def get_secret(inp):
    secret = []
    for index, item in enumerate(inp):
        secret.append(str(item ^ ((index % 33) + 9)))
    return [ord(item) for item in str("".join(secret))]


def get_totp(session: requests.Session):
    resp = session.get("https://github.com/Thereallo1026/spotify-secrets/blob/main/secrets/secretDict.json?raw=true")
    resp.raise_for_status()
    secrets = resp.json()
    version = max(secrets, key=int)
    secret_bytes = secrets[version]
    return generate(bytearray(get_secret(secret_bytes)), counter=int(time.time()) // 30)


class SpotifyAnon(SpotifyAuthBase):
    """
    Implements anonymous access to the Spotify API.
    """
    client_id: str  # was suggested by PyCharm

    TOKEN_URL = "https://open.spotify.com/api/token"

    def __init__(
            self,
            proxies=None,
            requests_session=True,
            requests_timeout=None,
            cache_handler=None
    ):
        """
        Creates a SpotifyAnon object

        Parameters:
        * proxies: Optional, interpreted as boolean
        * requests_session: A Requests session
        * requests_timeout: Optional, tell Requests to stop waiting for a response after
                            a given number of seconds
        * cache_handler: An instance of the `CacheHandler` class to handle
                         getting and saving cached authorization tokens.
                         Optional, will otherwise use `CacheFileHandler`.
                         (takes precedence over `cache_path` and `username`)
        """

        super(SpotifyAnon, self).__init__(requests_session)

        self.proxies = proxies
        self.requests_session = requests_session
        self.requests_timeout = requests_timeout
        self.cache_handler = cache_handler

        if cache_handler:
            assert issubclass(cache_handler.__class__, CacheHandler), \
                "cache_handler must be a subclass of CacheHandler: " + str(type(cache_handler)) \
                + " != " + str(CacheHandler)
            self.cache_handler = cache_handler
        else:
            self.cache_handler = MemoryCacheHandler()

    def get_access_token(self, as_dict=False, check_cache=True):
        """
        If a valid access token is in memory, returns it
        Else fetches a new token and returns it
            Parameters:
            - as_dict - a boolean indicating if returning the access token
                as a token_info dictionary, otherwise it will be returned
                as a string.
        """
        if as_dict:
            warnings.warn(
                "You're using 'as_dict = True'."
                "get_access_token will return the token string directly in future "
                "versions. Please adjust your code accordingly, or use "
                "get_cached_token instead.",
                DeprecationWarning,
                stacklevel=2,
            )

        if check_cache:
            token_info = self.cache_handler.get_cached_token()
            if token_info and not self.is_token_expired(token_info):
                return token_info if as_dict else token_info["access_token"]

        token_info = self._request_access_token()
        self.cache_handler.save_token_to_cache(token_info)
        self.client_id = token_info["client_id"]
        return token_info if as_dict else token_info["access_token"]

    def _request_access_token(self):
        """Gets client credentials access token """
        logger.debug("sending GET request to %s", self.TOKEN_URL)

        totp = get_totp(self._session)

        try:
            response = self._session.get(
                self.TOKEN_URL,
                params={
                    "productType": "web-player",
                    "totp": totp,
                    "totpVer": 5
                },
                verify=True,
                proxies=self.proxies,
                timeout=self.requests_timeout,
            )
            response.raise_for_status()
            token_info = response.json()
            return {"client_id": token_info["clientId"],
                    "access_token": token_info["accessToken"],
                    "expires_at": int(token_info["accessTokenExpirationTimestampMs"] / 1000)
                    }
        except requests.exceptions.HTTPError as http_error:
            self._handle_oauth_error(http_error)