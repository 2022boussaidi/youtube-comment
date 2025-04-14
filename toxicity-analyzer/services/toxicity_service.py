from detoxify import Detoxify
import numpy as np
from utils.text_cleaner import clean_text
from config.settings import Config

class ToxicityService:
    def __init__(self):
        self.model = Detoxify(Config.DETOXIFY_MODEL)
    
    def analyze(self, text):
        result = self.model.predict(text)
        return {
            key: float(value) if isinstance(value, np.float32) else value 
            for key, value in result.items()
        }