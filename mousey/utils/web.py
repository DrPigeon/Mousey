# -*- coding: utf-8 -*-
import aiohttp

from config import PASTEE_TOKEN
from mousey.const import USER_AGENT


PASTE_ENDPOINT = 'https://api.paste.ee/v1/pastes'


async def get_json(url, *, session=None, headers=None, **kwargs):
    """
    Download the json body from a specified url.

    Parameters
    ----------
    url : str
        The url to download the json from
    headers : dict
        The request headers to use. Note that the User-Agent is pre set and will be overwritten.
    session : Optional[aiohttp.ClientSession]
        The session to use for the request

    All kwargs which can be passed to a GET request using aiohttp can be used here.

    Returns
    -------
    dict
        The json body parsed as a dict
    """
    session = session or aiohttp.ClientSession()
    headers = headers or {}

    headers.update({'User-Agent': USER_AGENT})

    async with session.get(url, headers=headers, **kwargs) as resp:
        # ignoring content type as Mousey does a request which returns the wrong content type
        return await resp.json(content_type=None)


async def haste(content: str, *, session=None):
    """
    Creates a haste and returns the link to it.

    Parameters
    ----------
    content : str
        The content which gets put into the haste
    session : Optional[aiohttp.ClientSession]
        The session to use for the request

    Returns
    -------
    str
        The url to the haste
    """
    session = session or aiohttp.ClientSession()
    headers = {'User-Agent': USER_AGENT, 'X-Auth-Token': PASTEE_TOKEN}

    payload = {"sections": [{"name": "Mousey Haste", "contents": content}]}

    async with session.post(PASTE_ENDPOINT, headers=headers, json=payload) as resp:
        res = await resp.json()

    return res.get('link')
