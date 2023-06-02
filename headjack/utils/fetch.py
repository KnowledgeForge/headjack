from typing import Optional

import aiohttp

SOURCE_PATCH = {}


async def fetch(url: str, verb: str, json_data: Optional[dict] = None, return_json: bool = False):
    if verb not in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
        raise ValueError(f"Invalid HTTP verb: {verb}")

    async with aiohttp.ClientSession() as session:
        if verb == "GET":
            async with session.get(url) as response:
                if return_json:
                    return await response.json()
                else:
                    return await response.text()
        elif verb == "POST":
            async with session.post(url, json=json_data) as response:
                if return_json:
                    return await response.json()
                else:
                    return await response.text()
        elif verb == "PUT":
            async with session.put(url, json=json_data) as response:
                if return_json:
                    return await response.json()
                else:
                    return await response.text()
