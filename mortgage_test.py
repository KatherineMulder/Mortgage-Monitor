import pytest
from datetime import datetime
from mortgage import Mortgage


def test_mortgage_initialization():
    mortgage = Mortgage()
    assert mortgage._mortgage_id is None
    assert mortgage._mortgage_name == ""
    assert mortgage._initial_interest == 0.0
    assert mortgage._initial_term == 0
    assert mortgage._initial_principal == 0.0
    assert mortgage._deposit == 0.0
    assert mortgage._extra_costs == 0.0
    assert isinstance(mortgage._start_date, datetime)
    assert mortgage._comments == []
    assert mortgage.payment_override_enabled is False
    assert mortgage.monthly_payment_override is None
    assert mortgage.fortnightly_payment_override is None


def test_mortgage_id():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.mortgage_id = -1
    with pytest.raises(ValueError):
        mortgage.mortgage_id = "one"
    mortgage.mortgage_id = 1
    assert mortgage.mortgage_id == 1


def test_mortgage_name():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.mortgage_name = ""
    with pytest.raises(ValueError):
        mortgage.mortgage_name = 123
    mortgage.mortgage_name = "Home Loan"
    assert mortgage.mortgage_name == "Home Loan"


def test_initial_interest():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.initial_interest = -1
    with pytest.raises(ValueError):
        mortgage.initial_interest = "five"
    mortgage.initial_interest = 0.05
    assert mortgage.initial_interest == 0.05


def test_initial_term():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.initial_term = 0
    with pytest.raises(ValueError):
        mortgage.initial_term = 31
    with pytest.raises(ValueError):
        mortgage.initial_term = "twenty"
    mortgage.initial_term = 20
    assert mortgage.initial_term == 20


def test_initial_principal():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.initial_principal = 0
    with pytest.raises(ValueError):
        mortgage.initial_principal = -100000
    with pytest.raises(ValueError):
        mortgage.initial_principal = "hundred thousand"
    mortgage.initial_principal = 100000
    assert mortgage.initial_principal == 100000


def test_deposit():
    mortgage = Mortgage()
    mortgage.initial_principal = 100000
    with pytest.raises(ValueError):
        mortgage.deposit = -1000
    with pytest.raises(ValueError):
        mortgage.deposit = 150000
    with pytest.raises(ValueError):
        mortgage.deposit = "ten thousand"
    mortgage.deposit = 10000
    assert mortgage.deposit == 10000


def test_extra_costs():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.extra_costs = -500
    with pytest.raises(ValueError):
        mortgage.extra_costs = "five hundred"
    mortgage.extra_costs = 500
    assert mortgage.extra_costs == 500


def test_start_date():
    mortgage = Mortgage()
    with pytest.raises(ValueError):
        mortgage.start_date = "2022-01-01"
    new_date = datetime(2023, 1, 1)
    mortgage.start_date = new_date
    assert mortgage.start_date == new_date


def test_calculate_initial_payment_breakdown():
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=0,
        deposit=0,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    breakdown = mortgage.initial_payment_breakdown
    assert isinstance(breakdown, dict)
    assert "total_amount_borrowed" in breakdown
    assert "estimated_repayment_monthly" in breakdown
    assert "estimated_repayment_fortnightly" in breakdown


def test_calculate_mortgage_maturity():
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=0,
        deposit=0,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    maturity = mortgage.mortgage_maturity
    assert isinstance(maturity, dict)
    assert "monthly" in maturity
    assert "fortnightly" in maturity


def test_create_amortization_table():
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=0,
        deposit=0,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    amortization_schedule = mortgage.amortization_table()
    assert isinstance(amortization_schedule, dict)
    assert "monthly" in amortization_schedule
    assert "fortnightly" in amortization_schedule
    assert len(amortization_schedule["monthly"]) > 0
    assert len(amortization_schedule["fortnightly"]) > 0