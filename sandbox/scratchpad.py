import base64
import json
import os
import re
from io import BytesIO
from pathlib import Path
from textwrap import dedent
from typing import Any

import loguru
import requests
from exa_py import Exa
from openai import OpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageToolCall
from PIL import Image as PILImage
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

logger = loguru.logger

console = Console()


class Settings(BaseSettings):
    """environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "1234")
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "1234")
    ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "1234")
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "1234")
    LANGCHAIN_API_KEY: str = os.environ.get("LANGCHAIN_API_KEY", "1234")
    LANGCHAIN_TRACING_V2: bool = os.environ.get("LANGCHAIN_TRACING_V2", False)
    TAVILY_API_KEY: str = os.environ.get("TAVILY_API_KEY", "1234")
    EXA_API_KEY: str = os.environ.get("EXA_API_KEY", "1234")
    XAI_API_KEY: str = os.environ.get("XAI_API_KEY", "1234")

    def get_exa_client(self, **kwargs) -> Exa:
        return Exa(api_key=self.EXA_API_KEY, **kwargs)

    def get_openai_client(self, **kwargs) -> OpenAI:
        return OpenAI(**kwargs)


class Image(BaseModel):
    folder_path: str | Path = Path("assets")
    file_name: str
    url: str | None = None
    b64_string: str | None = None

    @field_validator("folder_path", check_fields=False)
    @classmethod
    def validate_folder_path(cls, v):
        folder_path = Path(v) if isinstance(v, str) else v
        if not folder_path.exists():
            raise FileNotFoundError(f"Folder path does not exist: {folder_path}")
        return folder_path

    @field_validator("file_name")
    @classmethod
    def validate_file(cls, v):
        suffix = Path(v).suffix
        if suffix not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            raise ValueError("Invalid file format")
        return v

    @field_validator("url", check_fields=False)
    @classmethod
    def validate_image_url(cls, v):
        if not re.match(r"^https?://", v):
            raise ValueError("Invalid URL")
        return v

    def download(self) -> None:
        image_path = self.folder_path / self.file_name
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(image_path, "wb") as image_file:
                image_file.write(response.content)
        else:
            raise requests.HTTPError(f"Failed to download image from {self.url}")

    def image_to_b64(self) -> str:
        image_path = self.folder_path / self.file_name
        try:
            with open(image_path, "rb") as image_file:
                self.b64_string = base64.b64encode(image_file.read()).decode("utf-8")
                return self.b64_string
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Image file not found at {image_path} : {str(e)}")

    def url_to_b64(self) -> str:
        response = requests.get(self.url)
        if response.status_code == 200:
            self.b64_string = base64.b64encode(response.content).decode("utf-8")
            return self.b64_string
        else:
            raise requests.HTTPError(f"Failed to download image from {self.url}")

    def save_to_image(self) -> None:
        image_path = self.folder_path / self.file_name
        try:
            with open(image_path, "wb") as image_file:
                image_file.write(base64.b64decode(self.b64_string))
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Image file not found at {image_path} : {str(e)}")

    def display_image(self) -> None:
        if self.b64_string:
            image = PILImage.open(BytesIO(base64.b64decode(self.b64_string)))
            image.show()
        else:
            image = PILImage.open(self.folder_path / self.file_name)
            image.show()


def test_github_models(settings: Settings) -> None:
    url = str(input("Enter image URL: "))
    query = str(input("Enter query: "))
    model = str(input("Enter model: "))

    image = Image(file_name="mustang.jpg", url=url)
    logger.info(f"Downloading image from {image.url}...")
    image.url_to_b64()

    logger.info(f"User: {query}")

    client = settings.get_openai_client(
        api_key=settings.GITHUB_TOKEN,
        base_url="https://models.inference.ai.azure.com",
    )

    response: ChatCompletion = client.chat.completions.create(
        model=model,
        base_url="https://models.inference.ai.azure.com",
        stream=False,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image.b64_string}"
                        },
                    },
                ],
            }
        ],
    )
    logger.debug(response)
    logger.info(f"{response.model}: {response.choices[0].message.content}")


def test_xai_models(settings: Settings) -> ChatCompletion:
    exa = settings.get_exa_client()

    def exa_search(
        query: str,
    ) -> dict[str, Any]:
        return exa.search_and_contents(
            query=query, type="auto", highlights=True, num_results=3
        )

    def process_tools(
        tool_calls: list[ChatCompletionMessageToolCall], messages: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            args: dict = json.loads(tool_call.function.arguments)
            if function_name == "search_with_exa":
                search_results = exa_search(**args)

                logger.debug(f"Search results: {search_results}")

                messages.append(
                    {
                        "role": "tool",
                        "content": str(search_results),
                        "tool_call_id": tool_call.id,
                    }
                )
                console.print(
                    "[bold cyan]Context updated[/bold cyan] [i]with[/i] "
                    "[bold green]search_with_exa[/bold green]: ",
                    args.get("query"),
                    "\n",
                )

        return messages

    model = "grok-beta"

    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_with_exa",
                "description": "use an advanced search engine to find information via semantic search",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "the search query",
                            "example_value": "top o'reilly books about large language models",
                        },
                    },
                    "required": ["query"],
                    "optional": [],
                },
            },
        }
    ]

    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": dedent(
                        """
                        You are an advanced AI research assistant that is knowledgeable and very meticulous.
                        You have access to a variety of tools and resources to help you with your tasks.
                        Your goal is to provide the user with the information they are looking for by using
                        the search tool provided and provide recommendations based on the search results.
                        """
                    ),
                }
            ],
        },
    ]

    client = settings.get_openai_client(
        api_key=settings.XAI_API_KEY,
        base_url="https://api.x.ai/v1",
    )

    while True:
        try:
            query = Prompt.ask("[bold green]What do you want to know?[/bold green]")
            messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query,
                        }
                    ],
                }
            )
            response: ChatCompletion = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
                tool_choice="auto",
                tools=tools,
                user="user",
            )

            logger.debug(response)
            message = response.choices[0].message
            logger.debug(message)

            tool_calls = message.tool_calls
            if tool_calls:
                messages.append(message)
                messages = process_tools(tool_calls, messages)
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Answer my previous query based on the search results",
                            }
                        ],
                    }
                )
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=False,
                    tool_choice="auto",
                    tools=tools,
                    user="user",
                )
                console.print(Markdown(response.choices[0].message.content))
                console.print()
            else:
                console.print()
                console.print(f"{response.model.upper()}: {message.content}")
                console.print()

        except Exception as e:
            logger.error(e)
            break

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

    # test_github_models(settings)

    test_xai_models(settings)
