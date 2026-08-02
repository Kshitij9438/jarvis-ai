import os
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    """
    Central configuration for JARVIS.

    Values are read from the environment with safe defaults so the
    application can start even when no .env file exists.
    """

    model_name: str = Field(
        default=os.getenv("MODEL_NAME", "phi3")
    )

    temperature: float = Field(
        default=0.3
    )

    @classmethod
    def from_env(cls):
        temperature = os.getenv("TEMPERATURE")

        if temperature is None:
            parsed_temperature = 0.3
        else:
            try:
                parsed_temperature = float(temperature)
            except ValueError as e:
                raise ValueError(
                    "TEMPERATURE must be a valid floating point number."
                ) from e

        return cls(
            model_name=os.getenv("MODEL_NAME", "phi3"),
            temperature=parsed_temperature,
        )


settings = Settings.from_env()