import pytest
from mortgage import Mortgage

@pytest.fixture
def mortgage_n():
    return Mortgage(payment_override_enabled="n",
                    monthly_payment_override=None,
                    fortnightly_payment_override=None,
                    comments=None)

@pytest.fixture
def mortgage_y():
    return Mortgage(payment_override_enabled="y",
                    monthly_payment_override="2000",
                    fortnightly_payment_override="1000",
                    comments=None)

def test_initial_payment_breakdown_n(mortgage_n):
    mortgage_n.mortgage_id = 1
    mortgage_n.mortgage_name = "test Mortgage (n)"
    mortgage_n.initial_interest = 3.5
    mortgage_n.initial_term = 25
    mortgage_n.initial_principal = 300000
    mortgage_n.deposit = 50000
    mortgage_n.extra_costs = 10000

    breakdown = mortgage_n.calculate_initial_payment_breakdown()

    assert breakdown["total_amount_borrow"] == 260000.0
    assert breakdown["monthly_interest"] > 0
    assert breakdown["estimated_monthly_repayment"] > 0
    assert breakdown["monthly_principal_repayment"] > 0
    assert breakdown["fortnightly_interest"] > 0
    assert breakdown["estimated_fortnightly_repayment"] > 0
    assert breakdown["fortnightly_principal_repayment"] > 0
    assert breakdown["estimated_monthly_repayment_plus"] > 0
    assert breakdown["estimated_monthly_repayment_minus"] > 0
    assert breakdown["estimated_fortnightly_repayment_plus"] > 0
    assert breakdown["estimated_fortnightly_repayment_minus"] > 0
    assert breakdown["initial_extra"] == 0
    assert breakdown["repayment"] > 0
    assert breakdown["fortnightly_extra"] == 0
    assert breakdown["fortnightly_repayment"] > 0

def test_initial_payment_breakdown_y(mortgage_y):
    mortgage_y.mortgage_id = 2
    mortgage_y.mortgage_name = "test Mortgage (y)"
    mortgage_y.initial_interest = 3.5
    mortgage_y.initial_term = 25
    mortgage_y.initial_principal = 300000
    mortgage_y.deposit = 50000
    mortgage_y.extra_costs = 10000
    breakdown = mortgage_y.calculate_initial_payment_breakdown()

    assert breakdown["total_amount_borrow"] == 260000.0
    assert breakdown["monthly_interest"] > 0
    assert breakdown["estimated_monthly_repayment"] > 0
    assert breakdown["monthly_principal_repayment"] > 0
    assert breakdown["fortnightly_interest"] > 0
    assert breakdown["estimated_fortnightly_repayment"] > 0
    assert breakdown["fortnightly_principal_repayment"] > 0
    assert breakdown["estimated_monthly_repayment_plus"] > 0
    assert breakdown["estimated_monthly_repayment_minus"] > 0
    assert breakdown["estimated_fortnightly_repayment_plus"] > 0
    assert breakdown["estimated_fortnightly_repayment_minus"] > 0
    assert breakdown["initial_extra"] > 0
    assert breakdown["repayment"] > 0
    assert breakdown["fortnightly_extra"] > 0
    assert breakdown["fortnightly_repayment"] > 0

def test_amortization_schedule_n(mortgage_n):
    mortgage_n.mortgage_id = 1
    mortgage_n.mortgage_name = "test Mortgage (n)"
    mortgage_n.initial_interest = 3.5
    mortgage_n.initial_term = 25
    mortgage_n.initial_principal = 300000
    mortgage_n.deposit = 50000
    mortgage_n.extra_costs = 10000

    amortization_schedule = mortgage_n.calculate_amortization_schedule()

    assert len(amortization_schedule) > 0
    assert amortization_schedule[-1]["balance"] == 0

def test_amortization_schedule_y(mortgage_y):
    mortgage_y.mortgage_id = 2
    mortgage_y.mortgage_name = "test Mortgage (y)"
    mortgage_y.initial_interest = 3.5
    mortgage_y.initial_term = 25
    mortgage_y.initial_principal = 300000
    mortgage_y.deposit = 50000
    mortgage_y.extra_costs = 10000

    amortization_schedule = mortgage_y.calculate_amortization_schedule()

    assert len(amortization_schedule) > 0
    assert amortization_schedule[-1]["balance"] == 0

def test_mortgage_maturity_n(mortgage_n):
    mortgage_n.mortgage_id = 1
    mortgage_n.mortgage_name = "test Mortgage (n)"
    mortgage_n.initial_interest = 3.5
    mortgage_n.initial_term = 25
    mortgage_n.initial_principal = 300000
    mortgage_n.deposit = 50000
    mortgage_n.extra_costs = 10000

    mortgage_n.calculate_initial_payment_breakdown()
    maturity = mortgage_n.calculate_mortgage_maturity()

    assert maturity["payment_overfull_term"] == 25 * 26
    assert maturity["full_term_amortize"] == 25
    assert maturity["estimated_reduced_term_to_amortize"] <= 25
    assert maturity["interest_over_full_term_plus"] > 0
    assert maturity["interest_over_full_term_minus"] > 0
    assert maturity["principle_plus_interest"] > 0
    assert maturity["interest_over_reduced_term"] == 0
    assert maturity["interest_saved_over_reduced_term"] == 0
    assert maturity["principle_plus_interest_over_reduced_term"] == 0

def test_mortgage_maturity_y(mortgage_y):
    mortgage_y.mortgage_id = 2
    mortgage_y.mortgage_name = "test Mortgage (y)"
    mortgage_y.initial_interest = 3.5
    mortgage_y.initial_term = 25
    mortgage_y.initial_principal = 300000
    mortgage_y.deposit = 50000
    mortgage_y.extra_costs = 10000

    mortgage_y.calculate_initial_payment_breakdown()
    maturity = mortgage_y.calculate_mortgage_maturity()

    assert maturity["payment_overfull_term"] == 25 * 26
    assert maturity["full_term_amortize"] == 25
    assert maturity["estimated_reduced_term_to_amortize"] <= 25
    assert maturity["interest_over_full_term_plus"] > 0
    assert maturity["interest_over_full_term_minus"] > 0
    assert maturity["principle_plus_interest"] > 0
    assert maturity["interest_over_reduced_term"] > 0
    assert maturity["interest_saved_over_reduced_term"] > 0
    assert maturity["principle_plus_interest_over_reduced_term"] > 0

if __name__ == "__main__":
    pytest.main()
