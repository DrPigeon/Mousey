# -*- coding: utf-8 -*-
import aiohttp

from mousey.const import USER_AGENT


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
