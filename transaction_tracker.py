from datetime import datetime, timedelta


class TransactionData:
    def __init__(self, batch_size: int, single_amount: float):
        self.start_time = datetime.now()
        self.data = {
            "batch_size": batch_size,
            "single_amount": single_amount,
            "total_amount": batch_size * single_amount,
            "transaction_count": 0,
            "transaction_times": [],
            "session_status": "In Progress",
            "error_message": None,
        }

    def transaction_starting(self, current_cycle):
        self.data["transaction_count"] = current_cycle + 1
        self.transaction_start_time = datetime.now()

    def transaction_successful(self):
        transaction_end_time = datetime.now()
        transaction_time = (transaction_end_time - self.transaction_start_time).total_seconds()
        self.data["transaction_times"].append(transaction_time)

    def transaction_failed(self, error_message):
        self.data["session_status"] = "Failed"
        self.data["error_message"] = error_message

    def session_completed(self):
        if self.data["error_message"] is None:
            self.data["session_status"] = "Completed"

    def get_data(self):
        data = self.data.copy()
        data["average_transaction_time"] = sum(data["transaction_times"]) / len(data["transaction_times"]) if data[
            "transaction_times"] else None
        data["elapsed_time"] = (datetime.now() - self.start_time).total_seconds()
        data["estimated_time_left"] = data["average_transaction_time"] * (
                data["batch_size"] - data["transaction_count"]) if data[
                                                                       "average_transaction_time"] is not None else None
        data["total_estimated_time"] = data["average_transaction_time"] * data["batch_size"] if data[
                                                                                                    "average_transaction_time"] is not None else None
        del data["transaction_times"]
        return data

    def pretty_stdout(self):
        data = self.get_data()
        for key, value in data.items():
            print(f"{key}:\n    {value}")
