import pytest
from transaction import Transaction
from mortgage import Mortgage

@pytest.fixture
def initial_mortgage():
    # Define the initial mortgage
    initial_loan_amount = 100000
    initial_interest_rate = 4.5
    initial_loan_term = 30
    initial_mortgage = Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                                initial_interest=initial_interest_rate,
                                initial_term=initial_loan_term, initial_principal=initial_loan_amount)
    return initial_mortgage
def test_update_mortgage(initial_mortgage):
    # Define the parameters for the transaction
    transaction_date = "2024-05-20"
    new_loan_amount = 95000
    new_interest_rate = 4.3
    new_loan_term = 25
    new_extra_cost = 500
    adjustment_description = "Refinancing"

    # Create a transaction with the given parameters and link it to the initial mortgage
    transaction = Transaction(transaction_date, new_loan_amount,
                              new_interest_rate, new_extra_cost, new_loan_term,
                              adjustment_description)
    transaction.mortgage = initial_mortgage

    # Verify that the initial mortgage's principal is correctly set
    assert initial_mortgage.initial_principal == 100000

    # Apply the transaction to update the mortgage
    transaction.update_mortgage()

    # Verify that the mortgage's attributes are updated correctly
    assert initial_mortgage.initial_principal == new_loan_amount
    assert initial_mortgage.initial_interest == new_interest_rate
    assert initial_mortgage.initial_term == new_loan_term
    assert initial_mortgage.extra_costs == new_extra_cost
    assert initial_mortgage.adjustment_description == adjustment_description

if __name__ == "__main__":
    pytest.main()
