import pytest
from mortgage import Mortgage
from decimal import Decimal

@pytest.fixture
def default_mortgage():
    return Mortgage(
        mortgage_id=1,
        mortgage_name="Initial Mortgage",
        initial_interest=4.5,
        initial_term=30,
        initial_principal=100000
    )


def test_total_loan_amount():
    mortgage = Mortgage(
        mortgage_id=1,
        mortgage_name="test Mortgage",
        initial_interest=5.0,
        initial_term=30,
        initial_principal=300000,
        deposit=5000,
        extra_costs=1000
    )
    assert mortgage.total_loan_amount() == 296000


def test_set_mortgage_id():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)

    mortgage.mortgage_id = 2
    assert mortgage.mortgage_id == 2

    with pytest.raises(ValueError):
        mortgage.mortgage_id = ""


def test_set_mortgage_name():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)

    # test valid input
    mortgage.mortgage_name = "New Mortgage"
    assert mortgage.mortgage_name == "New Mortgage"

    # test invalid input
    with pytest.raises(ValueError):
        mortgage.mortgage_name = ""


def test_get_mortgage_id():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    assert mortgage.mortgage_id == 1


def test_get_mortgage_name():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    assert mortgage.mortgage_name == "test Mortgage"


# test for calculation methods
def test_calculate_monthly_interest():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    assert mortgage.calculate_monthly_interest() == 1250.00


def test_calculate_monthly_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    result = mortgage.calculate_monthly_repayment()
    expected_result = Decimal('1610.46')
    assert result == expected_result


def test_calculate_fortnightly_interest():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    expected_result = Decimal('576.92')
    assert mortgage.calculate_fortnightly_interest() == expected_result


def test_calculate_fortnightly_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    result = mortgage.calculate_fortnightly_repayment()
    expected_result = Decimal('742.93')
    assert result == expected_result


def test_calculate_fortnightly_principal_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    result = mortgage.calculate_fortnightly_principal_repayment()
    expected_result = Decimal('166.01')
    assert result == expected_result


def test_calculate_remaining_balance_fortnightly():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    fortnights_paid = 0
    expected_result = 300000
    assert mortgage.calculate_remaining_balance_fortnightly(fortnights_paid) == expected_result


def test_calculate_remaining_balance_monthly():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    months_paid = 24

    monthly_interest_rate = mortgage.initial_interest / 12 / 100
    total_payments = mortgage.initial_term * 12
    monthly_payment = (mortgage.initial_principal * monthly_interest_rate) / (
            1 - (1 + monthly_interest_rate) ** -total_payments)
    total_paid = monthly_payment * months_paid
    expected_result = mortgage.initial_principal - total_paid

    assert mortgage.calculate_remaining_balance_monthly(months_paid) == round(expected_result, 2)


# TODO do more testings for this
def test_calculate_remaining_balance():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000, deposit=0, extra_costs=0)
    payments_paid = 24  # Assuming 24 payments have been made

    expected_result = {
        'monthly': 260142.68,
        'fortnightly': 281924.17
    }

    actual_result = mortgage.calculate_remaining_balance(payments_paid)
    print("Actual Result:", actual_result)
    print("Expected Result:", expected_result)

    assert actual_result == expected_result


# the test code that fail to make sure that my test are working as expected
# def test_calculate_fortnightly_interest():
#     mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
#     assert mortgage.calculate_fortnightly_interest() == 0  # intentionally failing the test

if __name__ == "__main__":
    pytest.main()
