import re

def clean_text(text):
    """Clean text (remove special characters and extra spaces)."""
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()