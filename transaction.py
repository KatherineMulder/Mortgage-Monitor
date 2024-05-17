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

   # add
    transaction_manager.add_mortgage(1, mortgage)

    # make balloon
    transaction_manager.make_balloon_payment(1, 100000)
    updated_mortgage = transaction_manager.get_mortgage(1)
    print("Updated Mortgage Details After Boom Payment:")
    for key, value in updated_mortgage.mortgage_maturity.items():
        print(f"  {key}: {value}")

    # Delete the mortgage
    transaction_manager.delete_mortgage(1)
    try:
        deleted_mortgage = transaction_manager.get_mortgage(1)
    except ValueError as e:
        print(e)  # Expected output: Mortgage ID not found
