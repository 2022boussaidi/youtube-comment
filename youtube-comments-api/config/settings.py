import os
from dotenv import load_dotenv

env_path = '.env'   # when u run a node app where the .env file is not in the same relative location as the file u are running then u need to specify the correct path for the .env file. Example if i have app.js and .env file both inside the same project folder location then when I'll do node app.js, then just dotenv.config() will work fine as its default path is
load_dotenv(dotenv_path=env_path)

class Config:
    API_KEY = os.getenv("API_KEY")
    MAX_ITERATIONS = 10
    REQUEST_DELAY = 2
    ERROR_DELAY = 10

__all__ = ['Config']