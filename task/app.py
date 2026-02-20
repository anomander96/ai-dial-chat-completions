import asyncio

from task.clients.client import DialClient
from task.clients.custom_client import CustomDialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    client = CustomDialClient(deployment_name="gpt-4o")

    conversation = Conversation()

    print("Provide System prompt or press 'enter' to continue.")
    system_prompt = input("> ").strip()
    if not system_prompt:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))

    print("\nType your question or 'exit' to quit.")
    while True:
        user_input = input("> ").strip()

        if user_input.lower() == "exit":
            print("Exiting the chat. Goodbye!")
            break

        conversation.add_message(Message(role=Role.USER, content=user_input))


        print("AI: ", end="", flush=True)
        if stream:
            response_message = await client.stream_completion(conversation.messages)
        else:
            response_message = client.get_completion(conversation.messages)

        conversation.add_message(response_message)
        print()


asyncio.run(start(True))