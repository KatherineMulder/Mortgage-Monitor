from datetime import datetime
from typing import Optional
from mortgage import Mortgage


def update_mortgage(mortgage: Mortgage, new_interest_rate: Optional[float] = None,
                    monthly_payment_override: Optional[float] = None, extra_costs: Optional[float] = None,
                    balloon_payment: Optional[float] = None, comments: Optional[str] = None):
    transaction_date = datetime.now()

    print(f"Before update: principal={mortgage.initial_principal}, interest={mortgage.initial_interest}, extra_costs={mortgage.extra_costs}")

    if new_interest_rate is not None:
        mortgage.initial_interest = new_interest_rate  # Use property setter

    if monthly_payment_override is not None:
        mortgage.monthly_payment_override = monthly_payment_override
        mortgage.payment_override_enabled = True

    if balloon_payment is not None:
        print(f"Making balloon payment: {balloon_payment}")
        mortgage.initial_principal -= balloon_payment

    if extra_costs is not None:
        print(f"Adding extra costs: {extra_costs}")
        mortgage.initial_principal += extra_costs
        mortgage.extra_costs += extra_costs

    if comments is not None:
        print(f"Updating comments: {comments}")
        mortgage._comments = comments

    print(f"After applying extra costs and balloon payment: principal={mortgage.initial_principal}, extra_costs={mortgage.extra_costs}")

    # Recalculate mortgage
    mortgage.calculate_initial_payment_breakdown()
    mortgage.calculate_mortgage_maturity()
    mortgage.amortization_table()

    print(f"After update: principal={mortgage.initial_principal}, interest={mortgage.initial_interest}, extra_costs={mortgage.extra_costs}")

    # Log the transaction
    transaction = {
        "datetime": transaction_date,
        "updated_principal": mortgage.initial_principal,
        "new_interest_rate": mortgage.initial_interest,
        "new_payment_monthly": mortgage.initial_payment_breakdown.get("total_repayment_monthly"),
        "new_payment_fortnightly": mortgage.initial_payment_breakdown.get("total_repayment_fortnightly"),
        "comments": mortgage._comments,
    }
    mortgage.transaction_logs.append(transaction)


if __name__ == "__main__":
    M = Mortgage("Test Mortgage", 5, 20, 810000, 50000, 10000, "Initial setup")
    try:
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
        print("Initial Payment Breakdown:")
        for key, value in M.get_initial_payment_breakdown().items():
            print(f"{key}: {value}")
        print()

        M.calculate_mortgage_maturity()
        print("Mortgage Maturity Details:")
        for key, value in M.mortgage_maturity.items():
            print(f"{key}: {value}")
        print()

        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:
            print(row)

        print("\nMaking Balloon Payment of 100000")
        M.make_balloon_payment(100000)
        print(f"Principal after balloon payment: {M.initial_principal}")

        print(f"Extra costs before update: {M.extra_costs}")
        update_mortgage(M, new_interest_rate=3.5, monthly_payment_override=4500, extra_costs=5000)
        print("\nAfter Mortgage Update:")
        print(f"Principal after update: {M.initial_principal}")
        print(f"Extra costs after update: {M.extra_costs}")
        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:
            print(row)

        expected_principal = 810000 - 100000 + 5000
        print(f"Expected principal: {expected_principal}")
        assert M.initial_principal == expected_principal, f"Expected principal: {expected_principal}, got: {M.initial_principal}"
        assert M.initial_interest == 0.035
        assert M.initial_term == 20

        last_transaction = M.transaction_logs[-1]
        assert last_transaction["updated_principal"] == expected_principal
        assert last_transaction["new_interest_rate"] == 0.035
        assert last_transaction["new_payment_monthly"] == M.initial_payment_breakdown["total_repayment_monthly"]
        assert last_transaction["new_payment_fortnightly"] == M.initial_payment_breakdown["total_repayment_fortnightly"]

        print("All tests passed!")

    except ValueError as e:
        print(f"Error: {e}")
