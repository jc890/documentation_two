import re
from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

from database.models import Base, Audit, Fault
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


# -------------------------------------------------------
# DATABASE NAME
# -------------------------------------------------------

def get_db_name(hospital_name):

    return f"{hospital_name.lower().replace(' ', '_')}_db"


# -------------------------------------------------------
# CREATE DATABASE
# -------------------------------------------------------

def create_database_if_not_exists(hospital_name):

    db_name = get_db_name(hospital_name)

    encoded_password = quote_plus(DB_PASSWORD)

    engine = create_engine(
        f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/postgres"
    )

    with engine.connect() as conn:

        conn = conn.execution_options(isolation_level="AUTOCOMMIT")

        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname=:name"),
            {"name": db_name}
        ).fetchone()

        if not result:
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"Database {db_name} created.")
        else:
            print(f"Database {db_name} already exists.")

    return db_name


# -------------------------------------------------------
# ENGINE
# -------------------------------------------------------

def get_engine(db_name):

    encoded_password = quote_plus(DB_PASSWORD)

    return create_engine(
        f"postgresql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{db_name}"
    )


# -------------------------------------------------------
# SCHEMA
# -------------------------------------------------------

def initialize_schema(engine):

    Base.metadata.create_all(engine)

    print("Schema initialized successfully.")


# -------------------------------------------------------
# CREATE AUDIT
# -------------------------------------------------------

def create_audit(session, name, audit_type, start_date, end_date):

    audit = Audit(
        audit_name=name,
        audit_type=audit_type,
        start_date=start_date,
        end_date=end_date
    )

    session.add(audit)
    session.commit()

    print(f"Audit '{name}' created.")

    return audit


# -------------------------------------------------------
# CLUSTER LOGIC
# -------------------------------------------------------

def get_cluster_id(session, audit_id, building, fault_type):

    """
    Same audit + same building + same fault → same cluster
    """

    result = session.execute(
        text("""
        SELECT cluster_id
        FROM faults
        WHERE audit_id=:a
        AND building=:b
        AND fault_type=:f
        LIMIT 1
        """),
        {"a": audit_id, "b": building, "f": fault_type}
    ).fetchone()

    if result:
        return result[0]

    max_cluster = session.execute(
        text("SELECT COALESCE(MAX(cluster_id),0) FROM faults")
    ).scalar()

    return max_cluster + 1


# -------------------------------------------------------
# INSERT FAULT
# -------------------------------------------------------

def insert_fault(session, audit_id, building, asset, fault_type, message, image_path=None):

    building = (building or "unknown").strip().lower()
    asset = (asset or "unknown").strip().lower()
    fault_type = (fault_type or "general fault").strip().lower()
    message = (message or "").strip()

    # normalize image name
    if image_path:
        image_path = image_path.strip()
        image_path = re.sub(r"\(file attached\)", "", image_path).strip()

    # avoid duplicates
    existing = session.query(Fault).filter_by(
        audit_id=audit_id,
        building=building,
        fault_type=fault_type,
        message=message
    ).first()

    if existing:
        return False

    cluster_id = get_cluster_id(session, audit_id, building, fault_type)

    fault = Fault(
        audit_id=audit_id,
        date=date.today(),
        building=building,
        asset=asset,
        fault_type=fault_type,
        message=message,
        cluster_id=cluster_id,
        image_path=image_path
    )

    session.add(fault)

    return True