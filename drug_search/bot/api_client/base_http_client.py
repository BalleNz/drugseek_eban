import enum
import json
import logging
from datetime import datetime
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
            self._session = aiohttp.ClientSession(
                base_url=self.base_url,
            )

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
            request_body: Optional[Union[dict, BaseModel]] = None,
            **kwargs
    ) -> Union[T, dict, list, None]:
        await self._ensure_session()

        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"

        headers["Content-Type"] = "application/json"

        json_data = None
        if request_body is not None:
            if isinstance(request_body, BaseModel):
                # Преобразуем Pydantic модель в словарь и сериализуем
                json_data = json.dumps(request_body.model_dump(), default=self._json_serializer)
            else:
                # Сериализуем обычный словарь
                json_data = json.dumps(request_body, default=self._json_serializer)

        try:
            async with self._session.request(
                    method=method.value,
                    url=endpoint,
                    headers=headers,
                    data=json_data,
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

    def _json_serializer(self, obj):
        """Кастомный сериализатор для обработки datetime"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
