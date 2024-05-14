from decimal import Decimal
from mortgage import Mortgage


class MortgageSummary:
    def __init__(self, loan_amount, interest_rate, loan_term):
        self._loan_amount = loan_amount
        self._interest_rate = interest_rate
        self._loan_term = loan_term
        self._monthly_payment = None
        self._total_interest_paid = None
        self._remaining_balance = None

    @property
    def loan_amount(self):
        return self._loan_amount

    @loan_amount.setter
    def loan_amount(self, value):
        self._loan_amount = value

    @property
    def interest_rate(self):
        return self._interest_rate

    @interest_rate.setter
    def interest_rate(self, value):
        self._interest_rate = value

    @property
    def loan_term(self):
        return self._loan_term

    @loan_term.setter
    def loan_term(self, value):
        self._loan_term = value

    @property
    def monthly_payment(self):
        return self._monthly_payment

    @monthly_payment.setter
    def monthly_payment(self, value):
        self._monthly_payment = value

    @property
    def total_interest_paid(self):
        return self._total_interest_paid

    @total_interest_paid.setter
    def total_interest_paid(self, value):
        self._total_interest_paid = value

    @property
    def remaining_balance(self):
        return self._remaining_balance

    @remaining_balance.setter
    def remaining_balance(self, value):
        self._remaining_balance = value

    def update_summary(self, mortgage):
        """
        Update the summary based on any changes made to the mortgage.
        """
        self._total_interest_paid = mortgage.calculate_monthly_interest()
        self._remaining_balance = mortgage.calculate_remaining_balance_monthly()

    def generate_summary(self, mortgage):
        """
        Generate a summary of the mortgage analysis based on the current mortgage information.
        """
        self._monthly_payment = mortgage.calculate_monthly_payment()


if __name__ == "__main__":
    print("Start Tests")

    # Initial mortgage object
    initial_loan_amount = Decimal('100000')
    initial_interest_rate = Decimal('4.5')
    initial_loan_term = 30
    existing_mortgage = Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                                 initial_interest=initial_interest_rate,
                                 initial_term=initial_loan_term, initial_principal=initial_loan_amount)


    summary = MortgageSummary(loan_amount=initial_loan_amount, interest_rate=initial_interest_rate,
                              loan_term=initial_loan_term)


    summary.update_summary(existing_mortgage)

    print("Mortgage Summary:")
    print(f"Loan Amount: {summary.loan_amount}")
    print(f"Interest Rate: {summary.interest_rate}")
    print(f"Loan Term: {summary.loan_term}")
    print(f"Monthly Payment: {summary.monthly_payment}")
    print(f"Total Interest Paid: {summary.total_interest_paid}")
    print(f"Remaining Balance: {summary.remaining_balance}")
    print("End Tests")


# TODO reminding monthly and fornightly needs update