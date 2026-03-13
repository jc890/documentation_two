import zipfile
import os

def extract_chat(zip_path):

    extract_folder = os.path.splitext(zip_path)[0] + "_extracted"

    os.makedirs(extract_folder, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:

        zip_ref.extractall(extract_folder)

        chat_file = None

        for file in zip_ref.namelist():
            if file.endswith(".txt"):
                chat_file = os.path.join(extract_folder, file)
                break

        if chat_file is None:
            raise Exception("No chat file found in ZIP")

        with open(chat_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    return lines, extract_folder

def parse_comma_message(message):

    parts = message.split(",")

    parts = [p.strip().lower() for p in parts]

    building = parts[0] if len(parts) > 0 else "Unknown"
    area = parts[1] if len(parts) > 1 else "Unknown"
    asset = parts[2] if len(parts) > 2 else "Unknown"
    issue = parts[3] if len(parts) > 3 else "General Fault"

    return building, area, asset, issue