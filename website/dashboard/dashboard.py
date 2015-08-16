from tenancy_summary import TenancySummary

class Dashboard():
    """
    Calculates the figures for the user's dashboard.
    Access the data with get_data. It returns a dict containing
    calculation results which can be passed directly to the index template
    """

    # data sources
    tenancies = None
    transactions = None

    def __init__(self, tenancies, transactions):
        self.tenancies = tenancies
        self.transactions = transactions
        self.tenancy_summaries = []
        self._calculate_tenancy_summaries()

    def get_data(self):
        return self.tenancy_summaries

    def _calculate_tenancy_summaries(self):
        for tenancy in self.tenancies:
            transactions = self.transactions.filter(tenancy=tenancy.id)
            tenancy_summary = TenancySummary(tenancy, transactions)
            tenancy_summary.calculate()
            self.tenancy_summaries.append(tenancy_summary)
