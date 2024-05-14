import pytest
from mortgage import Mortgage
from decimal import Decimal


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
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)

    # Test valid input
    mortgage.mortgage_id = 2
    assert mortgage.mortgage_id == 2

    # Test invalid input
    with pytest.raises(ValueError):
        mortgage.mortgage_id = ""


def test_set_mortgage_name():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)

    # test valid input
    mortgage.mortgage_name = "New Mortgage"
    assert mortgage.mortgage_name == "New Mortgage"

    # test invalid input
    with pytest.raises(ValueError):
        mortgage.mortgage_name = ""


def test_get_mortgage_id():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    assert mortgage.mortgage_id == 1


def test_get_mortgage_name():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    assert mortgage.mortgage_name == "test Mortgage"


# test for calculation methods
def test_calculate_monthly_interest():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    assert mortgage.calculate_monthly_interest() == 1250.00


def test_calculate_monthly_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    result = mortgage.calculate_monthly_repayment()
    expected_result = Decimal('1610.46')
    assert result == expected_result

def test_calculate_fortnightly_interest():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    expected_result = Decimal('576.92')
    assert mortgage.calculate_fortnightly_interest()

def test_calculate_fortnightly_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    result = mortgage.calculate_fortnightly_repayment()
    expected_result = Decimal('742.93')
    assert result == expected_result

def test_calculate_fortnightly_principal_repayment():
    mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
    result = mortgage.calculate_fortnightly_principal_repayment()
    expected_result = Decimal('166.01')
    assert result == expected_result


# the test code that fail to make sure that my test are working as expected
# def test_calculate_fortnightly_interest():
#     mortgage = Mortgage(1, "test Mortgage", 5.0, 30, 300000)
#     assert mortgage.calculate_fortnightly_interest() == 0  # intentionally failing the test



if __name__ == "__main__":
    pytest.main()
