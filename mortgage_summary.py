class MortgageSummary:
    def __init__(self, loan_amount, interest_rate, loan_term, monthly_payment, total_interest_paid, remaining_balance):
        self._loan_amount = loan_amount
        self._interest_rate = interest_rate
        self._loan_term = loan_term
        self._monthly_payment = monthly_payment
        self._total_interest_paid = total_interest_paid
        self._remaining_balance = remaining_balance

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
        update the summary based on any changes made to the mortgage.
        """
        self._total_interest_paid = mortgage.calculate_total_interest()
        self._remaining_balance = mortgage.calculate_remaining_balance()

    @staticmethod
    def calculate_total_interest(self, mortgage):
        """
        calculate the total interest paid over the life of the loan.
        """
        return mortgage.calculate_total_interest()

    @staticmethod
    def calculate_remaining_balance(self, mortgage):
        """
        calculate the remaining balance of the loan after a certain period.
        """
        return mortgage.calculate_remaining_balance()

    def generate_summary(self, mortgage):
        """
        generate a summary of the mortgage analysis based on the current mortgage information.
        need to expend more?
        """
        self._monthly_payment = mortgage.calculate_monthly_payment()

# TODO could validate that the loan amount, interest rate, and loan term are within acceptable ranges.
# TODO error handling
# TODO Amortization Schedule
# TODO Visualization
