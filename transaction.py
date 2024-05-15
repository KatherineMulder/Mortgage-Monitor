from mortgage import Mortgage
from decimal import Decimal


class Transaction:
    def __init__(self, transaction_date, new_principal, new_interest_rate, new_extra_cost, new_loan_term,
                 adjustment_description):
        self.mortgage = None
        self._transaction_date = transaction_date
        self._new_loan_amount = new_principal
        self._new_interest_rate = new_interest_rate
        self._new_extra_cost = new_extra_cost
        self._new_loan_term = new_loan_term
        self._adjustment_description = adjustment_description

    @property
    def transaction_date(self):
        return self._transaction_date

    @property
    def new_loan_amount(self):
        return self._new_loan_amount

    @property
    def new_interest_rate(self):
        return self._new_interest_rate

    @property
    def new_extra_cost(self):
        return self._new_extra_cost

    @property
    def new_loan_term(self):
        return self._new_loan_term

    @property
    def adjustment_description(self):
        return self._adjustment_description

    @transaction_date.setter
    def transaction_date(self, value):
        self._transaction_date = value

    @new_loan_amount.setter
    def new_loan_amount(self, value):
        self._new_loan_amount = value

    @new_interest_rate.setter
    def new_interest_rate(self, value):
        self._new_interest_rate = value

    @new_extra_cost.setter
    def new_extra_cost(self, value):
        self._new_extra_cost = value

    @new_loan_term.setter
    def new_loan_term(self, value):
        self._new_loan_term = value

    @adjustment_description.setter
    def adjustment_description(self, value):
        self._adjustment_description = value

    def calculate_monthly_interest(self):
        if self.mortgage:
            return self.mortgage.calculate_monthly_interest()

    def calculate_monthly_repayment(self):
        if self.mortgage:
            return self.mortgage.calculate_monthly_repayment()

    def calculate_fortnightly_interest(self):
        if self.mortgage:
            return self.mortgage.calculate_fortnightly_interest()

    def calculate_fortnightly_repayment(self):
        if self.mortgage:
            return self.mortgage.calculate_fortnightly_repayment()

    def update_mortgage(self):
        if self.mortgage:
            self.mortgage.update_mortgage(self._new_loan_amount,
                                          self._new_interest_rate,
                                          self._new_loan_term,
                                          self._new_extra_cost,
                                          self._adjustment_description)

    def __str__(self):
        return (f"Transaction Date: {self._transaction_date}, "
                f"New Loan Amount: {self._new_loan_amount}, "
                f"New Interest Rate: {self._new_interest_rate}, "
                f"New extra Cost: {self._new_extra_cost}, "
                f"New Loan Term: {self._new_loan_term}, "
                f"Adjustment Description: {self._adjustment_description}")


if __name__ == "__main__":
    print("Start Tests")

    initial_loan_amount = 100000
    initial_interest_rate = 4.5
    initial_loan_term = 30
    existing_mortgage = Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                                 initial_interest=initial_interest_rate,
                                 initial_term=initial_loan_term, initial_principal=initial_loan_amount)

    transaction_date = "2024-05-20"
    new_loan_amount = 95000
    new_interest_rate = 4.3
    new_loan_term = 25
    new_extra_cost = 500
    adjustment_description = "test"

    transaction = Transaction(transaction_date, new_loan_amount,
                              new_interest_rate, new_extra_cost,
                              new_loan_term, adjustment_description)

    transaction.mortgage = existing_mortgage
    print("Before Transaction:")
    print(existing_mortgage)
    transaction.update_mortgage()
    print("\nAfter Transaction:")
    print(existing_mortgage)
    print("\nMonthly Repayment:", existing_mortgage.calculate_monthly_repayment())
    print("Fortnightly Repayment:", existing_mortgage.calculate_fortnightly_repayment())
    print("End Tests")
