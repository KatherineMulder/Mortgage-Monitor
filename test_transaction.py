import pytest
from mortgage import Mortgage
from transaction import Transaction


def test_add_mortgage():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    assert 1 in transaction_manager.mortgages
    assert transaction_manager.get_mortgage(1) == mortgage


def test_update_mortgage():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.update_mortgage(1, _initial_principal=850000, _initial_interest=0.04)

    updated_mortgage = transaction_manager.get_mortgage(1)
    assert updated_mortgage._initial_principal == 850000
    assert updated_mortgage._initial_interest == 0.04
    assert updated_mortgage.initial_payment_breakdown["total_amount_borrowed"] == 850000 - 50000 + 10000


def test_delete_mortgage():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.delete_mortgage(1)

    with pytest.raises(ValueError):
        transaction_manager.get_mortgage(1)


def test_add_existing_mortgage():
    transaction_manager = Transaction()
    mortgage1 = Mortgage()
    mortgage1.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )
    mortgage1.calculate_initial_payment_breakdown()
    mortgage1.calculate_mortgage_maturity()
    mortgage1.amortization_table()

    mortgage2 = Mortgage()
    mortgage2.gather_inputs(
        principal=900000,
        interest=0.04,
        term=25,
        extra_costs=12000,
        deposit=70000,
        payment_override_enabled=False,
        monthly_payment_override=None,
        fortnightly_payment_override=None
    )
    mortgage2.calculate_initial_payment_breakdown()
    mortgage2.calculate_mortgage_maturity()
    mortgage2.amortization_table()

    transaction_manager.add_mortgage(1, mortgage1)

    with pytest.raises(ValueError):
        transaction_manager.add_mortgage(1, mortgage2)


def test_update_non_existing_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError):
        transaction_manager.update_mortgage(1, _initial_principal=850000, _initial_interest=0.04)


def test_delete_non_existing_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError):
        transaction_manager.delete_mortgage(1)


def test_make_boom_payment():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=False,
        monthly_payment_override=None,
        fortnightly_payment_override=None
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.make_boom_payment(1, 100000)

    updated_mortgage = transaction_manager.get_mortgage(1)
    assert updated_mortgage._initial_principal == 710000  # 810000 - 100000
    assert updated_mortgage.initial_payment_breakdown["total_amount_borrowed"] == 710000 - 50000 + 10000


def test_update_payment_override():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=False,
        monthly_payment_override=None,
        fortnightly_payment_override=None
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.update_payment_override(1, 7000, None)

    updated_mortgage = transaction_manager.get_mortgage(1)
    assert updated_mortgage.monthly_payment_override == 7000
    assert updated_mortgage.payment_override_enabled is True
    assert updated_mortgage.mortgage_maturity["total_interest_saved_monthly"] > 0


def test_update_payment_override_fortnightly():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    mortgage.gather_inputs(
        principal=810000,
        interest=0.05,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=False,
        monthly_payment_override=None,
        fortnightly_payment_override=None
    )
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.update_payment_override(1, None, 3500)

    updated_mortgage = transaction_manager.get_mortgage(1)
    assert updated_mortgage.fortnightly_payment_override == 3500
    assert updated_mortgage.payment_override_enabled is True
    assert updated_mortgage.mortgage_maturity["total_interest_saved_fortnightly"] > 0


if __name__ == "__main__":
    pytest.main()
