import sys
from datetime import date
import pandas as pd

from config import (
    DEFAULT_AUDIT_NAME,
    DEFAULT_AUDIT_TYPE,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
)

from whatsapp.extractor import extract_chat
from whatsapp.parser import parse_chat
from whatsapp.cleaner import (
    filter_by_message_boundary,
    clean_messages,
    split_faults,
)

from database.db_manager import (
    create_database_if_not_exists,
    get_engine,
    initialize_schema,
    create_audit,
    insert_fault,
)

from sqlalchemy.orm import sessionmaker
from reports.docx_generator import generate_docx_report


# -------------------------------------------------------
# CORE PIPELINE
# -------------------------------------------------------

def process_whatsapp_chat(zip_path, start_msg, end_msg, hospital_name):

    print("\n--- STEP 1: Extracting chat ---")
    lines, image_folder = extract_chat(zip_path)

    
    print("--- STEP 2: Parsing chat ---")
    df_parse = parse_chat(lines)

    # create timestamp column once
    df_parse["timestamp"] = pd.to_datetime(
        df_parse["Date"].astype(str) + " " + df_parse["Time"].astype(str),
        errors="coerce"
    )

    print("\nParsed dataframe preview:")
    print(df_parse.head(10))
    print("\nColumns:", df_parse.columns)
    print("Total rows:", len(df_parse))
    print("\nParsed dataframe preview:")
    print(df_parse.head(10))
    print("\nColumns:", df_parse.columns)
    print("Total rows:", len(df_parse))

  
    print("\n--- STEP 4: Filtering by boundary ---")
    df_filtered = filter_by_message_boundary(df_parse, start_msg, end_msg)

    print(f"Rows after boundary filter: {len(df_filtered)}")

    if not df_filtered.empty:
        print("\nFirst 10 rows:")
        print(df_filtered[["Date", "Message", "Image"]].head(10).to_string(index=False))
    else:
        print("Filtered DataFrame is empty!")
    print("\n--- STEP 3: Cleaning messages ---")
    df_clean = clean_messages(df_filtered)

    
    df_clean = df_clean[
    df_clean["Image"].fillna("").astype(str).str.strip() != ""
    ].copy()
    
    print("\n=== DEBUG: Cleaned image rows ===")
    print(df_clean[["Date", "Time", "Message", "Image"]].head(20).to_string(index=False))

    print(f"\nRows after cleaning: {len(df_clean)}")
    print("\n--- STEP 5: Splitting faults ---")
    df_faults = split_faults(df_clean)

    print(f"Rows after splitting faults: {len(df_faults)}")

    print("\n--- STEP 6: Setting up database ---")

    db_name = create_database_if_not_exists(hospital_name)

    engine = get_engine(db_name)

    initialize_schema(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    print("\n--- STEP 7: Creating audit ---")

    audit = create_audit(
        session=session,
        name=DEFAULT_AUDIT_NAME,
        audit_type=DEFAULT_AUDIT_TYPE,
        start_date=DEFAULT_START_DATE,
        end_date=DEFAULT_END_DATE,
    )

    print("\n--- STEP 8: Inserting faults into DB ---")

    inserted = 0

    for _, row in df_faults.iterrows():

        try:

            result = insert_fault(
                session=session,
                audit_id=audit.id,
                building=row.get("Building", "Unknown"),
                asset=row.get("Asset", "Unknown"),
                fault_type=row.get("Fault Type", "General Fault"),
                message=row.get("Message", ""),
                image_path=row.get("Image", None)
            )

            if result:
                inserted += 1

        except Exception as e:

            session.rollback()
            print(f"Error inserting fault: {e}")

    session.commit()

    print(f"\nInserted {inserted} faults successfully.")

    # ----------------------------------------
    # STEP 9: Generate Report
    # ----------------------------------------

    print("\n--- STEP 9: Generating DOCX report ---")

    generate_docx_report(
        session=session,
        audit_id=audit.id,
        image_folder=image_folder
    )

    print("\nSystem execution completed successfully.")


# -------------------------------------------------------
# ENTRY POINT
# -------------------------------------------------------

def main():

    print("\nElectrical Audit Intelligence System\n")

    try:

        zip_path = input("Enter WhatsApp ZIP file path: ").strip()

        hospital_name = input("Enter hospital name: ").strip()

        start_msg = input("Enter START message text (partial match): ").lower().strip()

        end_msg = input("Enter END message text (partial match): ").lower().strip()

        if not zip_path or not hospital_name:
            raise ValueError("ZIP path and hospital name are required.")

        process_whatsapp_chat(
            zip_path=zip_path,
            start_msg=start_msg,
            end_msg=end_msg,
            hospital_name=hospital_name,
        )

    except Exception as e:

        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()