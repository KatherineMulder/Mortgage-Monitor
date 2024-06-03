import pytest
from datetime import datetime, timedelta
from mortgage import Mortgage


def test_mortgage_initialization():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )

    assert mortgage.mortgage_name == "Test Mortgage"
    assert mortgage.initial_interest == 0.05
    assert mortgage.initial_term == 20
    assert mortgage.initial_principal == 810000
    assert mortgage.deposit == 50000
    assert mortgage.extra_costs == 10000
    assert mortgage._comments == "initial setup"


def test_gather_inputs():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.gather_inputs(
        principal=820000,
        interest=4.5,
        term=25,
        extra_costs=15000,
        deposit=60000,
        payment_override_enabled=True,
        monthly_payment_override=3000,
        fortnightly_payment_override=1500
    )

    assert mortgage.initial_principal == 820000
    assert mortgage.initial_interest == 0.045
    assert mortgage.initial_term == 25
    assert mortgage.extra_costs == 15000
    assert mortgage.deposit == 60000
    assert mortgage.payment_override_enabled is True
    assert mortgage.monthly_payment_override == 3000
    assert mortgage.fortnightly_payment_override == 1500


def test_calculate_projected_payment():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    monthly_payment = mortgage.calculate_projected_payment(810000, 5, 20, "monthly")
    fortnightly_payment = mortgage.calculate_projected_payment(810000, 5, 20, "fortnightly")

    assert monthly_payment > 0
    assert fortnightly_payment > 0


def test_calculate_initial_payment_breakdown():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()
    breakdown = mortgage.get_initial_payment_breakdown()

    assert breakdown["total_amount_borrowed"] == 770000


def test_make_balloon_payment():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.make_balloon_payment(100000)

    assert mortgage.initial_principal == 710000


def test_apply_extra_costs():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.apply_extra_costs(5000)

    assert mortgage.initial_principal == 815000


def test_add_comments():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.add_comments("Added a comment")
    comments = mortgage.get_comments()

    assert "Added a comment" in comments


def test_amortization_table():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()
    amortization_schedule = mortgage.amortization_table()

    assert len(amortization_schedule["monthly"]) > 0
    assert len(amortization_schedule["fortnightly"]) > 0


def test_add_interest_rate_change():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    new_rate = 4.5
    effective_date = datetime.now() + timedelta(days=365)
    mortgage.add_interest_rate_change(new_rate, effective_date)

    assert len(mortgage.interest_rate_changes) == 1
    assert mortgage.interest_rate_changes[0]["new_interest_rate"] == new_rate
    assert mortgage.interest_rate_changes[0]["effective_date"] == effective_date


def test_invalid_start_date():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )

    with pytest.raises(ValueError):
        mortgage.start_date = "invalid_date"


def test_invalid_mortgage_id():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )

    with pytest.raises(ValueError):
        mortgage.mortgage_id = -1


def test_generate_planning_scenarios():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    scenarios = mortgage.generate_planning_scenarios(
        principal_increment=3000.00,
        principal_increments=15,
        interest_increment=0.25,
        interest_increments=15
    )

    assert len(scenarios) == 16
    assert "monthly_payments" in scenarios[0]
    assert "fortnightly_payments" in scenarios[0]


def test_calculate_mortgage_maturity():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()

    maturity = mortgage.mortgage_maturity
    assert "monthly" in maturity
    assert "fortnightly" in maturity
    assert maturity["monthly"]["full_term_payments"] > 0
    assert maturity["fortnightly"]["full_term_payments"] > 0


def test_make_balloon_payment_invalid_amount():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()

    with pytest.raises(ValueError):
        mortgage.make_balloon_payment(-50000)

    with pytest.raises(ValueError):
        mortgage.make_balloon_payment(900000)


def test_apply_extra_costs_invalid_amount():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.calculate_initial_payment_breakdown()

    with pytest.raises(ValueError):
        mortgage.apply_extra_costs(-5000)


def test_start_date_property():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    new_date = datetime.now() + timedelta(days=365)
    mortgage.start_date = new_date

    assert mortgage.start_date == new_date


def test_mortgage_id_property():
    mortgage = Mortgage(
        mortgage_name="Test Mortgage",
        initial_interest=5.0,
        initial_term=20,
        initial_principal=810000,
        deposit=50000,
        extra_costs=10000,
        comments="initial setup"
    )
    mortgage.mortgage_id = 123

    assert mortgage.mortgage_id == 123
