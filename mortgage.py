from decimal import Decimal, getcontext
from math import log, floor

# set decimal precision high enough for financial calculations?
getcontext().prec = 28


class Mortgage:
    def __init__(self, comments=None, payment_override_enabled="n", monthly_payment_override=None,
                 fortnightly_payment_override=None):
        self._mortgage_id = None
        self._mortgage_name = ""
        self._initial_interest = 0.0
        self._initial_term = 0
        self._initial_principal = 0.0
        self._deposit = 0.0
        self._extra_costs = 0.0
        self._comments = comments if comments else []
        self.payment_override_enabled = payment_override_enabled
        self.monthly_payment_override = monthly_payment_override
        self.fortnightly_payment_override = fortnightly_payment_override
        self.initial_payment_breakdown = {}
        self.mortgage_maturity = {}
        self.amortization_schedule = []

    @property
    def mortgage_id(self):
        return self._mortgage_id

    @mortgage_id.setter
    def mortgage_id(self, value):
        if not isinstance(value, int):
            raise ValueError("mortgage ID must be an integer")
        if value < 0:
            raise ValueError("mortgage ID cannot be negative")
        self._mortgage_id = value

    @property
    def mortgage_name(self):
        return self._mortgage_name

    @mortgage_name.setter
    def mortgage_name(self, value):
        if not isinstance(value, str):
            raise ValueError("mortgage name must be a string")
        if not value:
            raise ValueError("mortgage name cannot be empty")
        self._mortgage_name = value

    @property
    def initial_interest(self):
        return self._initial_interest

    @initial_interest.setter
    def initial_interest(self, value):
        if not isinstance(value, (float, int)):
            raise ValueError("initial interest must be a numeric value")
        if value < 0:
            raise ValueError("initial interest cannot be negative")
        self._initial_interest = float(value)

    @property
    def initial_term(self):
        return self._initial_term

    @initial_term.setter
    def initial_term(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("initial term must be a number")
        if value <= 0:
            raise ValueError("initial term must be greater than zero")
        if value > 30:
            raise ValueError("maximum initial term is 30 years")
        self._initial_term = value

    @property
    def initial_principal(self):
        return self._initial_principal

    @initial_principal.setter
    def initial_principal(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("initial principal must be a number")
        if value <= 0:
            raise ValueError("initial principal must be greater than zero")
        self._initial_principal = value

    @property
    def deposit(self):
        return self._deposit

    @deposit.setter
    def deposit(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("deposit must be a number")
        if value < 0:
            raise ValueError("deposit cannot be negative")
        if value > self._initial_principal:
            raise ValueError("deposit cannot be greater than the initial principal")
        self._deposit = value

    @property
    def extra_costs(self):
        return self._extra_costs

    @extra_costs.setter
    def extra_costs(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError("extra costs must be a number")
        if value < 0:
            raise ValueError("extra costs cannot be negative")
        self._extra_costs = value

    def calculate_total_amount_borrow(self):
        return self._initial_principal - self._deposit + self._extra_costs

    def calculate_estimated_repayment(self, fortnightly=True, adjustment_factor=0.0):
        total_amount_borrow = Decimal(self.calculate_total_amount_borrow())
        interest_rate = Decimal(self._initial_interest) / 100 + Decimal(adjustment_factor)
        term_multiplier = 26 if fortnightly else 12
        term = self._initial_term * term_multiplier

        estimated_repayment = total_amount_borrow * (interest_rate / term_multiplier) / (
                1 - (1 + interest_rate / term_multiplier) ** -term
        )
        return float(estimated_repayment.quantize(Decimal('.01')))

    def calculate_initial_payment_breakdown(self):
        total_amount_borrow = Decimal(self.calculate_total_amount_borrow())


        monthly_interest = Decimal('0')
        estimated_monthly_repayment = Decimal('0')
        monthly_principal_repayment = Decimal('0')

        if total_amount_borrow > 0:
            # interest
            monthly_interest = (total_amount_borrow * Decimal(self._initial_interest) / Decimal('12') / Decimal(
                '100')).quantize(Decimal('.01'))


            # repayment
            rate_per_month = Decimal(self._initial_interest) / Decimal('12') / Decimal('100')
            term_in_months = self._initial_term * 12
            estimated_monthly_repayment = (total_amount_borrow * (
                    rate_per_month / (Decimal('1') - (Decimal('1') + rate_per_month) ** -term_in_months)
            )).quantize(Decimal('.01'))
            # Monthly principal repayment
            monthly_principal_repayment = estimated_monthly_repayment - monthly_interest

        # calculations
        fortnightly_interest = Decimal('0')
        estimated_fortnightly_repayment = Decimal('0')
        fortnightly_principal_repayment = Decimal('0')

        if total_amount_borrow > 0:
            # interest
            fortnightly_interest = (total_amount_borrow * Decimal(self._initial_interest) / Decimal('26') / Decimal(
                '100')).quantize(Decimal('.01'))


            #  repayment
            rate_per_fortnight = Decimal(self._initial_interest) / Decimal('26') / Decimal('100')
            term_in_fortnights = self._initial_term * 26
            estimated_fortnightly_repayment = (total_amount_borrow * (
                    rate_per_fortnight / (
                    Decimal('1') - (Decimal('1') + rate_per_fortnight) ** -term_in_fortnights)
            )).quantize(Decimal('.01'))
            # Fortnightly principal repayment
            fortnightly_principal_repayment = estimated_fortnightly_repayment - fortnightly_interest

        #  ±0.1% calculations
        self.estimated_monthly_repayment_plus = Decimal(
            self.calculate_estimated_repayment(fortnightly=False, adjustment_factor=0.001))
        self.estimated_monthly_repayment_minus = Decimal(
            self.calculate_estimated_repayment(fortnightly=False, adjustment_factor=-0.001))
        self.estimated_fortnightly_repayment_plus = Decimal(
            self.calculate_estimated_repayment(fortnightly=True, adjustment_factor=0.001))
        self.estimated_fortnightly_repayment_minus = Decimal(
            self.calculate_estimated_repayment(fortnightly=True, adjustment_factor=-0.001))

        initial_extra = Decimal('0')
        fortnightly_extra = Decimal('0')

        if self.payment_override_enabled.lower() == "y":
            if self.monthly_payment_override is not None:
                monthly_override_amount = Decimal(self.monthly_payment_override)
                if monthly_override_amount <= estimated_monthly_repayment:
                    raise ValueError("Monthly override payment must be greater than the estimated monthly repayment.")
                initial_extra = monthly_override_amount - estimated_monthly_repayment

            if self.fortnightly_payment_override is not None:
                fortnightly_override_amount = Decimal(self.fortnightly_payment_override)
                if fortnightly_override_amount <= estimated_fortnightly_repayment:
                    raise ValueError(
                        "Fortnightly override payment must be greater than the estimated fortnightly repayment.")
                fortnightly_extra = fortnightly_override_amount - estimated_fortnightly_repayment

        repayment = monthly_interest + monthly_principal_repayment + initial_extra
        fortnightly_repayment = fortnightly_interest + fortnightly_principal_repayment + fortnightly_extra

        return {
            "total_amount_borrow": float(total_amount_borrow),
            "monthly_interest": float(monthly_interest),
            "estimated_monthly_repayment": float(estimated_monthly_repayment),
            "monthly_principal_repayment": float(monthly_principal_repayment),
            "fortnightly_interest": float(fortnightly_interest),
            "estimated_fortnightly_repayment": float(estimated_fortnightly_repayment),
            "fortnightly_principal_repayment": float(fortnightly_principal_repayment),
            "estimated_monthly_repayment_plus": float(self.estimated_monthly_repayment_plus),
            "estimated_monthly_repayment_minus": float(self.estimated_monthly_repayment_minus),
            "estimated_fortnightly_repayment_plus": float(self.estimated_fortnightly_repayment_plus),
            "estimated_fortnightly_repayment_minus": float(self.estimated_fortnightly_repayment_minus),
            "initial_extra": float(initial_extra),
            "repayment": float(repayment),
            "fortnightly_extra": float(fortnightly_extra),
            "fortnightly_repayment": float(fortnightly_repayment)
        }

    def calculate_amortization_schedule(self):
        total_amount_borrow = Decimal(self.calculate_total_amount_borrow())
        term_months = self._initial_term * 12
        monthly_interest_rate = Decimal(self._initial_interest) / 12 / 100
        monthly_repayment = Decimal(self.calculate_estimated_repayment(fortnightly=False))

        balance = total_amount_borrow
        amortization_schedule = []

        for month in range(1, term_months + 1):
            interest_payment = (balance * monthly_interest_rate).quantize(Decimal('.01'))
            principal_payment = (monthly_repayment - interest_payment).quantize(Decimal('.01'))
            balance = (balance - principal_payment).quantize(Decimal('.01'))
            amortization_schedule.append({
                "month": month,
                "interest_payment": float(interest_payment),
                "principal_payment": float(principal_payment),
                "total_payment": float(monthly_repayment),
                "balance": max(float(balance), 0)
            })

            if balance <= 0:
                break

        self.amortization_schedule = amortization_schedule
        return self.amortization_schedule

    def calculate_mortgage_maturity(self):
        total_amount_borrow = Decimal(self.calculate_total_amount_borrow())
        monthly_interest_rate = Decimal(self._initial_interest) / 12 / 100
        fortnightly_interest_rate = Decimal(self._initial_interest) / 26 / 100

        # regular
        monthly_repayment = Decimal(self.calculate_estimated_repayment(fortnightly=False))
        fortnightly_repayment = Decimal(self.calculate_estimated_repayment(fortnightly=True))

        def calculate_term(balance, payment, interest_rate, period):
            term = 0
            while balance > 0:
                interest_payment = (balance * interest_rate).quantize(Decimal('.01'))
                principal_payment = (payment - interest_payment).quantize(Decimal('.01'))
                balance = (balance - principal_payment).quantize(Decimal('.01'))
                term += 1
                if term > period:
                    break
            return term

        term_months = self._initial_term * 12
        term_fortnights = self._initial_term * 26

        regular_monthly_term = calculate_term(total_amount_borrow, monthly_repayment, monthly_interest_rate,
                                              term_months)
        regular_fortnightly_term = calculate_term(total_amount_borrow, fortnightly_repayment, fortnightly_interest_rate,
                                                  term_fortnights)

        overridden_monthly_term = overridden_fortnightly_term = None
        if self.payment_override_enabled.lower() == "y":
            if self.monthly_payment_override is not None:
                overridden_monthly_repayment = Decimal(self.monthly_payment_override)
                overridden_monthly_term = calculate_term(total_amount_borrow, overridden_monthly_repayment,
                                                         monthly_interest_rate, term_months)

            if self.fortnightly_payment_override is not None:
                overridden_fortnightly_repayment = Decimal(self.fortnightly_payment_override)
                overridden_fortnightly_term = calculate_term(total_amount_borrow, overridden_fortnightly_repayment,
                                                             fortnightly_interest_rate, term_fortnights)

        # for the calculation
        payment_overfull_term = self._initial_term * 26
        payments_over_reduced_term = regular_fortnightly_term if self.payment_override_enabled.lower() == "n" else \
            floor(-log(1 - float(total_amount_borrow) / (fortnightly_repayment * 26)) / log(
                1 + float(fortnightly_interest_rate)))
        full_term_amortize = payment_overfull_term / 26
        estimated_reduced_term_to_amortize = payments_over_reduced_term / 26
        interest_over_full_term_plus = float(
            self.estimated_fortnightly_repayment_plus) * 26 * self._initial_term - float(total_amount_borrow)
        interest_over_full_term_minus = float(
            self.estimated_fortnightly_repayment_minus) * 26 * self._initial_term - float(total_amount_borrow)
        principle_plus_interest = float(total_amount_borrow) + interest_over_full_term_plus
        interest_over_reduced_term = 0 if self.payment_override_enabled.lower() == "n" else \
            float(overridden_fortnightly_repayment) * 26 * regular_fortnightly_term - float(total_amount_borrow)
        interest_saved_over_reduced_term = 0 if self.payment_override_enabled.lower() == "n" else \
            interest_over_full_term_plus - interest_over_reduced_term
        principle_plus_interest_over_reduced_term = 0 if self.payment_override_enabled.lower() == "n" else \
            float(total_amount_borrow) + interest_over_reduced_term

        self.mortgage_maturity = {
            "payment_overfull_term": payment_overfull_term,
            "payments_over_reduced_term": payments_over_reduced_term,
            "full_term_amortize": full_term_amortize,
            "estimated_reduced_term_to_amortize": estimated_reduced_term_to_amortize,
            "interest_over_full_term_plus": interest_over_full_term_plus,
            "interest_over_full_term_minus": interest_over_full_term_minus,
            "principle_plus_interest": principle_plus_interest,
            "interest_over_reduced_term": interest_over_reduced_term,
            "interest_saved_over_reduced_term": interest_saved_over_reduced_term,
            "principle_plus_interest_over_reduced_term": principle_plus_interest_over_reduced_term
        }

        return self.mortgage_maturity


if __name__ == "__main__":
    print("start Tests")

    mortgage_n = Mortgage(payment_override_enabled="n")
    mortgage_n.mortgage_id = 1
    mortgage_n.mortgage_name = "test Mortgage (n)"
    mortgage_n.initial_interest = 3.5
    mortgage_n.initial_term = 25
    mortgage_n.initial_principal = 300000
    mortgage_n.deposit = 50000
    mortgage_n.extra_costs = 10000

    mortgage_y = Mortgage(payment_override_enabled="y", monthly_payment_override="2000",
                          fortnightly_payment_override="1000")
    mortgage_y.mortgage_id = 2
    mortgage_y.mortgage_name = "test Mortgage (y)"
    mortgage_y.initial_interest = 3.5
    mortgage_y.initial_term = 25
    mortgage_y.initial_principal = 300000
    mortgage_y.deposit = 50000
    mortgage_y.extra_costs = 10000

    print("testing __str__ method:")
    print(mortgage_n)
    print(mortgage_y)

    print("\ntesting calculate_initial_payment_breakdown method for 'n':")
    breakdown_n = mortgage_n.calculate_initial_payment_breakdown()
    print("total amount borrow:", breakdown_n["total_amount_borrow"])
    print("monthly Interest:", breakdown_n["monthly_interest"])
    print("monthly Repayment:", breakdown_n["estimated_monthly_repayment"])
    print("monthly Principal Repayment:", breakdown_n["monthly_principal_repayment"])
    print("fortnightly Interest:", breakdown_n["fortnightly_interest"])
    print("fortnightly Repayment:", breakdown_n["estimated_fortnightly_repayment"])
    print("fortnightly Principal Repayment:", breakdown_n["fortnightly_principal_repayment"])
    print("estimated Monthly Repayment (+0.1%):", breakdown_n["estimated_monthly_repayment_plus"])
    print("estimated Monthly Repayment (-0.1%):", breakdown_n["estimated_monthly_repayment_minus"])
    print("estimated Fortnightly Repayment (+0.1%):", breakdown_n["estimated_fortnightly_repayment_plus"])
    print("estimated Fortnightly Repayment (-0.1%):", breakdown_n["estimated_fortnightly_repayment_minus"])
    print("initial Extra:", breakdown_n["initial_extra"])
    print("repayment:", breakdown_n["repayment"])
    print("fortnightly Extra:", breakdown_n["fortnightly_extra"])
    print("fortnightly Repayment:", breakdown_n["fortnightly_repayment"])

    print("\ntesting calculate_initial_payment_breakdown method for 'y':")
    breakdown_y = mortgage_y.calculate_initial_payment_breakdown()
    print("total amount borrow:", breakdown_y["total_amount_borrow"])
    print("monthly Interest:", breakdown_y["monthly_interest"])
    print("monthly Repayment:", breakdown_y["estimated_monthly_repayment"])
    print("monthly Principal Repayment:", breakdown_y["monthly_principal_repayment"])
    print("fortnightly Interest:", breakdown_y["fortnightly_interest"])
    print("fortnightly Repayment:", breakdown_y["estimated_fortnightly_repayment"])
    print("fortnightly Principal Repayment:", breakdown_y["fortnightly_principal_repayment"])
    print("estimated Monthly Repayment (+0.1%):", breakdown_y["estimated_monthly_repayment_plus"])
    print("estimated Monthly Repayment (-0.1%):", breakdown_y["estimated_monthly_repayment_minus"])
    print("estimated Fortnightly Repayment (+0.1%):", breakdown_y["estimated_fortnightly_repayment_plus"])
    print("estimated Fortnightly Repayment (-0.1%):", breakdown_y["estimated_fortnightly_repayment_minus"])
    print("initial Extra:", breakdown_y["initial_extra"])
    print("repayment:", breakdown_y["repayment"])
    print("fortnightly Extra:", breakdown_y["fortnightly_extra"])
    print("fortnightly Repayment:", breakdown_y["fortnightly_repayment"])
    print("\ntesting calculate_amortization_schedule method for 'n':")
    amortization_schedule_n = mortgage_n.calculate_amortization_schedule()
    for month_info in amortization_schedule_n:
        print(month_info)
    print("\ntesting calculate_amortization_schedule method for 'y':")
    amortization_schedule_y = mortgage_y.calculate_amortization_schedule()
    for month_info in amortization_schedule_y:
        print(month_info)
    print("\ntesting calculate_mortgage_maturity method for 'n':")
    maturity_n = mortgage_n.calculate_mortgage_maturity()
    print(maturity_n)

    print("\ntesting calculate_mortgage_maturity method for 'y':")
    maturity_y = mortgage_y.calculate_mortgage_maturity()
    print(maturity_y)

    print("end Tests")
