from datetime import datetime
from typing import List, Optional, Dict


class Mortgage:
    def __init__(self, mortgage_name: str, initial_interest: float, initial_term: int, initial_principal: float,
                 deposit: float, extra_costs: float, comments: Optional[str] = None,
                 payment_override_enabled: bool = False,
                 monthly_payment_override: Optional[float] = None, fortnightly_payment_override: Optional[float] = None,
                 start_date: Optional[datetime] = None, created_at: Optional[datetime] = None):
        self._mortgage_id: Optional[int] = None
        self._mortgage_name: str = mortgage_name
        self._initial_interest: float = initial_interest / 100
        self._initial_term: int = initial_term
        self._initial_principal: float = initial_principal
        self._deposit: float = deposit
        self._extra_costs: float = extra_costs
        self._start_date: datetime = start_date if start_date else datetime.now()
        self._created_at: Optional[datetime] = created_at
        self._comments: str = comments if comments else ""
        self.payment_override_enabled: bool = payment_override_enabled
        self.monthly_payment_override: Optional[float] = monthly_payment_override
        self.fortnightly_payment_override: Optional[float] = fortnightly_payment_override
        self.initial_payment_breakdown: Dict = {}
        self.mortgage_maturity: Dict = {}
        self.amortization_schedule: Dict[str, List[Dict[str, float]]] = {}
        self.interest_rate_changes: List[Dict] = []
        self.historical_transactions: List[Dict] = []
        self.transaction_logs = []

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        if value is None or not isinstance(value, datetime):
            raise ValueError("Start date must be a datetime.")
        self._start_date = value

    @property
    def mortgage_id(self) -> Optional[int]:
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, value: int) -> None:
        if value is None or not isinstance(value, int):
            raise ValueError("Mortgage ID must be an integer")
        if value < 0:
            raise ValueError("Mortgage ID cannot be negative")
        self._mortgage_id = value

    @property
    def mortgage_name(self) -> str:
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, value: str) -> None:
        if value is None or not isinstance(value, str):
            raise ValueError("Mortgage name must be a string")
        if not value:
            raise ValueError("Mortgage name cannot be empty")
        self._mortgage_name = value

    @property
    def initial_interest(self) -> float:
        return self._initial_interest

    @initial_interest.setter
    def initial_interest(self, value: float) -> None:
        if value is None or not isinstance(value, (float, int)):
            raise ValueError("Initial interest must be a numeric value")
        if value < 0:
            raise ValueError("Initial interest cannot be negative")
        self._initial_interest = float(value)

    @property
    def initial_term(self) -> int:
        return self._initial_term

    @initial_term.setter
    def initial_term(self, value: int) -> None:
        if value is None or not isinstance(value, int):
            raise ValueError("Initial term must be an integer")
        if value <= 0:
            raise ValueError("Initial term must be greater than zero")
        if value > 30:
            raise ValueError("Maximum initial term is 30 years")
        self._initial_term = value

    @property
    def initial_principal(self) -> float:
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("Initial principal must be a number")
        if value <= 0:
            raise ValueError("Initial principal must be greater than zero")
        self._initial_principal = value

    @property
    def deposit(self) -> float:
        return self._deposit

    @deposit.setter
    def deposit(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("Deposit must be a number")
        if value < 0:
            raise ValueError("Deposit cannot be negative")
        if value > self._initial_principal:
            raise ValueError("Deposit cannot be greater than the initial principal")
        self._deposit = value

    @property
    def extra_costs(self) -> float:
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, value: float) -> None:
        if value is None or not isinstance(value, (int, float)):
            raise ValueError("Extra costs must be a number")
        if value < 0:
            raise ValueError("Extra costs cannot be negative")
        self._extra_costs = value

    def gather_inputs(self, principal, interest, term, extra_costs, deposit, payment_override_enabled,
                      monthly_payment_override, fortnightly_payment_override):
        self._initial_principal = principal
        self._initial_interest = interest / 100
        self._initial_term = term
        self._extra_costs = extra_costs
        self._deposit = deposit
        self.payment_override_enabled = payment_override_enabled
        self.monthly_payment_override = monthly_payment_override
        self.fortnightly_payment_override = fortnightly_payment_override

    def calculate_projected_payment(self, principal: float, interest_rate: float, term: int, frequency: str):
        if frequency == "monthly":
            rate = interest_rate / 12 / 100
            payments = term * 12
        elif frequency == "fortnightly":
            rate = interest_rate / 26 / 100
            payments = term * 26
        else:
            raise ValueError("Invalid frequency. Choose either 'monthly' or 'fortnightly'.")

        payment = principal * (rate / (1 - (1 + rate) ** -payments))
        return payment

    def generate_planning_scenarios(self, principal_increment: float, principal_increments: int,
                                    interest_increment: float, interest_increments: int):
        total_amount_borrowed = self._initial_principal - self._deposit + self._extra_costs
        scenarios = []

        for i in range(principal_increments + 1):
            principal = total_amount_borrowed + (i * principal_increment)
            monthly_payments = []
            fortnightly_payments = []

            for j in range(interest_increments + 1):
                interest_rate = (self._initial_interest * 100) + (j * interest_increment)

                monthly_payment = self.calculate_projected_payment(principal, interest_rate, self._initial_term,
                                                                   "monthly")
                fortnightly_payment = self.calculate_projected_payment(principal, interest_rate, self._initial_term,
                                                                       "fortnightly")

                monthly_payments.append(monthly_payment)
                fortnightly_payments.append(fortnightly_payment)

            scenarios.append({
                "principal": principal,
                "monthly_payments": monthly_payments,
                "fortnightly_payments": fortnightly_payments
            })

        return scenarios

    def calculate_initial_payment_breakdown(self):
        principal = self._initial_principal
        interest = self._initial_interest
        term = self._initial_term
        extra_costs = self._extra_costs
        deposit = self._deposit
        payment_override_enabled = self.payment_override_enabled
        monthly_payment_override = self.monthly_payment_override
        fortnightly_payment_override = self.fortnightly_payment_override

        total_amount_borrowed = principal - deposit + extra_costs

        # annual interest rate to monthly interest rate
        monthly_rate = interest / 12
        estimated_repayment_monthly = total_amount_borrowed * (monthly_rate / (1 - (1 + monthly_rate) ** -(term * 12)))
        initial_interest_monthly = total_amount_borrowed * monthly_rate
        initial_principal_monthly = estimated_repayment_monthly - initial_interest_monthly
        initial_extra_monthly = monthly_payment_override - estimated_repayment_monthly if payment_override_enabled else 0
        total_repayment_monthly = initial_interest_monthly + initial_principal_monthly + initial_extra_monthly

        # fortnightly
        fortnightly_rate = interest / 26
        estimated_repayment_fortnightly = total_amount_borrowed * (
                fortnightly_rate / (1 - (1 + fortnightly_rate) ** -(term * 26)))
        initial_interest_fortnightly = total_amount_borrowed * fortnightly_rate
        initial_principal_fortnightly = estimated_repayment_fortnightly - initial_interest_fortnightly
        initial_extra_fortnightly = fortnightly_payment_override - estimated_repayment_fortnightly \
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

        full_term_payments_fortnightly = term * 26
        interest_over_full_term_fortnightly = details['estimated_repayment_fortnightly'] * 26 * term - principal
        principal_plus_interest_full_term_fortnightly = interest_over_full_term_fortnightly + principal

        full_term_payments_monthly = term * 12
        interest_over_full_term_monthly = details['estimated_repayment_monthly'] * 12 * term - principal
        principal_plus_interest_full_term_monthly = interest_over_full_term_monthly + principal

        # override
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
        initial_interest = self._initial_interest
        override = self.payment_override_enabled
        monthly_override_amount = self.monthly_payment_override
        fortnightly_override_amount = self.fortnightly_payment_override

        amortization_table_monthly = []
        amortization_table_fortnightly = []

        balance_monthly = total_amount_borrowed
        balance_fortnightly = total_amount_borrowed

        accumulated_interest_monthly = 0
        accumulated_principal_payment_monthly = 0
        accumulated_interest_fortnightly = 0
        accumulated_principal_payment_fortnightly = 0

        # changes
        current_interest = initial_interest
        change_idx = 0
        changes = self.interest_rate_changes
        next_change = changes[change_idx] if changes else None

        # monthly
        for period in range(1, term * 12 + 1):
            # Check for interest rate change
            if (next_change and period > (next_change["effective_date"].year - self._start_date.year) * 12 +
                    next_change["effective_date"].month - self._start_date.month):
                current_interest = next_change["new_interest_rate"] / 100
                change_idx += 1
                next_change = changes[change_idx] if change_idx < len(changes) else None

            interest_payment = balance_monthly * (current_interest / 12) if balance_monthly > 0 else 0
            principal_payment = self.initial_payment_breakdown[
                                    "estimated_repayment_monthly"] - interest_payment if interest_payment > 0 else 0
            extra_payment = (monthly_override_amount - self.initial_payment_breakdown
            ["estimated_repayment_monthly"]) if override and interest_payment > 0 else 0
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
        current_interest = initial_interest
        change_idx = 0
        next_change = changes[change_idx] if changes else None

        for period in range(1, term * 26 + 1):
            #  rate change
            if next_change and period > (next_change["effective_date"].year - self._start_date.year) * 26 + (
                    next_change["effective_date"].month - self._start_date.month) * 2:
                current_interest = next_change["new_interest_rate"] / 100
                change_idx += 1
                next_change = changes[change_idx] if change_idx < len(changes) else None

            interest_payment = balance_fortnightly * (current_interest / 26) if balance_fortnightly > 0 else 0
            principal_payment = self.initial_payment_breakdown[
                                    "estimated_repayment_fortnightly"] - interest_payment if interest_payment > 0 else 0
            extra_payment = (fortnightly_override_amount - self.initial_payment_breakdown[
                "estimated_repayment_fortnightly"]) if override and interest_payment > 0 else 0
            total_payment = interest_payment + principal_payment + extra_payment
            new_balance = balance_fortnightly - principal_payment - extra_payment if balance_fortnightly > 0 else 0
            accumulated_interest_fortnightly += interest_payment if balance_fortnightly > 0 else 0
            accumulated_principal_payment_fortnightly += principal_payment + extra_payment if interest_payment > 0 else 0

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

    def make_balloon_payment(self, lump_sum: float):
        if lump_sum <= 0:
            raise ValueError("Lump sum payment must be greater than zero")
        if lump_sum > self._initial_principal:
            raise ValueError("Lump sum payment cannot be greater than the remaining principal")
        self._initial_principal -= lump_sum
        transaction = {
            "transaction_date": datetime.now(),
            "transaction_type": "Balloon Payment",
            "amount": lump_sum,
            "current_principal": self._initial_principal,
            "description": "Made a balloon payment"
        }
        self.historical_transactions.append(transaction)
        self.calculate_initial_payment_breakdown()
        self.calculate_mortgage_maturity()
        self.amortization_table()

    def apply_extra_costs(self, extra_costs: float):
        if extra_costs <= 0:
            raise ValueError("Extra costs must be greater than zero")
        self._initial_principal += extra_costs
        transaction = {
            "transaction_date": datetime.now(),
            "transaction_type": "Extra Costs",
            "amount": extra_costs,
            "current_principal": self._initial_principal,
            "description": "Added extra costs to principal"
        }
        self.historical_transactions.append(transaction)
        self.calculate_initial_payment_breakdown()
        self.calculate_mortgage_maturity()
        self.amortization_table()

    def add_comments(self, comments: str):
        self.historical_transactions.append({
            "transaction_date": datetime.now(),
            "transaction_type": "Comments",
            "description": comments
        })

    def get_comments(self) -> List[str]:
        return [t["description"] for t in self.historical_transactions if t["transaction_type"] == "Comments"]

    def get_initial_payment_breakdown(self):
        return self.initial_payment_breakdown

    def to_dict(self):
        return {
            "mortgage_id": self._mortgage_id,
            "initial_interest": self._initial_interest,
            "initial_term": self._initial_term,
            "initial_principal": self._initial_principal,
            "deposit": self._deposit,
            "extra_costs": self._extra_costs,
            "start_date": self._start_date,
            "comments": self.get_comments(),
            "payment_override_enabled": self.payment_override_enabled,
            "monthly_payment_override": self.monthly_payment_override,
            "fortnightly_payment_override": self.fortnightly_payment_override,
            "initial_payment_breakdown": self.initial_payment_breakdown,
            "mortgage_maturity": self.mortgage_maturity,
            "amortization_schedule": self.amortization_schedule,
            "historical_transactions": self.historical_transactions
        }

    def add_interest_rate_change(self, new_interest_rate: float, effective_date: datetime):
        self.interest_rate_changes.append({"new_interest_rate": new_interest_rate, "effective_date": effective_date})

    def get_amortization_schedules(self):
        return self.amortization_table()


if __name__ == "__main__":
    M = Mortgage("Test Mortgage", 5, 20, 810000, 50000, 10000, "initial setup")
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

        # initial
        M.calculate_initial_payment_breakdown()
        print("Initial Payment Breakdown:")
        for key, value in M.get_initial_payment_breakdown().items():
            print(f"{key}: {value}")
        print()

        # maturity
        M.calculate_mortgage_maturity()
        print("Mortgage Maturity Details:")
        for key, value in M.mortgage_maturity.items():
            print(f"{key}: {value}")
        print()

        # amortization table
        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:  # show first 5 data
            print(row)

        # balloon
        M.make_balloon_payment(100000)
        print("\nAfter Balloon Payment of 100000:")
        M.calculate_mortgage_maturity()
        for key, value in M.mortgage_maturity.items():
            print(f"{key}: {value}")
        amortization_schedule = M.amortization_table()
        print("Amortization Table (Monthly - first 5 periods):")
        for row in amortization_schedule["monthly"][:5]:
            print(row)

        # scenarios for the increment
        scenarios = M.generate_planning_scenarios(
            principal_increment=3000.00,
            principal_increments=15,
            interest_increment=5.0,
            interest_increments=15
        )

        print("\nProjected Payments Per Month")
        total_amount_borrowed = 810000 - 50000 + 10000
        header = ["Interest Rate"] + [f"${principal:,.2f}" for principal in
                                      range(total_amount_borrowed, total_amount_borrowed + (3000 * 8), 3000)]
        print("\t".join(header))

        for i in range(16):
            row = [f"{5.0 + (5 * i):.2f}%"]
            for scenario in scenarios:
                row.append(f"${scenario['monthly_payments'][i]:,.2f}")
            print("\t".join(row))

        print("\nprojected payments fortnight")
        print("\t".join(header))

        for i in range(16):
            row = [f"{5.0 + (5 * i):.2f}%"]
            for scenario in scenarios:
                row.append(f"${scenario['fortnightly_payments'][i]:,.2f}")
            print("\t".join(row))


    except Exception as e:
        print(f"error: {e}")
