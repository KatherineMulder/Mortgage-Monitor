from transaction import Transaction
from user import User
from mortgage import Mortgage
from database import create_database


class MortgageMonitor:
    def __init__(self, transaction_manager: Transaction):
        self.transaction_manager = transaction_manager
        self.users = {}

    def add_user(self, user: User):
        if user.user_id in self.users:
            raise ValueError("User ID already exists")
        self.users[user.user_id] = user

    def remove_user(self, user_id: int):
        if user_id not in self.users:
            raise ValueError("User ID not found")
        del self.users[user_id]

    def add_mortgage(self, user_id: int, mortgage: Mortgage):
        if user_id not in self.users:
            raise ValueError("User ID not found")
        mortgage_id = len(self.transaction_manager.mortgages) + 1
        self.transaction_manager.add_mortgage(mortgage_id, mortgage)
        self.users[user_id].initiate_mortgage({"mortgage_id": mortgage_id})

    def update_mortgage(self, user_id: int, mortgage_id: int, updated_details: dict):
        if user_id not in self.users:
            raise ValueError("User ID not found")
        if mortgage_id not in self.transaction_manager.mortgages:
            raise ValueError("Mortgage ID not found")
        self.transaction_manager.update_mortgage(mortgage_id, **updated_details)
        self.users[user_id].update_mortgage(mortgage_id, updated_details)

    def remove_mortgage(self, user_id: int, mortgage_id: int):
        if user_id not in self.users:
            raise ValueError("User ID not found")
        if mortgage_id not in self.transaction_manager.mortgages:
            raise ValueError("Mortgage ID not found")
        self.transaction_manager.delete_mortgage(mortgage_id)
        self.users[user_id].mortgages.remove(mortgage_id)

    def add_transaction(self, transaction: dict):
        user_id = transaction.get("user_id")
        if user_id not in self.users:
            raise ValueError("User ID not found")
        mortgage_id = transaction.get("mortgage_id")
        if mortgage_id not in self.transaction_manager.mortgages:
            raise ValueError("Mortgage ID not found")
        lump_sum = transaction.get("lump_sum")
        if lump_sum is not None:
            self.transaction_manager.make_balloon_payment(mortgage_id, lump_sum)

    def display_user_details(self, user_id: int):
        if user_id not in self.users:
            raise ValueError("User ID not found")
        user = self.users[user_id]
        print(f"User ID: {user.user_id}")
        print(f"Username: {user.username}")
        print(f"Mortgages: {user.mortgages}")

    def display_mortgage_details(self, mortgage_id: int):
        try:
            mortgage = self.transaction_manager.get_mortgage(mortgage_id)
            print(f"Mortgage ID: {mortgage_id}")
            print(f"Initial Principal: {mortgage.initial_principal}")
            print(f"Interest Rate: {mortgage.initial_interest}")
            print(f"Term: {mortgage.initial_term} years")
            print(f"Deposit: {mortgage.deposit}")
            print(f"Extra Costs: {mortgage.extra_costs}")
            print(f"Start Date: {mortgage.start_date}")
            print(f"Payment Override Enabled: {mortgage.payment_override_enabled}")
            if mortgage.payment_override_enabled:
                print(f"Monthly Payment Override: {mortgage.monthly_payment_override}")
                print(f"Fortnightly Payment Override: {mortgage.fortnightly_payment_override}")
        except ValueError as e:
            print(e)

    def display_all_mortgages(self):
        for mortgage_id in self.transaction_manager.mortgages:
            self.display_mortgage_details(mortgage_id)
            print("")

    def display_amortization_schedule(self, mortgage_id: int):
        try:
            mortgage = self.transaction_manager.get_mortgage(mortgage_id)
            amortization_schedule = mortgage.amortization_schedule
            print(f"Amortization Schedule for Mortgage ID: {mortgage_id} (Monthly - first 5 periods):")
            for row in amortization_schedule["monthly"][:5]:  # show first 5 data
                print(row)
            print(f"Amortization Schedule for Mortgage ID: {mortgage_id} (Fortnightly - first 5 periods):")
            for row in amortization_schedule["fortnightly"][:5]:  # show first 5 data
                print(row)
        except ValueError as e:
            print(e)

    def display_payment_breakdown(self, mortgage_id: int):
        try:
            mortgage = self.transaction_manager.get_mortgage(mortgage_id)
            breakdown = mortgage.initial_payment_breakdown
            print(f"Initial Payment Breakdown for Mortgage ID: {mortgage_id}")
            for key, value in breakdown.items():
                print(f"  {key}: {value}")
        except ValueError as e:
            print(e)

    def display_mortgage_maturity(self, mortgage_id: int):
        try:
            mortgage = self.transaction_manager.get_mortgage(mortgage_id)
            maturity = mortgage.mortgage_maturity
            print(f"Mortgage Maturity Details for Mortgage ID: {mortgage_id}")
            for key, value in maturity.items():
                print(f"  {key}: {value}")
        except ValueError as e:
            print(e)


if __name__ == "__main__":
    #  database is created and tables exist
    create_database()

    transaction_manager = Transaction()

    # create and add a user
    user = User(user_id=1, username="kat", password="password123")
    User.create_user(user.username, user.password)  # Save to the database

    monitor = MortgageMonitor(transaction_manager)
    monitor.add_user(user)

    # create and add a mortgage
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
    monitor.add_mortgage(user_id=1, mortgage=mortgage)

    # display mortgage details
    monitor.display_mortgage_details(1)
    print("")

    # display the amortization schedule
    monitor.display_amortization_schedule(1)
    print("")

    # display the payment breakdown
    monitor.display_payment_breakdown(1)
    print("")

    # display the mortgage maturity details
    monitor.display_mortgage_maturity(1)
    print("")

    # display user details
    monitor.display_user_details(1)
    print("")

    # make a balloon payment transaction
    transaction = {"user_id": 1, "mortgage_id": 1, "lump_sum": 100000}
    monitor.add_transaction(transaction)

    # Display updated mortgage details after balloon payment
    monitor.display_mortgage_details(1)
    print("")

    # remove the mortgage from the user
    monitor.remove_mortgage(user_id=1, mortgage_id=1)
    monitor.display_user_details(1)
