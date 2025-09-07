import enum
import logging
from typing import Type, TypeVar, Optional, Union

import aiohttp
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class HTTPMethod(enum.Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class BaseHttpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self._session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession(base_url=self.base_url)

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None

    async def _request(
            self,
            method: HTTPMethod,
            endpoint: str,
            response_model: Optional[Type[T]] = None,
            access_token: Optional[str] = None,
            **kwargs
    ) -> Union[T, dict, list, None]:
        await self._ensure_session()

        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        headers["Content-Type"] = "application/json"

        try:
            async with self._session.request(
                    method=method.value,
                    url=endpoint,
                    headers=headers,
                    **kwargs
            ) as response:
                response.raise_for_status()

                if response.status == 204:  # No Content
                    return None

                data = await response.json()

                if response_model:
                    return response_model.model_validate(data)
                return data

        except aiohttp.ClientError as e:
            logging.error(f"Request failed: {e}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            raise
