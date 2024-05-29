from mortgage import Mortgage
from typing import List, Dict


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

    def initial_mortgage_setup(self, mortgage_id: int, mortgage_name: str, initial_interest: float, initial_term: int, initial_principal: float,
                               deposit: float, extra_costs: float, start_date: str, comments: str, payment_override_enabled: bool,
                               monthly_payment_override: float, fortnightly_payment_override: float):
        if mortgage_id in self.mortgages:
            raise ValueError("Mortgage ID already exists")
        mortgage = Mortgage(mortgage_name, initial_interest, initial_term, initial_principal, deposit, extra_costs, comments,
                            payment_override_enabled, monthly_payment_override, fortnightly_payment_override)
        self.mortgages[mortgage_id] = mortgage
        mortgage.calculate_initial_payment_breakdown()
        mortgage.calculate_mortgage_maturity()
        mortgage.amortization_table()
        return {
            "initial_payment_breakdown": mortgage.get_initial_payment_breakdown(),
            "mortgage_maturity_date": mortgage.mortgage_maturity,
            "amortization_table": mortgage.amortization_schedule,
            "graphical_representation": None  # Add your graphical representation logic here
        }

    def mortgage_update(self, mortgage_id: int, updated_interest_rate: float, current_principal: float, remaining_term_months: int,
                        extra_payment: float, balloon_payment: float, payment_override_enabled: bool, monthly_payment_override: float,
                        fortnightly_payment_override: float, comments: str):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        mortgage.update_mortgage(new_interest_rate=updated_interest_rate, current_principal=current_principal, remaining_term_months=remaining_term_months,
                                 extra_payment=extra_payment, updated_monthly_payment=monthly_payment_override, updated_fortnightly_payment=fortnightly_payment_override,
                                 balloon_payment=balloon_payment)
        mortgage.add_comment(comments)
        return {
            "updated_amortization_schedule": mortgage.amortization_schedule,
            "historical_transaction_tracking": mortgage.historical_transactions
        }

    def generate_planning_scenarios(self, mortgage_id: int, principal_increment: float, principal_increments: int,
                                    interest_increment: float, interest_increments: int):
        if mortgage_id not in self.mortgages:
            raise ValueError("Mortgage ID not found")
        mortgage = self.mortgages[mortgage_id]
        return mortgage.generate_planning_scenarios(principal_increment, principal_increments, interest_increment, interest_increments)
