import pytest
from datetime import datetime
from mortgage import Mortgage
from transaction import Transaction


def create_sample_mortgage():
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
    return mortgage


def test_add_mortgage():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    assert 1 in transaction_manager.mortgages
    assert transaction_manager.mortgages[1] == mortgage


def test_add_mortgage_duplicate_id():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    with pytest.raises(ValueError, match="Mortgage ID already exists"):
        transaction_manager.add_mortgage(1, mortgage)


def test_update_mortgage():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    transaction_manager.update_mortgage(1, initial_principal=900000)
    updated_mortgage = transaction_manager.get_mortgage(1)

    assert updated_mortgage.initial_principal == 900000


def test_update_nonexistent_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError, match="Mortgage ID not found"):
        transaction_manager.update_mortgage(1, initial_principal=900000)


def test_delete_mortgage():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    transaction_manager.delete_mortgage(1)

    with pytest.raises(ValueError, match="Mortgage ID not found"):
        transaction_manager.get_mortgage(1)


def test_delete_nonexistent_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError, match="Mortgage ID not found"):
        transaction_manager.delete_mortgage(1)


def test_get_mortgage():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    retrieved_mortgage = transaction_manager.get_mortgage(1)

    assert retrieved_mortgage == mortgage


def test_get_nonexistent_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError, match="Mortgage ID not found"):
        transaction_manager.get_mortgage(1)


def test_make_balloon_payment():
    transaction_manager = Transaction()
    mortgage = create_sample_mortgage()
    transaction_manager.add_mortgage(1, mortgage)

    transaction_manager.make_balloon_payment(1, 100000)
    updated_mortgage = transaction_manager.get_mortgage(1)

    assert updated_mortgage.initial_principal == 710000  # Assuming initial_principal is reduced by 100000
    assert updated_mortgage.mortgage_maturity['monthly']['total_interest_paid'] < \
           updated_mortgage.mortgage_maturity['monthly']['interest_over_full_term']


def test_make_balloon_payment_nonexistent_mortgage():
    transaction_manager = Transaction()

    with pytest.raises(ValueError, match="Mortgage ID not found"):
        transaction_manager.make_balloon_payment(1, 100000)


def test_add_comment():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.add_comment(1, "First comment")
    comments = transaction_manager.get_comments(1)
    assert len(comments) == 1
    assert comments[0] == "First comment"


def test_add_comment_nonexistent_id():
    transaction_manager = Transaction()
    with pytest.raises(ValueError):
        transaction_manager.add_comment(1, "Comment on nonexistent mortgage")


def test_get_comments():
    transaction_manager = Transaction()
    mortgage = Mortgage()
    transaction_manager.add_mortgage(1, mortgage)
    transaction_manager.add_comment(1, "First comment")
    transaction_manager.add_comment(1, "Second comment")
    comments = transaction_manager.get_comments(1)
    assert len(comments) == 2
    assert comments[0] == "First comment"
    assert comments[1] == "Second comment"


def test_get_comments_nonexistent_id():
    transaction_manager = Transaction()
    with pytest.raises(ValueError):
        transaction_manager.get_comments(1)


if __name__ == "__main__":
    pytest.main()
