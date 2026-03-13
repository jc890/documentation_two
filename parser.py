import re
import pandas as pd


def parse_chat(lines):
    """
    Parse WhatsApp exported chat text into structured dataframe.
    Works with cleaner.py and keeps comma structure intact.
    """

    records = []

    header_pattern = re.compile(
        r'^(\d{1,2}/\d{1,2}/\d{2}),\s*(\d{1,2}:\d{2})\s*-\s*(.*?):\s*(.*)'
    )

    image_pattern = re.compile(
        r'(IMG-\d+-WA\d+\.(?:jpg|jpeg|png))',
        re.IGNORECASE
    )

    current_message = None

    for line in lines:

        line = line.strip()

        header_match = header_pattern.match(line)

        # ---------------------------------------------------
        # NEW MESSAGE
        # ---------------------------------------------------
        if header_match:

            if current_message:
                records.append(current_message)

            date = header_match.group(1)
            time = header_match.group(2)
            sender = header_match.group(3)
            message = header_match.group(4)

            image_match = image_pattern.search(message)

            image_name = None
            if image_match:
                image_name = image_match.group(1)

            # remove image name and attachment text
            message_clean = image_pattern.sub("", message)
            message_clean = message_clean.replace("(file attached)", "")
            message_clean = message_clean.replace("<Media omitted>", "")

            message_clean = re.sub(r"\s+", " ", message_clean).strip()

            current_message = {
                "Date": date,
                "Time": time,
                "Sender": sender,
                "Message": message_clean,
                "Image": image_name
            }

        # ---------------------------------------------------
        # CONTINUATION LINE (multi-line WhatsApp messages)
        # ---------------------------------------------------
        else:

            if current_message:

                extra_text = line.strip()

                extra_text = re.sub(r"\s+", " ", extra_text)

                current_message["Message"] += " " + extra_text

    # append last message
    if current_message:
        records.append(current_message)

    df = pd.DataFrame(records)

    print("Parsed dataframe preview:")
    print(df.head(10))

    print("\nColumns:", df.columns)
    print("Total rows:", len(df))

    return df