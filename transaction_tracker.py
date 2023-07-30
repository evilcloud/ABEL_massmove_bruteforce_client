class TransactionData:
    def __init__(self, batch_size: int, single_amount: float):
        self.batch_size = batch_size
        self.single_amount = single_amount
        self.total_amount = batch_size * single_amount
        self.transaction_count = 0
        self.successful_transactions = 0
        self.failed_transactions = 0
        self.pending_transactions = 0
        self.data = {
            "batch_size": self.batch_size,
            "single_amount": self.single_amount,
            "total_amount": self.total_amount,
            "transaction_count": self.transaction_count,
            "successful_transactions": self.successful_transactions,
            "failed_transactions": self.failed_transactions,
            "pending_transactions": self.pending_transactions,
        }

    def transaction_starting(self, current_cycle):
        self.transaction_count = current_cycle + 1
        self.data["transaction_count"] = self.transaction_count
        self.pending_transactions += 1
        self.data["pending_transactions"] = self.pending_transactions

    def transaction_successful(self):
        self.successful_transactions += 1
        self.pending_transactions -= 1
        self.data["successful_transactions"] = self.successful_transactions
        self.data["pending_transactions"] = self.pending_transactions

    def transaction_failed(self, error_message):
        self.failed_transactions += 1
        self.pending_transactions -= 1
        self.data["failed_transactions"] = self.failed_transactions
        self.data["pending_transactions"] = self.pending_transactions

    def session_completed(self):
        self.data["session_status"] = "completed"

    def get_data(self):
        return self.data
