import base64
import os
import re
from io import BytesIO
from pathlib import Path

import loguru
import requests
from litellm import completion
from PIL import Image as PILImage
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = loguru.logger


class Settings(BaseSettings):
    """environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "1234")


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


if __name__ == "__main__":
    settings = Settings(_env_file=".env", _env_file_encoding="utf-8")

    url = str(input("Enter image URL: "))
    query = str(input("Enter query: "))
    model = str(input("Enter model: "))

    image = Image(file_name="mustang.jpg", url=url)
    logger.info(f"Downloading image from {image.url}...")
    image.url_to_b64()

    logger.info(f"User: {query}")

    response = completion(
        model=f"openai/{model}",
        api_key=settings.GITHUB_TOKEN,
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
