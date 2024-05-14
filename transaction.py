class Transaction:
    def __init__(self, transaction_date, new_loan_amount, new_interest_rate, new_loan_term, adjustment_description):
        self._transaction_type = None
        self._transaction_date = transaction_date
        self._new_loan_amount = new_loan_amount
        self._new_interest_rate = new_interest_rate
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

    @new_loan_term.setter
    def new_loan_term(self, value):
        self._new_loan_term = value

    @adjustment_description.setter
    def adjustment_description(self, value):
        self._adjustment_description = value

    def update_loan_amount(self, mortgage):
        mortgage.loan_amount = self._new_loan_amount

    def update_interest_rate(self, mortgage):
        mortgage.interest_rate = self._new_interest_rate

    def update_loan_term(self, mortgage):
        mortgage.loan_term = self._new_loan_term

    def update_adjustment_description(self, mortgage):
        """
        Updates the adjustment description of the mortgage based on the transaction.
        """
        mortgage.adjustment_description = self._adjustment_description

    def apply_transaction(self, mortgage):
        if self._transaction_type == "Loan Amount Change":
            self.update_loan_amount(mortgage)
        elif self._transaction_type == "Interest Rate Change":
            self.update_interest_rate(mortgage)
        elif self._transaction_type == "Loan Term Change":
            self.update_loan_term(mortgage)

    def __str__(self):
        return f"Transaction Date: {self._transaction_date}, New Loan Amount: {self._new_loan_amount}, New Interest Rate: {self._new_interest_rate}, New Loan Term: {self._new_loan_term}, Adjustment Description: {self._adjustment_description}"
