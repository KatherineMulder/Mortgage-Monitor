from decimal import Decimal

class Mortgage:
    def __init__(self, mortgage_id, mortgage_name, initial_interest, initial_term, initial_principal,
                 deposit=0, extra_costs=0):
        self._mortgage_id = mortgage_id
        self._mortgage_name = mortgage_name
        self._initial_interest = initial_interest
        self._initial_term = initial_term
        self._initial_principal = initial_principal
        self._deposit = deposit
        self._extra_costs = extra_costs

    @property
    def mortgage_id(self):
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, mortgage_id):
        if not mortgage_id:
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
        if not initial_interest:
            raise ValueError("Initial interest is required")
        self._initial_interest = initial_interest

    @property
    def initial_term(self):
        return self._initial_term

    @initial_term.setter
    def initial_term(self, initial_term):
        if not initial_term:
            raise ValueError("Initial term is required")
        self._initial_term = initial_term

    @property
    def initial_principal(self):
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, initial_principal):
        if not initial_principal:
            raise ValueError("Initial principal is required")
        self._initial_principal = initial_principal

    @property
    def deposit(self):
        return self._deposit

    @deposit.setter
    def deposit(self, deposit):
        self._deposit = deposit

    @property
    def extra_costs(self):
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, extra_costs):
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
        initial_interest=5.0,
        initial_term=30,
        initial_principal=300000,
        deposit=5000,
        extra_costs=1000
    )

    print(mortgage)
    assert (
            str(mortgage)
            == "Mortgage ID: 1\nMortgage Name: test Mortgage\nInitial Interest: "
               "5.0\nInitial Term: 30\nInitial Principal: 300000\nDeposit: 5000\nExtra Costs: 1000"
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
    print("End Tests")
