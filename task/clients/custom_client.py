import json
import aiohttp
import requests

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class CustomDialClient(BaseClient):
    _endpoint: str

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"

    def get_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "messages": [msg.to_dict() for msg in messages]
        }

        print(f"REQUEST: {json.dumps(request_data, indent=2)}")

        response = requests.post(
            url=self._endpoint,
            headers=headers,
            json=request_data
        )

        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")

        data = response.json()
        print(f"RESPONSE: {json.dumps(data, indent=2)}")

        content = data["choices"][0]["message"]["content"]
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        headers = {
            "api-key": self._api_key,
            "Content-Type": "application/json"
        }
        request_data = {
            "stream": True,
            "messages": [msg.to_dict() for msg in messages]
        }

        print(f"REQUEST: {json.dumps(request_data, indent=2)}")

        contents = []
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._endpoint,
                json=request_data,
                headers=headers
            ) as response:
                async for line in response.content:
                    snippet = self._get_content_snippet(line)
                    if snippet is None:
                        continue
                    print(snippet, end="", flush=True)
                    contents.append(snippet)

        print()
        return Message(role=Role.AI, content="".join(contents))

    @staticmethod
    def _get_content_snippet(line: bytes) -> str | None:
        decoded = line.decode("utf-8").strip()
        if not decoded or not decoded.startswith("data: "):
            return None
        data_str = decoded[len("data: "):]
        if data_str == "[DONE]":
            return None
        chunk = json.loads(data_str)
        delta = chunk["choices"][0]["delta"]
        content = delta.get("content")
        return content if content else None