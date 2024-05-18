from mortgage import Mortgage


class Transaction:
    def __init__(self):
        self.mortgages = {}

    def add_mortgage(self, mortgage_id: int, mortgage: Mortgage):
        if mortgage_id in self.mortgages:
            raise ValueError("Mortgage ID already exists")
        self.mortgages[mortgage_id] = mortgage

    def update_mortgage(self, mortgage_id: int, **kwargs):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        mortgage.update_mortgage(**kwargs)

    def delete_mortgage(self, mortgage_id: int):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        del self.mortgages[mortgage_id]

    def get_mortgage(self, mortgage_id: int) -> Mortgage:
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        return self.mortgages[mortgage_id]

    def make_balloon_payment(self, mortgage_id: int, lump_sum: float):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        mortgage.make_balloon_payment(lump_sum)

    def add_comment(self, mortgage_id: int, comment: str):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        mortgage.add_comment(comment)

    def get_comments(self, mortgage_id: int):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        return mortgage.get_comments()


if __name__ == "__main__":
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

    # add the mortgage to the transaction manager
    transaction_manager.add_mortgage(1, mortgage)

    # balloon pay extra for 100000
    transaction_manager.make_balloon_payment(1, 100000)
    updated_mortgage = transaction_manager.get_mortgage(1)
    print("Updated Mortgage Details After Balloon Payment:")
    for key, value in updated_mortgage.mortgage_maturity.items():
        print(f"  {key}: {value}")

    # add a comment to the mortgage
    transaction_manager.add_comment(1, "initial mortgage setup completed.")
    transaction_manager.add_comment(1, "first payment made.")

    # retrieve and display comments
    comments = transaction_manager.get_comments(1)
    print("Comments on Mortgage ID 1:")
    for comment in comments:
        print(comment)

    transaction_manager.delete_mortgage(1)
    try:
        deleted_mortgage = transaction_manager.get_mortgage(1)
    except ValueError as e:
        print(e)
