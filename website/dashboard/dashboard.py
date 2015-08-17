from tenancy_summary import TenancySummary
from property_summary import PropertySummary

class Dashboard():
    """
    Calculates the figures for the user's dashboard.
    Access the data with get_data. It returns a dict containing
    calculation results which can be passed directly to the index template
    """

    # data sources
    properties = None
    tenancies = None
    transactions = None

    def __init__(self, properties, tenancies, transactions):
        self.properties = properties
        self.tenancies = tenancies
        self.transactions = transactions

        self.tenancy_summaries = []
        self.property_summaries = []

        self._calculate_tenancy_summaries()
        self._calculate_property_summaries()

    def get_data(self):
        return self.tenancy_summaries, self.property_summaries

    def _calculate_tenancy_summaries(self):
        for tenancy in self.tenancies:
            transactions = self.transactions.filter(tenancy=tenancy.id)
            tenancy_summary = TenancySummary(tenancy, transactions)
            tenancy_summary.calculate()
            self.tenancy_summaries.append(tenancy_summary)

    def _calculate_property_summaries(self):
        for prop in self.properties:
            transactions = self.transactions.filter(property=prop.id)
            property_summary = PropertySummary(prop, transactions)
            property_summary.calculate()
            self.property_summaries.append(property_summary)
