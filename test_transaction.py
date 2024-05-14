import pytest
from mortgage import Mortgage
from transaction import Transaction


@pytest.fixture
def default_mortgage():
    return Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                    initial_interest=4.5, initial_term=30, initial_principal=100000)


def test_update_mortgage():
    mortgage = Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                        initial_interest=5.0, initial_term=30, initial_principal=300000)

    transaction = Transaction("2024-05-20", 250000, 4.5, 25, 20, "refinancing")
    transaction.mortgage = mortgage

    transaction.update_mortgage(new_principal=250000, new_interest_rate=4.5, new_loan_term=20)

    assert mortgage.initial_principal == 250000
    assert mortgage.initial_interest == 4.5
    assert mortgage.initial_term == 20


def test_apply_transaction():
    mortgage = Mortgage(mortgage_id=1, mortgage_name="Initial Mortgage",
                        initial_interest=5.0, initial_term=30, initial_principal=300000)

    transaction = Transaction("2024-05-20", 250000, 4.5, 25, 20, "refinancing")
    transaction.mortgage = mortgage
    transaction.apply_transaction()

    assert mortgage.loan_amount == 250000
    assert mortgage.interest_rate == 4.5
    assert mortgage.loan_term == 20
    assert mortgage.extra_costs == 25
    assert mortgage.adjustment_description == "refinancing"


if __name__ == "__main__":
    pytest.main()
