from datetime import datetime


def get_current_datetime_in_dm() -> str:
    """
    Get the current date and format it as DDMM.
    """
    d = datetime.now()
    return d.strftime("%d%m")
