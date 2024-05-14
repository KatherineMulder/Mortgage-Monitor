class AnalysisPeriod:
    def __init__(self, period_type, start_date, end_date):
        self._period_type = period_type
        self._start_date = start_date
        self._end_date = end_date

    @property
    def period_type(self):
        return self._period_type

    @period_type.setter
    def period_type(self, value):
        self._period_type = value

    @property
    def start_date(self):
        return self._start_date

    @start_date.setter
    def start_date(self, value):
        self._start_date = value

    @property
    def end_date(self):
        return self._end_date

    @end_date.setter
    def end_date(self, value):
        self._end_date = value

    def calculate_duration(self):
        """
        calculate the duration of the analysis period.
        """
        if self._period_type == "Days":
            return (self._end_date - self._start_date).days
        elif self._period_type == "Months":

            return (self._end_date.year - self._start_date.year) * 12 + (self._end_date.month - self._start_date.month)
        elif self._period_type == "Years":

            return self._end_date.year - self._start_date.year
        else:
            # handle invalid period type?
            return None

    def validate_date_range(self):
        """
        Validate the date range and period type.
        """
        if self._start_date >= self._end_date:
            return False  # end date must be after start date
        if self._period_type not in ["Days", "Months", "Years"]:
            return False  # invalid period type
        return True

    def adjust_start_date(self, new_start_date):
        """
        Adjust the start date of the analysis period.
        """
        self._start_date = new_start_date

    def adjust_end_date(self, new_end_date):
        """
        Adjust the end date of the analysis period.
        """
        self._end_date = new_end_date

    def adjust_period_type(self, new_period_type):
        """
        Adjust the period type of the analysis period.
        """
        self._period_type = new_period_type

    def __str__(self):
        """
        Return a string representation of the analysis period.
        """
        return f"Analysis Period: {self._period_type} from {self._start_date} to {self._end_date}"

