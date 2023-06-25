import time
import json
from datetime import datetime, timedelta
from external_communications import MultiChannelCommunicator

# TODO: fix transaction curve
# TODO: average per transaction gone missing
class TransactionData:
    def __init__(self, batch_size, single_amount):
        self.cycle_duration = None
        self.communication = MultiChannelCommunicator()
        self.status = "launching"
        self.batch_size = batch_size
        self.single_amount = single_amount
        self.total_expected_amount = batch_size * single_amount
        self.total_transferred = 0
        self.start_time = datetime.now()
        self.transaction_curve = []
        self.current_time = datetime.now()
        self.error_message = None
        self.communication.message_telegram("---LAUNCHING---")
        self.communication.message_telegram(
            {
                "batch size": self.batch_size,
                "single amount": self.single_amount,
                "total expected_amount": self.total_expected_amount,
                "start time": self._format_timestamp(self.start_time),
            }
        )

    def _format_time(self, seconds):
        """Format duration in seconds to 'MM:SS' format."""
        return time.strftime("%M:%S", time.gmtime(seconds))

    def _format_timestamp(self, timestamp):
        """Format timestamp to human-readable format."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def transaction_starting(self, current_cycle):
        self.status = "starting"
        self.current_cycle = current_cycle
        self.transaction_start_time = datetime.now()
        self.current_time = datetime.now()

        self._message_api()

    def transaction_pending(self):
        self.status = "running"
        self.current_time = datetime.now()
        self.total_transferred = self.single_amount * self.current_cycle

        self._message_api()

    def transaction_successful(self):
        self.status = "transacted"
        self.current_time = datetime.now()

        self._message_api()

    def transaction_completed(self):
        self.status = "completed"
        self.current_time = datetime.now()
        self.cycle_duration = int(
            (self.current_time - self.transaction_start_time).total_seconds()
        )

        self.transaction_curve.append({self.current_cycle: self.cycle_duration})
        self.total_transferred = self.single_amount * self.current_cycle

        self._message_api()
        self._message_telegram()

    def transaction_failed(self, error_message):
        self.status = "failed"
        self.error_message = error_message

        self._message_all()
        self._message_telegram()

    def get_json(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()
        average_transaction_time = (
            elapsed_seconds / len(self.transaction_curve)
            if self.transaction_curve
            else 0
        )
        remaining_cycles = self.batch_size - self.current_cycle
        time_left_estimate = timedelta(
            seconds=average_transaction_time * remaining_cycles
        )

        data = {
            "status": self.status,
            "batch size": self.batch_size,
            "single amount": self.single_amount,
            "total expected_amount": self.total_expected_amount,
            "total transferred": self.total_transferred,
            "start time": self._format_timestamp(self.start_time),
            "current time": self._format_timestamp(current_time),
            "elapsed time": str(elapsed_time),
            "average tx duration": str(timedelta(seconds=average_transaction_time)),
            "estimated time left": str(time_left_estimate),
            "current cycle": self.current_cycle,
            "transaction curve": self.transaction_curve,
        }
        if self.current_cycle == 1 and self.status != "completed":
            del data["average tx duration"]
        if self.status == "failed":
            data["error message"] = self.error_message
        if self.status == "completed":
            del data["current cycle"]

        return data

    def _message_api(self):
        self.communication.message_api(self.get_json())

    def _message_all(self):
        self.communication.message_all(self.get_json())

    def _message_telegram(self):
        self.communication.message_telegram(
            {
                "status": self.status,
                "current cycle": self.current_cycle,
                "batch size": self.batch_size,
                "total transferred": self.total_transferred,
                "total expected amount": self.total_expected_amount,
                "current time": self._format_time(
                    (datetime.now() - self.start_time).total_seconds()
                ),
                "total time": self._format_time(
                    (datetime.now() - self.start_time).total_seconds()
                ),
            }
        )

    def _print_json(self):
        print(json.dumps(self.get_json(), indent=4))


