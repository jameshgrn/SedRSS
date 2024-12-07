import os
from typing import Dict

# LLM Configuration
LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for faster, cheaper processing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Vector Store Configuration
VECTOR_STORE_PATH = "data/vector_store"

# Keywords for relevance scoring
KEYWORDS = [
    "sedimentology",
    "fluvial geomorphology",
    "stratigraphy",
    "deltatic geomorphology",
    "sediment transport",
    "earth surface processes",
    "rivers",
    "river channels",
    "deltas",
    "avulsion",
    "morphodynamics",
    "alluvial dynamics"
]

# Journal Impact Factors
JOURNAL_IMPACT_FACTORS: Dict[str, float] = {
    "Nature": 49.962,
    "Science": 47.728,
    "Nature Geoscience": 16.908,
    "Geology": 5.399,
    "Sedimentology": 3.825,
    "Journal of Sedimentary Research": 2.768,
    # Add more journals as needed
}

# Email Configuration
SMTP_CONFIG = {
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME"),
    "password": os.getenv("SMTP_PASSWORD"),
}

# Newsletter Configuration
SUBSCRIBER_LIST = os.getenv("SUBSCRIBER_LIST", "").split(",") 