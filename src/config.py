import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    CLICKHOUSE_HOST = "q9gou7xoo6.ap-south-1.aws.clickhouse.cloud"
    CLICKHOUSE_USER = "shashini"
    CLICKHOUSE_PASSWORD = "78e76q}D7£6["
    CLICKHOUSE_DATABASE = "default"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    # App Configuration
    MAX_CHAT_HISTORY = 10
    DEFAULT_TIMEZONE = 'Asia/Colombo'
    WORK_HOURS_START = '07:30:00'
    WORK_HOURS_END = '19:30:00'

# Machine mappings moved from main file
MACHINE_MAPPINGS = {
    'production': {
        'stenter1': 'TJ-Stenter01 Length(ioid2)',
        'stenter01': 'TJ-Stenter01 Length(ioid2)',
        # ... rest of mappings
    },
    # ... other mapping categories
}