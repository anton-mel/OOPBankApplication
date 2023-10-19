class OverdrawError(Exception):
    "Indicates that account balance was insufficient to complete the transation"

    pass

class TransactionLimitError(Exception):
    "Indicates that either a daily or monthly limit was hit for this account"

    def __init__(self, limit_type, limit):
        super().__init__()
        self.limit_type = limit_type
        self.limit = limit

class TransactionSequenceError(Exception):
    "Indicates that this transaction was not created in sequential order"

    def __init__(self, date):
        super().__init__()
        self.latest_date = date