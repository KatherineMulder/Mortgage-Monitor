from decimal import Decimal
import math


class Mortgage:
    def __init__(self, mortgage_id, mortgage_name, initial_interest, initial_term,
                 initial_principal, deposit=0, extra_costs=0):

        self.mortgage_id = mortgage_id
        self.mortgage_name = mortgage_name
        self.initial_interest = initial_interest
        self.initial_term = initial_term
        self.initial_principal = initial_principal
        self.deposit = deposit
        self.extra_costs = extra_costs
        self.adjustment_description = None

    @property
    def mortgage_id(self):
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, value):
        self._mortgage_id = value

    @property
    def mortgage_name(self):
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, mortgage_name):
        if not mortgage_name:
            raise ValueError("mortgage name is required")
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

    """
    initial payment: 
    interest
    principle
    extra
    repayment
    """
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

    def calculate_monthly_principal_remaining(self, months):
        remaining_principal = Decimal(str(self._initial_principal))
        for _ in range(months):
            monthly_principal_repayment = self.calculate_monthly_principal_repayment()
            remaining_principal -= monthly_principal_repayment
        return remaining_principal

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

    # def calculate_fortnightly_principal_remaining(self, fortnights):
    #     remaining_principal = Decimal(str(self._initial_principal))
    #     for _ in range(fortnights):
    #         fortnightly_principal_repayment = self.calculate_fortnightly_principal_repayment()
    #         remaining_principal -= fortnightly_principal_repayment
    #     return remaining_principal

    # def calculate_remaining_balance_monthly(self, months_paid):
    #     """
    #     calculates the remaining balance specifically for monthly payments.
    #     t doesn't update any existing balance, it's a standalone calculation
    #     """
    #     monthly_interest_rate = self.initial_interest / 12 / 100
    #     total_payments = self.initial_term * 12
    #     monthly_payment = (self.initial_principal * monthly_interest_rate) / (
    #             1 - (1 + monthly_interest_rate) ** -total_payments)
    #     total_paid = monthly_payment * months_paid
    #     remaining_balance = self.initial_principal - total_paid
    #     return round(remaining_balance, 2)
    #
    # def calculate_remaining_balance_fortnightly(self, fortnights_paid):
    #     """
    #     it doesn't update any existing balance, it's a standalone calculation
    #     """
    #     fortnightly_interest_rate = self.initial_interest / 26 / 100
    #     total_payments = self.initial_term * 26
    #     fortnightly_payment = (self.initial_principal * fortnightly_interest_rate) / (
    #             1 - (1 + fortnightly_interest_rate) ** -total_payments)
    #     total_paid = fortnightly_payment * fortnights_paid
    #     remaining_balance = self.initial_principal - total_paid
    #     return round(remaining_balance, 2)
    #
    # # def calculate_remaining_balance(self, payments_paid):
    # #
    # #     """
    # #     for update the remaining balance based on the number of payments already made
    # #     and calculates the remaining balance for both monthly and fortnightly payment frequencies
    # #
    # #     """
    # #     monthly_interest_rate = self.initial_interest / 12 / 100
    # #     total_payments = self.initial_term * 12
    # #     remaining_payments = total_payments - payments_paid
    # #     monthly_payment = (self.initial_principal * monthly_interest_rate) / (
    # #             1 - (1 + monthly_interest_rate) ** -remaining_payments)
    # #
    # #     fortnightly_interest_rate = self.initial_interest / 26 / 100
    # #     total_payments_fortnightly = self.initial_term * 26
    # #     remaining_payments_fortnightly = total_payments_fortnightly - payments_paid
    # #     fortnightly_payment = (self.initial_principal * fortnightly_interest_rate) / (
    # #             1 - (1 + fortnightly_interest_rate) ** -remaining_payments_fortnightly)
    # #
    # #     total_paid_monthly = monthly_payment * payments_paid
    # #     remaining_balance_monthly = self.initial_principal - total_paid_monthly
    # #
    # #     total_paid_fortnightly = fortnightly_payment * payments_paid
    # #     remaining_balance_fortnightly = self.initial_principal - total_paid_fortnightly
    # #
    # #     return {
    # #         'monthly': round(remaining_balance_monthly, 2),
    # #         'fortnightly': round(remaining_balance_fortnightly, 2)
    # #     }

    """
    maturity:
    payment overfull term 
    
    """

    def payments_over_full_term_fortnight(self):
        payments_full_term = self.initial_term * 26
        return payments_full_term

    def payments_over_reduced_term_fortnight(self, reduced_term):
        if reduced_term == "n":
            return self.initial_term * 26
        else:
            principal_value = self.initial_principal
            rate_value = self.initial_interest / 100
            return -math.log(1 - principal_value / (self.initial_term * 26) * rate_value / 26) / (math.log(1 + rate_value / 26))

    def full_term_amortize_fortnight(self):
        return self.payments_over_full_term_fortnight() / 26

    def estimated_reduced_term_amortize_fortnight(self, reduced_term):
        payments_over_reduced_term = self.payments_over_reduced_term_fortnight(reduced_term)
        return payments_over_reduced_term / 26

    # TODO rounding discrepancies
    def interest_over_full_term_fortnight(self):
        fortnightly_repayment = self.calculate_fortnightly_repayment()
        term_in_fortnights = self.initial_term * 26
        total_amount = self.initial_principal - self.deposit + self.extra_costs
        return fortnightly_repayment * 26 * self.initial_term - total_amount

    # TODO rounding discrepancies
    def principal_and_interest_fortnight(self):
        total_amount = self.initial_principal - self.deposit + self.extra_costs
        interest_over_full_term = self.interest_over_full_term_fortnight()
        return total_amount + interest_over_full_term

    def interest_over_reduced_term_fortnight(self):
        if self.extra_costs == 0:
            return 0
        else:
            fortnightly_repayment = self.calculate_fortnightly_repayment()
            term_in_fortnights = self.initial_term * 26
            total_amount = self.initial_principal - self.deposit + self.extra_costs
            return fortnightly_repayment * 26 * self.initial_term - total_amount

    def principal_plus_interest_over_reduced_term_fortnight(self):
        if self.extra_costs == 0:
            return 0
        else:
            interest_over_reduced_term = self.interest_over_reduced_term_fortnight()
            total_principal_plus_interest = self.initial_principal + interest_over_reduced_term
            return total_principal_plus_interest


    def update_mortgage(self, new_loan_amount, new_interest_rate, new_loan_term, new_extra_cost=0, new_adjustment_description=None):
        self.initial_principal = new_loan_amount
        self.initial_interest = new_interest_rate
        self.initial_term = new_loan_term
        self.extra_costs = new_extra_cost
        self.adjustment_description = new_adjustment_description

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

    print("monthly Interest:", mortgage.calculate_monthly_interest())
    print("monthly Repayment:", mortgage.calculate_monthly_repayment())
    print("monthly Principal Repayment:", mortgage.calculate_monthly_principal_repayment())
    print("fortnightly Interest:", mortgage.calculate_fortnightly_interest())
    print("fortnightly Repayment:", mortgage.calculate_fortnightly_repayment())
    print("fortnightly Principal Repayment:", mortgage.calculate_fortnightly_principal_repayment())
    print("fnd initial payment tests")



    """
    maturity test
    """

    print("Start Maturity Tests")

    # test payments_over_full_term_fortnight method
    initial_term = 30
    expected_payments = initial_term * 26

    actual_payments = mortgage.payments_over_full_term_fortnight()

    if actual_payments == expected_payments:
        print("test passed: The calculated payments over the full term match the expected value.")
    else:
        print("test failed: The calculated payments over the full term do not match the expected value.")
        print("expected:", expected_payments)
        print("actual:", actual_payments)

    # payments over reduced term for fortnight
    payment = mortgage.payments_over_reduced_term_fortnight("n")
    print("payment over reduced term:", payment)

    # full term amortization amount per fortnight
    amortization_per_fortnight = mortgage.full_term_amortize_fortnight()
    print("full term amortization per fortnight:", amortization_per_fortnight)

    # estimated reduced term amortization amount per fortnight
    reduced_term_amortization_per_fortnight = mortgage.estimated_reduced_term_amortize_fortnight("n")
    print("reduced term amortization per fortnight:", reduced_term_amortization_per_fortnight)

    # calculate interest over full term in fortnights
    interest_over_full_term_fortnight = mortgage.interest_over_full_term_fortnight()
    print("interest over full term in fortnights:", interest_over_full_term_fortnight)

    principal_plus_interest = mortgage.principal_and_interest_fortnight()
    print("principal plus interest:", principal_plus_interest)

    # interest_over_reduced_term_fortnight = mortgage.interest_over_reduced_term_fortnight()
    # print("interest over reduced term in fortnights:", interest_over_reduced_term_fortnight)

    # principal_plus_interest_over_reduced_term_fortnight = mortgage.principal_plus_interest_over_reduced_term_fortnight()
    # print("Principal plus interest over reduced term in fortnights:", principal_plus_interest_over_reduced_term_fortnight)


