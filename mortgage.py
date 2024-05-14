from decimal import Decimal


class Mortgage:
    def __init__(self, mortgage_id, mortgage_name, initial_interest, initial_term,
                 initial_principal,deposit, extra_costs):
        self.mortgage_id = mortgage_id
        self.mortgage_name = mortgage_name
        self.initial_interest = initial_interest
        self.initial_term = initial_term
        self.initial_principal = initial_principal
        self.deposit = deposit
        self.extra_costs = extra_costs

    @property
    def mortgage_id(self):
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, mortgage_id):
        if mortgage_id is None:
            raise ValueError("Mortgage ID is required")
        self._mortgage_id = mortgage_id

    @property
    def mortgage_name(self):
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, mortgage_name):
        if not mortgage_name:
            raise ValueError("Mortgage name is required")
        self._mortgage_name = mortgage_name

    @property
    def initial_interest(self):
        return self._initial_interest

    @initial_interest.setter
    def initial_interest(self, initial_interest):
        if initial_interest is None:
            raise ValueError("Initial interest is required")
        if initial_interest < 0:
            raise ValueError("Initial interest cannot be negative")
        self._initial_interest = initial_interest

    @property
    def initial_term(self):
        return self._initial_term

    @initial_term.setter
    def initial_term(self, initial_term):
        if initial_term is None:
            raise ValueError("Initial term is required")
        if initial_term < 0:
            raise ValueError("Initial term cannot be negative")
        self._initial_term = initial_term

    @property
    def initial_principal(self):
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, initial_principal):
        if initial_principal is None:
            raise ValueError("Initial principal is required")
        if initial_principal < 0:
            raise ValueError("Initial principal cannot be negative")
        self._initial_principal = initial_principal

    @property
    def deposit(self):
        return self._deposit

    @deposit.setter
    def deposit(self, deposit):
        if deposit is None:
            raise ValueError("Deposit is required")
        if deposit < 0:
            raise ValueError("Deposit cannot be negative")
        self._deposit = deposit

    @property
    def extra_costs(self):
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, extra_costs):
        if extra_costs is None:
            raise ValueError("Extra costs are required")
        if extra_costs < 0:
            raise ValueError("Extra costs cannot be negative")
        self._extra_costs = extra_costs

    def total_loan_amount(self):
        return self._initial_principal - self._deposit + self._extra_costs

    def calculate_monthly_interest(self):
        total_loan_amount = self._initial_principal - self._deposit + self._extra_costs
        if total_loan_amount > 0:
            return (Decimal(str(total_loan_amount)) * Decimal(str(self._initial_interest)) / Decimal('12') / Decimal(
                '100')).quantize(Decimal('.01'))
        else:
            return Decimal('0')

    def calculate_monthly_repayment(self):
        rate_per_month = Decimal(str(self._initial_interest)) / Decimal('12') / Decimal('100')
        term_in_months = self._initial_term * 12
        total_loan_amount = self._initial_principal - self._deposit + self._extra_costs
        if total_loan_amount > 0:
            return (Decimal(str(total_loan_amount)) * (
                    rate_per_month / (Decimal('1') - (Decimal('1') + rate_per_month) ** -term_in_months))).quantize(
                Decimal('.01'))
        else:
            return Decimal('0')

    def calculate_monthly_principal_repayment(self):
        monthly_interest = self.calculate_monthly_interest()
        monthly_repayment = self.calculate_monthly_repayment()
        return monthly_repayment - monthly_interest

    # def calculate_principal_remaining(self, months):
    #     remaining_principal = Decimal(str(self._initial_principal))
    #     for _ in range(months):
    #         monthly_principal_repayment = self.calculate_monthly_principal_repayment()
    #         remaining_principal -= monthly_principal_repayment
    #     return remaining_principal

    def calculate_fortnightly_interest(self):
        total_loan_amount = self._initial_principal - self._deposit + self._extra_costs
        if total_loan_amount > 0:
            return (Decimal(str(total_loan_amount)) * Decimal(str(self._initial_interest)) / Decimal('26') / Decimal(
                '100')).quantize(Decimal('.01'))
        else:
            return Decimal('0')

    def calculate_fortnightly_repayment(self):
        rate_per_fortnight = Decimal(str(self._initial_interest)) / Decimal('26') / Decimal('100')
        term_in_fortnights = self._initial_term * 26
        total_loan_amount = self._initial_principal - self._deposit + self._extra_costs
        if total_loan_amount > 0:
            return (Decimal(str(total_loan_amount)) * (rate_per_fortnight / (
                    Decimal('1') - (Decimal('1') + rate_per_fortnight) ** -term_in_fortnights))).quantize(
                Decimal('.01'))
        else:
            return Decimal('0')

    def calculate_fortnightly_principal_repayment(self):
        fortnightly_interest = self.calculate_fortnightly_interest()
        fortnightly_repayment = self.calculate_fortnightly_repayment()
        return fortnightly_repayment - fortnightly_interest

    def calculate_fortnightly_principal_remaining(self, fortnights):
        remaining_principal = Decimal(str(self._initial_principal))
        for _ in range(fortnights):
            fortnightly_principal_repayment = self.calculate_fortnightly_principal_repayment()
            remaining_principal -= fortnightly_principal_repayment
        return remaining_principal

    def calculate_remaining_balance_monthly(self, months_paid):
        monthly_interest_rate = self.initial_interest / 12 / 100
        total_payments = self.initial_term * 12
        monthly_payment = (self.initial_principal * monthly_interest_rate) / (
                    1 - (1 + monthly_interest_rate) ** -total_payments)  # Calculate monthly payment
        total_paid = monthly_payment * months_paid
        remaining_balance = self.initial_principal - total_paid
        return round(remaining_balance,2)

    def calculate_remaining_balance_fortnightly(self, fortnights_paid):
        fortnightly_interest_rate = self.initial_interest / 26 / 100
        total_payments = self.initial_term * 26
        fortnightly_payment = (self.initial_principal * fortnightly_interest_rate) / (
                1 - (1 + fortnightly_interest_rate) ** -total_payments)
        total_paid = fortnightly_payment * fortnights_paid
        remaining_balance = self.initial_principal - total_paid
        return round(remaining_balance, 2)

    def update_mortgage(self, new_loan_amount, new_interest_rate, new_loan_term, new_extra_cost=0, new_adjustment_description=None):
        self.initial_principal = new_loan_amount
        self.initial_interest = new_interest_rate
        self.initial_term = new_loan_term
        self.extra_costs = new_extra_cost
        # Update adjustment description if provided
        if new_adjustment_description is not None:
            self.mortgage_name = new_adjustment_description

    def __str__(self):
        return "\n".join([
            f"Mortgage ID: {self.mortgage_id}",
            f"Mortgage Name: {self.mortgage_name}",
            f"Initial Interest: {self.initial_interest}",
            f"Initial Term: {self.initial_term}",
            f"Initial Principal: {self.initial_principal}",
            f"Deposit: {self.deposit}",
            f"Extra Costs: {self.extra_costs}",
        ])


if __name__ == "__main__":
    print("Start Tests")
    mortgage = Mortgage(
        mortgage_id=1,
        mortgage_name="test Mortgage",
        initial_interest=5,
        initial_term=30,
        initial_principal=300000,
        deposit=5000,
        extra_costs=1000
    )
    print("Actual String Representation:")
    print(str(mortgage))
    print("\nExpected String Representation:")
    expected_string = (
        "Mortgage ID: 1\n"
        "Mortgage Name: test Mortgage\n"
        "Initial Interest: 5\n"
        "Initial Term: 30\n"
        "Initial Principal: 300000\n"
        "Deposit: 5000\n"
        "Extra Costs: 1000"
    )

    print(mortgage)

    assert (
            str(mortgage)
            == expected_string
    ), "__str__ not the same"

    mortgage.mortgage_name = "New Mortgage"
    assert mortgage.mortgage_name == "New Mortgage", "just a getter and setter"

    try:
        mortgage.mortgage_id = ""
    except ValueError:
        pass
    except:
        raise

    print("Monthly Interest:", mortgage.calculate_monthly_interest())
    print("Monthly Repayment:", mortgage.calculate_monthly_repayment())
    print("Monthly Principal Repayment:", mortgage.calculate_monthly_principal_repayment())
    print("Fortnightly Interest:", mortgage.calculate_fortnightly_interest())
    print("Fortnightly Repayment:", mortgage.calculate_fortnightly_repayment())
    print("Fortnightly Principal Repayment:", mortgage.calculate_fortnightly_principal_repayment())


    # remaining_balance function
    months_paid = 12
    remaining_balance = mortgage.calculate_remaining_balance_monthly(months_paid)
    print(f"Remaining balance after {months_paid} months: {remaining_balance}")

    fortnights_paid = 24
    remaining_balance_fortnightly = mortgage.calculate_remaining_balance_fortnightly(fortnights_paid)
    print(f"Remaining balance after {fortnights_paid} fortnights: {remaining_balance_fortnightly}")

    print("End Tests")



