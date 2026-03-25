from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    model_name: str = os.getenv("MODEL_NAME")
    temperature: float = float(os.getenv("TEMPERATURE"))

settings = Settings()

