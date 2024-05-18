from datetime import datetime
from typing import List, Optional, Dict


class Mortgage:
    def __init__(self,
                 comments: Optional[List[str]] = None,
                 payment_override_enabled: bool = False,
                 monthly_payment_override: Optional[float] = None,
                 fortnightly_payment_override: Optional[float] = None):
        self._mortgage_id: Optional[int] = None
        self._mortgage_name: str = ""
        self._initial_interest: float = 0.0
        self._initial_term: int = 0
        self._initial_principal: float = 0.0
        self._deposit: float = 0.0
        self._extra_costs: float = 0.0
        self._start_date: datetime = datetime.now()
        self._comments: List[str] = comments if comments else []
        self.payment_override_enabled: bool = payment_override_enabled
        self.monthly_payment_override: Optional[float] = monthly_payment_override
        self.fortnightly_payment_override: Optional[float] = fortnightly_payment_override
        self.initial_payment_breakdown: Dict = {}
        self.mortgage_maturity: Dict = {}
        self.amortization_schedule: Dict[str, List[Dict[str, float]]] = {}

    @property
    def mortgage_id(self) -> Optional[int]:
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, value: int) -> None:
        if value is None or not isinstance(value, int):
            raise ValueError("mortgage ID must be an integer")
        if value < 0:
            raise ValueError("mortgage ID cannot be negative")
        self._mortgage_id = value

    @property
    def mortgage_name(self) -> str:
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, value: str) -> None:
        if value is None or not isinstance(value, str):
            raise ValueError("mortgage name must be a string")
        if not value:
            raise ValueError("mortgage name cannot be empty")
        self._mortgage_name = value

    @property
    def initial_interest(self) -> float:
        return self._initial_interest

    @initial_interest.setter
    def initial_interest(self, value: float) -> None:
        if value is None or not isinstance(value, (float, int)):
            raise ValueError("initial interest must be a numeric value")
        if value < 0:
            raise ValueError("initial interest cannot be negative")
        self._initial_interest = float(value)

    @property
    def initial_term(self) -> int:
        return self._initial_term

    @initial_term.setter
    def initial_term(self, value: int) -> None:
        if value is None or not isinstance(value, int):
            raise ValueError("initial term must be an integer")
        if value <= 0:
            raise ValueError("initial term must be greater than zero")
        if value > 30:
            raise ValueError("maximum initial term is 30 years")
        self._initial_term = value

    @property
    def initial_principal(self) -> float:
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("initial principal must be a number")
        if value <= 0:
            raise ValueError("initial principal must be greater than zero")
        self._initial_principal = value

    @property
    def deposit(self) -> float:
        return self._deposit

    @deposit.setter
    def deposit(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("deposit must be a number")
        if value < 0:
            raise ValueError("deposit cannot be negative")
        if value > self._initial_principal:
            raise ValueError("deposit cannot be greater than the initial principal")
        self._deposit = value

    @property
    def extra_costs(self) -> float:
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("extra costs must be a number")
        if value < 0:
            raise ValueError("extra costs cannot be negative")
        self._extra_costs = value

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        if value is None or not isinstance(value, datetime):
            raise ValueError("start date must be a datetime object")
        self._start_date = value

    def gather_inputs(self, principal: float, interest: float, term: int, extra_costs: float, deposit: float,
                      payment_override_enabled: bool, monthly_payment_override: Optional[float],
                      fortnightly_payment_override: Optional[float]):
        self._initial_principal = principal
        self._initial_interest = interest
        self._initial_term = term
        self._extra_costs = extra_costs
        self._deposit = deposit
        self.payment_override_enabled = payment_override_enabled
        self.monthly_payment_override = monthly_payment_override
        self.fortnightly_payment_override = fortnightly_payment_override

    def update_mortgage(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, f"_{key}"):
                setattr(self, f"_{key}", value)
            elif hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Invalid attribute: {key}")

        # recalculate
        self.calculate_initial_payment_breakdown()
        self.calculate_mortgage_maturity()
        self.amortization_table()

    def delete_mortgage(self):
        """delete the mortgage by resetting all attributes."""
        self.__init__()

    def make_balloon_payment(self, lump_sum: float):
        if lump_sum <= 0:
            raise ValueError("Lump sum payment must be greater than zero")
        if lump_sum > self._initial_principal:
            raise ValueError("Lump sum payment cannot be greater than the remaining principal")
        self._initial_principal -= lump_sum
        self.calculate_initial_payment_breakdown()
        self.calculate_mortgage_maturity()
        self.amortization_table()

    def calculate_initial_payment_breakdown(self):
        principal = self._initial_principal
        interest = self._initial_interest
        term = self._initial_term
        extra_costs = self._extra_costs
        deposit = self._deposit
        payment_override_enabled = self.payment_override_enabled
        monthly_payment_override = self.monthly_payment_override
        fortnightly_payment_override = self.fortnightly_payment_override

        # add total amount for input deposit and extra costs
        total_amount_borrowed = principal - deposit + extra_costs

        monthly_rate = interest / 12
        estimated_repayment_monthly = total_amount_borrowed * (monthly_rate / (1 - (1 + monthly_rate) ** -(term * 12)))
        initial_interest_monthly = total_amount_borrowed * monthly_rate
        initial_principal_monthly = estimated_repayment_monthly - initial_interest_monthly
        initial_extra_monthly = monthly_payment_override - initial_interest_monthly if payment_override_enabled else 0
        total_repayment_monthly = initial_interest_monthly + initial_principal_monthly + initial_extra_monthly

        fortnightly_rate = interest / 26
        estimated_repayment_fortnightly = total_amount_borrowed * (
                fortnightly_rate / (1 - (1 + fortnightly_rate) ** -(term * 26)))
        initial_interest_fortnightly = total_amount_borrowed * fortnightly_rate
        initial_principal_fortnightly = estimated_repayment_fortnightly - initial_interest_fortnightly
        initial_extra_fortnightly = fortnightly_payment_override - initial_interest_fortnightly \
            if payment_override_enabled else 0
        total_repayment_fortnightly = (initial_interest_fortnightly + initial_principal_fortnightly
                                       + initial_extra_fortnightly)

        self.initial_payment_breakdown = {
            "total_amount_borrowed": total_amount_borrowed,
            "estimated_repayment_monthly": estimated_repayment_monthly,
            "estimated_repayment_fortnightly": estimated_repayment_fortnightly,
            "initial_interest_monthly": initial_interest_monthly,
            "initial_principal_monthly": initial_principal_monthly,
            "initial_extra_monthly": initial_extra_monthly,
            "total_repayment_monthly": total_repayment_monthly,
            "initial_interest_fortnightly": initial_interest_fortnightly,
            "initial_principal_fortnightly": initial_principal_fortnightly,
            "initial_extra_fortnightly": initial_extra_fortnightly,
            "total_repayment_fortnightly": total_repayment_fortnightly
        }

    def calculate_mortgage_maturity(self):
        details = self.initial_payment_breakdown
        term = self._initial_term
        interest = self._initial_interest
        principal = details["total_amount_borrowed"]
        override = self.payment_override_enabled
        monthly_override_amount = self.monthly_payment_override
        fortnightly_override_amount = self.fortnightly_payment_override

        # full term
        full_term_payments_fortnightly = term * 26
        interest_over_full_term_fortnightly = details['estimated_repayment_fortnightly'] * 26 * term - principal
        principal_plus_interest_full_term_fortnightly = interest_over_full_term_fortnightly + principal

        full_term_payments_monthly = term * 12
        interest_over_full_term_monthly = details['estimated_repayment_monthly'] * 12 * term - principal
        principal_plus_interest_full_term_monthly = interest_over_full_term_monthly + principal

        # term override
        remaining_principal_monthly = principal
        total_interest_paid_monthly = 0
        total_repayment_monthly = 0
        total_interest_saved_monthly = 0
        months_to_repay = 0

        if override and monthly_override_amount is not None:
            while remaining_principal_monthly > 0:
                months_to_repay += 1
                interest_paid_this_month = remaining_principal_monthly * (interest / 12)
                principal_paid_this_month = monthly_override_amount - interest_paid_this_month
                remaining_principal_monthly -= principal_paid_this_month
                total_interest_paid_monthly += interest_paid_this_month
                total_repayment_monthly += monthly_override_amount

            total_interest_saved_monthly = interest_over_full_term_monthly - total_interest_paid_monthly

        remaining_principal_fortnightly = principal
        total_interest_paid_fortnightly = 0
        total_repayment_fortnightly = 0
        total_interest_saved_fortnightly = 0
        fortnights_to_repay = 0

        if override and fortnightly_override_amount is not None:
            while remaining_principal_fortnightly > 0:
                fortnights_to_repay += 1
                interest_paid_this_fortnight = remaining_principal_fortnightly * (interest / 26)
                principal_paid_this_fortnight = fortnightly_override_amount - interest_paid_this_fortnight
                remaining_principal_fortnightly -= principal_paid_this_fortnight
                total_interest_paid_fortnightly += interest_paid_this_fortnight
                total_repayment_fortnightly += fortnightly_override_amount

            total_interest_saved_fortnightly = interest_over_full_term_fortnightly - total_interest_paid_fortnightly

        self.mortgage_maturity = {
            "monthly": {
                "full_term_payments": full_term_payments_monthly,
                "interest_over_full_term": interest_over_full_term_monthly,
                "principal_plus_interest_full_term": principal_plus_interest_full_term_monthly,
                "total_interest_paid": total_interest_paid_monthly,
                "total_repayment": total_repayment_monthly,
                "total_interest_saved": total_interest_saved_monthly,
                "months_to_repay": months_to_repay
            },
            "fortnightly": {
                "full_term_payments": full_term_payments_fortnightly,
                "interest_over_full_term": interest_over_full_term_fortnightly,
                "principal_plus_interest_full_term": principal_plus_interest_full_term_fortnightly,
                "total_interest_paid": total_interest_paid_fortnightly,
                "total_repayment": total_repayment_fortnightly,
                "total_interest_saved": total_interest_saved_fortnightly,
                "fortnights_to_repay": fortnights_to_repay
            }
        }

    def amortization_table(self):
        total_amount_borrowed = self.initial_payment_breakdown["total_amount_borrowed"]
        term = self._initial_term
        interest = self._initial_interest
        override = self.payment_override_enabled
        monthly_override_amount = self.monthly_payment_override
        fortnightly_override_amount = self.fortnightly_payment_override

        amortization_table_monthly = []
        amortization_table_fortnightly = []

        # create balances
        balance_monthly = total_amount_borrowed
        balance_fortnightly = total_amount_borrowed

        accumulated_interest_monthly = 0
        accumulated_principal_payment_monthly = 0
        accumulated_interest_fortnightly = 0
        accumulated_principal_payment_fortnightly = 0

        # monthly
        for period in range(1, term * 12 + 1):
            interest_payment = balance_monthly * (interest / 12) if balance_monthly > 0 else 0
            principal_payment = self.initial_payment_breakdown[
                                    "estimated_repayment_monthly"] - interest_payment if interest_payment > 0 else 0
            extra_payment = (monthly_override_amount - self.initial_payment_breakdown[
                "estimated_repayment_monthly"]) if override and interest_payment > 0 else 0
            total_payment = interest_payment + principal_payment + extra_payment
            new_balance = balance_monthly - principal_payment - extra_payment if balance_monthly > 0 else 0
            accumulated_interest_monthly += interest_payment if balance_monthly > 0 else 0
            accumulated_principal_payment_monthly += principal_payment + extra_payment if interest_payment > 0 else 0

            amortization_table_monthly.append({
                "Period": period,
                "Balance": balance_monthly,
                "Interest": interest_payment,
                "Principal": principal_payment,
                "Extra": extra_payment,
                "Total Payment": total_payment,
                "New Balance": new_balance,
                "Accumulated Interest": accumulated_interest_monthly,
                "Accumulated Principal Payment": accumulated_principal_payment_monthly
            })

            balance_monthly = new_balance
            if balance_monthly <= 0:
                break

        # fortnightly
        for period in range(1, term * 26 + 1):
            interest_payment = balance_fortnightly * (interest / 26) if balance_fortnightly > 0 else 0
            principal_payment = self.initial_payment_breakdown[
                                    "estimated_repayment_fortnightly"] - interest_payment if interest_payment > 0 else 0
            extra_payment = (fortnightly_override_amount - self.initial_payment_breakdown[
                "estimated_repayment_fortnightly"]) if override and interest_payment > 0 else 0
            total_payment = interest_payment + principal_payment + extra_payment
            new_balance = balance_fortnightly - principal_payment - extra_payment if balance_fortnightly > 0 else 0
            accumulated_interest_fortnightly += interest_payment if balance_fortnightly > 0 else 0
            accumulated_principal_payment_fortnightly += (principal_payment +
                                                          extra_payment) if interest_payment > 0 else 0

            amortization_table_fortnightly.append({
                "Period": period,
                "Balance": balance_fortnightly,
                "Interest": interest_payment,
                "Principal": principal_payment,
                "Extra": extra_payment,
                "Total Payment": total_payment,
                "New Balance": new_balance,
                "Accumulated Interest": accumulated_interest_fortnightly,
                "Accumulated Principal Payment": accumulated_principal_payment_fortnightly
            })

            balance_fortnightly = new_balance
            if balance_fortnightly <= 0:
                break

        self.amortization_schedule = {
            "monthly": amortization_table_monthly,
            "fortnightly": amortization_table_fortnightly
        }
        return self.amortization_schedule

    def add_comment(self, comment: str):
        self._comments.append(comment)

    def get_comments(self):
        return self._comments


if __name__ == "__main__":
    M = Mortgage()
    try:

        M.gather_inputs(
            principal=810000,
            interest=0.05,
            term=20,
            extra_costs=10000,
            deposit=50000,
            payment_override_enabled=True,
            monthly_payment_override=6000,
            fortnightly_payment_override=3000
        )

        M.calculate_initial_payment_breakdown()
        print("Initial Payment Breakdown:")
        print("Monthly:", M.initial_payment_breakdown["estimated_repayment_monthly"])
        print("Fortnightly:", M.initial_payment_breakdown["estimated_repayment_fortnightly"])
        print("Payment Override Enabled:", M.payment_override_enabled)
        print("Monthly Payment Override:", M.monthly_payment_override)
        print("Fortnightly Payment Override:", M.fortnightly_payment_override)
        print()

        M.calculate_mortgage_maturity()
        print("Mortgage Maturity Details:")
        print("Monthly:")
        for key, value in M.mortgage_maturity.items():
            print(f"  {key}: {value}")
        print()

        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:  # show first 5 data
            print(row)

        # test boom payment
        M.make_balloon_payment(100000)
        print("\nAfter Boom Payment of 100000:")
        M.calculate_mortgage_maturity()
        for key, value in M.mortgage_maturity.items():
            print(f"  {key}: {value}")
        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:  # show first 5 data
            print(row)

        # add comment
        M.add_comment("need extra money to for insurance.")
        M.add_comment("borrow more money for buying a car.")

        print("\nComments:")
        comments = M.get_comments()
        for comment in comments:
            print(comment)

    except Exception as e:
        print(f"An error occurred: {e}")
