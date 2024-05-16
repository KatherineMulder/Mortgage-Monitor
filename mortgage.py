from decimal import Decimal


class Mortgage:
    def __init__(self, comments=None, payment_override=None):
        self._mortgage_id = None
        self._mortgage_name = ""
        self._initial_interest = 0.0
        self._initial_term = 0
        self._initial_principal = 0.0
        self._deposit = 0.0
        self._extra_costs = 0.0
        self._comments = comments if comments else []
        self.payment_override = None
        self.initial_payment_breakdown = {}
        self.mortgage_maturity = {}
        self.amortization_schedule = []

    @property
    def mortgage_id(self):
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, value):
        if not isinstance(value, int):
            raise ValueError("mortgage ID must be an integer")
        if value < 0:
            raise ValueError("mortgage ID cannot be negative")
        self._mortgage_id = value

    @property
    def mortgage_name(self):
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, value):
        if not isinstance(value, str):
            raise ValueError("mortgage name must be a string")
        if not value:
            raise ValueError("mortgage name cannot be empty")
        self._mortgage_name = value

    @property
    def initial_interest(self):
        return self._initial_interest

    @initial_interest.setter
    def initial_interest(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("initial interest must be a numeric value")
        if value < 0:
            raise ValueError("initial interest cannot be negative")
        self._initial_interest = float(value)

    @property
    def initial_term(self):
        return self._initial_term

    @initial_term.setter
    def initial_term(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("initial term must be a number")
        if value <= 0:
            raise ValueError("initial term must be greater than zero")
        if value > 30:
            raise ValueError("maximum initial term is 30 years")
        self._initial_term = value

    @property
    def initial_principal(self):
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("initial principal must be a number")
        if value <= 0:
            raise ValueError("initial principal must be greater than zero")
        self._initial_principal = value

    @property
    def deposit(self):
        return self._deposit

    @deposit.setter
    def deposit(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("deposit must be a number")
        if value < 0:
            raise ValueError("deposit cannot be negative")
        if value > self._initial_principal:
            raise ValueError("deposit cannot be greater than the initial principal")
        self._deposit = value

    @property
    def extra_costs(self):
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("extra costs must be a number")
        if value < 0:
            raise ValueError("extra costs cannot be negative")
        self._extra_costs = value

    def calculate_initial_payment_breakdown(self):

        # monthly calculations
        total_loan_amount = self._initial_principal - self._deposit + self._extra_costs
        monthly_interest = Decimal('0')
        estimated_monthly_repayment = Decimal('0')
        monthly_principal_repayment = Decimal('0')

        if total_loan_amount > 0:
            # monthly interest
            monthly_interest = (Decimal(str(total_loan_amount)) * Decimal(str(self._initial_interest)) /
                                Decimal('12') / Decimal('100')).quantize(Decimal('.01'))
            # monthly repayment
            rate_per_month = Decimal(str(self._initial_interest)) / Decimal('12') / Decimal('100')
            term_in_months = self._initial_term * 12
            estimated_monthly_repayment = (Decimal(str(total_loan_amount)) * (
                    rate_per_month / (Decimal('1') - (Decimal('1') + rate_per_month) ** -term_in_months))).quantize(
                Decimal('.01'))
            # monthly principal repayment
            monthly_principal_repayment = estimated_monthly_repayment - monthly_interest

        # fortnightly calculations
        fortnightly_interest = Decimal('0')
        estimated_fortnightly_repayment = Decimal('0')
        fortnightly_principal_repayment = Decimal('0')

        if total_loan_amount > 0:
            # fortnightly interest
            fortnightly_interest = (Decimal(str(total_loan_amount)) * Decimal(str(self._initial_interest)) /
                                    Decimal('26') / Decimal('100')).quantize(Decimal('.01'))
            # fortnightly repayment
            rate_per_fortnight = Decimal(str(self._initial_interest)) / Decimal('26') / Decimal('100')
            term_in_fortnights = self._initial_term * 26
            estimated_fortnightly_repayment = (Decimal(str(total_loan_amount)) * (
                    rate_per_fortnight / (
                        Decimal('1') - (Decimal('1') + rate_per_fortnight) ** -term_in_fortnights))).quantize(
                Decimal('.01'))
            # fortnightly principal repayment
            fortnightly_principal_repayment = estimated_fortnightly_repayment - fortnightly_interest

        return (monthly_interest, estimated_monthly_repayment, monthly_principal_repayment,
                fortnightly_interest, estimated_fortnightly_repayment, fortnightly_principal_repayment)



    def update_initial_payment_breakdown(self, payment_override):
        pass



    def calculate_mortgage_maturity(self):
        pass

    def generate_amortization_schedule(self):
        pass


if __name__ == "__main__":
    print("start Tests")

    # Create a test Mortgage object
    mortgage = Mortgage()
    mortgage.mortgage_id = 1
    mortgage.mortgage_name = "test Mortgage"
    mortgage.initial_interest = 3.5
    mortgage.initial_term = 25
    mortgage.initial_principal = 300000
    mortgage.deposit = 50000
    mortgage.extra_costs = 10000

    # test the __str__ method
    print("testing __str__ method:")
    print(mortgage)

    # test the calculate_initial_payment_breakdown method
    print("\ntesting calculate_initial_payment_breakdown method:")
    breakdown = mortgage.calculate_initial_payment_breakdown()
    print("monthly Interest:", breakdown[0])
    print("monthly Repayment:", breakdown[1])
    print("monthly Principal Repayment:", breakdown[2])
    print("fortnightly Interest:", breakdown[3])
    print("fortnightly Repayment:", breakdown[4])
    print("fortnightly Principal Repayment:", breakdown[5])
    print("end Tests")
