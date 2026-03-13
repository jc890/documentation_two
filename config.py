from datetime import date
import os

from dotenv import load_dotenv

load_dotenv()

# -------------------------------------------------------
# DATABASE CONFIGURATION
# -------------------------------------------------------

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1sust@123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5050")

print(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
# -------------------------------------------------------
# EMBEDDING CONFIGURATION
# -------------------------------------------------------

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
SIMILARITY_THRESHOLD = 0.85


# -------------------------------------------------------
# DEFAULT AUDIT SETTINGS
# -------------------------------------------------------

DEFAULT_AUDIT_NAME = "Pre Electrical Audit 2026"
DEFAULT_AUDIT_TYPE = "pre"   # pre / post

DEFAULT_START_DATE = date(2026, 3, 1)
DEFAULT_END_DATE = date(2026, 3, 5)


# -------------------------------------------------------
# REPORT SETTINGS
# -------------------------------------------------------

# Prompts user for name, then adds .docx extension
report_name = input("Enter the report name: ")
REPORT_FILE_NAME = f"{report_name}.docx"
print(f"File will be saved as: {REPORT_FILE_NAME}")



# -------------------------------------------------------
# WHATSAPP PARSING SETTINGS
# -------------------------------------------------------

CHAT_FILE_NAME = "_chat.txt"

MIN_MESSAGE_LENGTH = 5

IGNORED_MESSAGES = [
    "ok",
    "okay",
    "yes",
    "no",
    "done",
    
]