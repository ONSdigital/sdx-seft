from datetime import datetime


class DatetimeService:
    def __init__(self):
        self.now = datetime.now()

    def get_current_datetime_in_dm(self) -> str:
        """
        Return the current date and format it as DDMM.
        """
        return self.now.strftime("%d%m")
