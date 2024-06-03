import pytest
from mortgage import Mortgage
from update_mortgage import update_mortgage


def test_update_mortgage():
    M = Mortgage("Test Mortgage", 5, 20, 810000, 50000, 10000, "Initial setup")
    M.gather_inputs(
        principal=810000,
        interest=5,
        term=20,
        extra_costs=10000,
        deposit=50000,
        payment_override_enabled=True,
        monthly_payment_override=6000,
        fortnightly_payment_override=3000
    )

    M.calculate_initial_payment_breakdown()
    M.calculate_mortgage_maturity()
    M.amortization_table()

    M.make_balloon_payment(100000)

    update_mortgage(M, new_interest_rate=3.5, monthly_payment_override=4500, extra_costs=5000)

    expected_principal = 810000 - 100000 + 5000

    assert M.initial_principal == expected_principal, f"Expected principal: {expected_principal}, got: {M.initial_principal}"
    assert M.initial_interest == 0.035
    assert M.initial_term == 20  # same term

    last_transaction = M.transaction_logs[-1]
    assert last_transaction["updated_principal"] == expected_principal
    assert last_transaction["new_interest_rate"] == 0.035
    assert last_transaction["new_payment_monthly"] == M.initial_payment_breakdown["total_repayment_monthly"]
    assert last_transaction["new_payment_fortnightly"] == M.initial_payment_breakdown["total_repayment_fortnightly"]


if __name__ == "__main__":
    pytest.main()
