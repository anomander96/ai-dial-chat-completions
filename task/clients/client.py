from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        self.client = Dial(api_key=self._api_key, base_url=DIAL_ENDPOINT)
        self.async_client = AsyncDial(api_key=self._api_key, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[Message]) -> Message:
        completion = self.client.chat.completions.create(
            deployment_name = self._deployment_name,
            stream = False,
            messages = [m.to_dict() for m in messages]
        )

        if not completion.choices:
            raise Exception("No choices in response found")
        content = completion.choices[0].message.content
        print(content)
        return Message(role = Role.AI, content = content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        chunks = await self.async_client.chat.completions.create(
            deployment_name = self._deployment_name,
            stream = True,
            messages = [m.to_dict() for m in messages]
        )

        contents = []
        async for chunk in chunks:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end = "", flush = True)
                contents.append(content)
        print()
        return Message(role = Role.AI, content = "".join(contents))
