def validate_birthdata(data: dict):
    if not data["name"]:
        raise ValueError("Name is required")

    if not (1 <= data["DOB"]["month"] <= 12):
        raise ValueError("Invalid month")

    if not (1 <= data["DOB"]["day"] <= 31):
        raise ValueError("Invalid day")

    if not (0 <= data["TOB"]["hour"] <= 23):
        raise ValueError("Invalid hour")

    if not (0 <= data["TOB"]["min"] <= 59):
        raise ValueError("Invalid minute")

    if (data["POB"]["timezone"] % 0.5) != 0:
        raise ValueError("Timezone must be in 0.5 increments")

    return True