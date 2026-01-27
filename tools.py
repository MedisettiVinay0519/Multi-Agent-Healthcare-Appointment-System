from __future__ import annotations
from langchain_core.tools import tool
from typing import Literal
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

# --------------------------------------------------
# DATA PATH (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------
DATA_PATH = Path(r"C:\Users\LENOVO\Downloads\availability.csv")

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def load_data():
    return pd.read_csv(DATA_PATH)


def save_data(df):
    df.to_csv(DATA_PATH, index=False)


def validate_date(date: str):
    if not re.match(r"^\d{2}-\d{2}-\d{4}$", date):
        raise ValueError("Date must be in DD-MM-YYYY format")


def validate_datetime(dt: str):
    if not re.match(r"^\d{2}-\d{2}-\d{4} \d{2}:\d{2}$", dt):
        raise ValueError("Datetime must be in DD-MM-YYYY HH:MM format")


def validate_id(id_number: int):
    if not re.match(r"^\d{7,8}$", str(id_number)):
        raise ValueError("ID must be 7 or 8 digits")


def normalize_datetime(dt_str: str) -> str:
    """Convert DD-MM-YYYY HH:MM → DD-MM-YYYY H.MM"""
    dt = datetime.strptime(dt_str, "%d-%m-%Y %H:%M")
    return f"{dt.day:02d}-{dt.month:02d}-{dt.year} {dt.hour}.{dt.minute:02d}"

# --------------------------------------------------
# INFORMATION TOOLS
# --------------------------------------------------

@tool
def check_availability_by_doctor(
    desired_date: str,
    doctor_name: Literal[
        "kevin anderson","robert martinez","susan davis","daniel miller",
        "sarah wilson","michael green","lisa brown","jane smith",
        "emily johnson","john doe"
    ]
):
    """Check availability for a specific doctor on a given date."""
    validate_date(desired_date)

    df = load_data()
    df["date_only"] = df["date_slot"].astype(str).str.split(" ").str[0]
    df["time_only"] = df["date_slot"].astype(str).str.split(" ").str[1]

    rows = df[
        (df["date_only"] == desired_date)
        & (df["doctor_name"] == doctor_name)
        & (df["is_available"] == True)
    ]["time_only"].tolist()

    if not rows:
        return f"No availability for {doctor_name} on {desired_date}."

    return f"Available slots for {doctor_name} on {desired_date}: {', '.join(rows)}"


@tool
def check_availability_by_specialization(
    desired_date: str,
    specialization: Literal[
        "general_dentist","cosmetic_dentist","prosthodontist",
        "pediatric_dentist","emergency_dentist",
        "oral_surgeon","orthodontist"
    ]
):
    """Check availability by specialization."""
    validate_date(desired_date)

    df = load_data()
    df["date_only"] = df["date_slot"].astype(str).str.split(" ").str[0]
    df["time_only"] = df["date_slot"].astype(str).str.split(" ").str[1]

    rows = df[
        (df["date_only"] == desired_date)
        & (df["specialization"] == specialization)
        & (df["is_available"] == True)
    ]

    if rows.empty:
        return f"No availability for {specialization} on {desired_date}."

    output = f"Availability for {specialization} on {desired_date}:\n"
    for doctor, group in rows.groupby("doctor_name"):
        times = ", ".join(group["time_only"].tolist())
        output += f"{doctor}: {times}\n"

    return output

# --------------------------------------------------
# BOOKING TOOLS
# --------------------------------------------------

@tool
def set_appointment(
    desired_date: str,
    id_number: int,
    doctor_name: Literal[
        "kevin anderson","robert martinez","susan davis","daniel miller",
        "sarah wilson","michael green","lisa brown","jane smith",
        "emily johnson","john doe"
    ]
):
    """Book an appointment."""
    validate_datetime(desired_date)
    validate_id(id_number)

    df = load_data()
    slot = normalize_datetime(desired_date)

    case = df[
        (df["date_slot"] == slot)
        & (df["doctor_name"] == doctor_name)
        & (df["is_available"] == True)
    ]

    if case.empty:
        return "No available appointment for that time."

    df.loc[case.index, ["is_available", "patient_to_attend"]] = [False, id_number]
    save_data(df)

    return "Appointment successfully booked."


@tool
def cancel_appointment(
    date: str,
    id_number: int,
    doctor_name: Literal[
        "kevin anderson","robert martinez","susan davis","daniel miller",
        "sarah wilson","michael green","lisa brown","jane smith",
        "emily johnson","john doe"
    ]
):
    """Cancel an existing appointment."""
    validate_datetime(date)
    validate_id(id_number)

    df = load_data()
    slot = normalize_datetime(date)

    case = df[
        (df["date_slot"] == slot)
        & (df["patient_to_attend"] == id_number)
        & (df["doctor_name"] == doctor_name)
    ]

    if case.empty:
        return "No matching appointment found."

    df.loc[case.index, ["is_available", "patient_to_attend"]] = [True, None]
    save_data(df)

    return "Appointment cancelled successfully."


@tool
def reschedule_appointment(
    old_date: str,
    new_date: str,
    id_number: int,
    doctor_name: Literal[
        "kevin anderson","robert martinez","susan davis","daniel miller",
        "sarah wilson","michael green","lisa brown","jane smith",
        "emily johnson","john doe"
    ]
):
    """Reschedule an appointment."""
    validate_datetime(old_date)
    validate_datetime(new_date)
    validate_id(id_number)

    cancel_result = cancel_appointment(
        date=old_date,
        id_number=id_number,
        doctor_name=doctor_name
    )

    if "successfully" not in cancel_result.lower():
        return cancel_result

    return set_appointment(
        desired_date=new_date,
        id_number=id_number,
        doctor_name=doctor_name
    )
