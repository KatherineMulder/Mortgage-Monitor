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
