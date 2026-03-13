import re
import pandas as pd
from config import MIN_MESSAGE_LENGTH, IGNORED_MESSAGES


# ---------------------------------------------------
# NORMALIZE TEXT
# ---------------------------------------------------
def normalize_text(text):

    text = str(text).lower()

    text = re.sub(r"<.*?>", " ", text)

    # keep comma because parser depends on it
    text = re.sub(r"[^a-z0-9,\-/\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------------------
# EXTRACT WHATSAPP IMAGE ID
# ---------------------------------------------------
def extract_wa_id(text):

    if pd.isna(text) or text is None:
        return None

    match = re.search(r"wa\d+", str(text).lower())

    return match.group(0) if match else None


# ---------------------------------------------------
# FILTER CHAT BETWEEN START AND END MESSAGE
# ---------------------------------------------------
import pandas as pd
import re


def extract_timestamp_from_input(text):

    match = re.search(r"(\d{1,2}/\d{1,2}/\d{2}),\s*(\d{1,2}:\d{2})", text)

    if not match:
        raise ValueError("Could not extract date/time from input")

    date = match.group(1)
    time = match.group(2)

    return pd.to_datetime(f"{date} {time}", errors="coerce")


def filter_by_message_boundary(df, start_msg, end_msg):

    start_id = extract_wa_id(start_msg)
    end_id = extract_wa_id(end_msg)

    start_time = extract_timestamp_from_input(start_msg)
    end_time = extract_timestamp_from_input(end_msg)

    if not start_id or not end_id:
        raise ValueError("Could not extract WA IDs")

    df = df.copy()

    if "timestamp" not in df.columns:
        df["timestamp"] = pd.to_datetime(
            df["Date"].astype(str) + " " + df["Time"].astype(str),
            errors="coerce"
        )

    df["wa_id"] = df["Image"].apply(extract_wa_id)

    # ---------------------------------------
    # exact start row
    # ---------------------------------------

    start_rows = df[
        (df["wa_id"] == start_id) &
        (df["timestamp"] == start_time)
    ]

    if start_rows.empty:
        raise ValueError("Exact start message not found")

    start_index = start_rows.index[0]

    # ---------------------------------------
    # exact end row
    # ---------------------------------------

    end_rows = df[
        (df["wa_id"] == end_id) &
        (df["timestamp"] == end_time)
    ]

    if end_rows.empty:
        raise ValueError("Exact end message not found")

    end_index = end_rows.index[0]

    if start_index > end_index:
        raise ValueError("Start appears after end")

    df_filtered = df.iloc[start_index:end_index + 1].copy()

    df_filtered.drop(columns=["wa_id"], inplace=True)

    print(f"Rows after boundary filter: {len(df_filtered)}")

    return df_filtered
# ---------------------------------------------------
# CLEAN TEXT MESSAGES
# ---------------------------------------------------
def clean_messages(df):

    def clean_text(text):

        text = str(text).lower()

        text = re.sub(r"<media omitted>", "", text)
        text = re.sub(r"this message was deleted", "", text)

        text = re.sub(r"http\S+", "", text)

        # keep commas for parsing
        text = re.sub(r"[^a-z0-9,\-/\s]", " ", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    df = df.copy()

    df["Message"] = df["Message"].apply(clean_text)
    df = df[df["Image"].notna()]
    df = df[df["Message"].notna()]
    df = df[df["Message"].str.strip() != ""]

    df = df[df["Message"].str.len() >= MIN_MESSAGE_LENGTH]

    df = df[~df["Message"].isin(IGNORED_MESSAGES)]

    print("Rows after cleaning:", len(df))

    return df


# ---------------------------------------------------
# SPLIT BUILDING / AREA / ASSET / FAULT
# ---------------------------------------------------
def split_faults(df):

    rows = []

    asset_keywords = [
        "db", "vdb", "pldb", "pdb",
        "panel", "control panel",
        "mcc", "ups", "transformer"
    ]

    for _, row in df.iterrows():

        msg = str(row["Message"]).lower()

        building = "unknown"
        area = "unknown"
        asset = "unknown"

        faults = []

        if "," in msg:

            parts = [p.strip() for p in msg.split(",") if p.strip()]

            if len(parts) >= 1:
                building = parts[0]

            if len(parts) >= 2:
                area = parts[1]

            asset_index = None

            # detect asset position
            for i, p in enumerate(parts):

                if any(k in p for k in asset_keywords):
                    asset = p
                    asset_index = i

            # everything after asset = faults
            if asset_index is not None and asset_index + 1 < len(parts):
                faults = parts[asset_index + 1:]

        if not faults:
            faults = ["general fault"]

        # create separate rows for each fault
        for fault in faults:

            rows.append([
                row["Date"],
                row["Time"],
                row["Sender"],
                msg,
                building,
                area,
                asset,
                fault,
                row["Image"]
            ])

    df_expanded = pd.DataFrame(
        rows,
        columns=[
            "Date",
            "Time",
            "Sender",
            "Message",
            "Building",
            "Area",
            "Asset",
            "Fault Type",
            "Image"
        ]
    )

    print("Rows after splitting faults:", len(df_expanded))

    return df_expanded