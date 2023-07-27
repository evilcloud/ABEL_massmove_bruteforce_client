import time
import json
from datetime import datetime, timedelta
from external_communications import MultiChannelCommunicator


class TransactionData:
    STATUS = "status"
    BATCH_SIZE = "cycle count"
    SINGLE_AMOUNT = "increment"
    TOTAL_EXPECTED_AMOUNT = "tx capacity"
    TOTAL_TRANSFERRED = "filled"
    START_TIME = "t:start"
    CURRENT_TIME = "t:current"
    ELAPSED_TIME = "t:estimated"
    AVERAGE_TX_DURATION = "average tx time"
    ESTIMATED_TIME_LEFT = "t:remaining"
    CURRENT_CYCLE = "curr cycle"
    TRANSACTION_CURVE = "transaction curve"
    ERROR_MESSAGE = "error message"

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
        self.finished = False
        self.communication.message_telegram("---LAUNCHING---")
        self.communication.message_telegram(
            {
                self.BATCH_SIZE: self.batch_size,
                self.SINGLE_AMOUNT: self.single_amount,
                self.TOTAL_EXPECTED_AMOUNT: self.total_expected_amount,
                self.START_TIME: self._format_timestamp(self.start_time),
            }
        )

    def _format_time(self, seconds):
        """Format duration in seconds to 'MM:SS' format."""
        return time.strftime("%M:%S", time.gmtime(seconds))

    def _format_timestamp(self, timestamp):
        """Format timestamp to human-readable format."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

    def launching_session(self):
        self.status = "launching"
        self.current_time = datetime.now()
        self.communication.message_telegram("---LAUNCHING---")
        self.communication.message_telegram(
            {
                self.BATCH_SIZE: self.batch_size,
                self.SINGLE_AMOUNT: self.single_amount,
                self.TOTAL_EXPECTED_AMOUNT: self.total_expected_amount,
                self.START_TIME: self._format_timestamp(self.start_time),
            }
        )

    def transaction_starting(self, current_cycle):
        self.status = "starting"
        self.current_cycle = current_cycle
        self.transaction_start_time = datetime.now()
        self.current_time = datetime.now()

        self._message_api()

    def transaction_pending(self):
        self.status = "running"
        self.current_time = datetime.now()

        self._message_api()

    def transaction_successful(self):
        self.status = "transacted"
        self.total_transferred += self.single_amount
        self.current_time = datetime.now()

        self._message_api()

    def transaction_completed(self):
        self.status = "completed"
        self.current_time = datetime.now()
        self.cycle_duration = int(
            (self.current_time - self.transaction_start_time).total_seconds()
        )

        self.transaction_curve.append(self.cycle_duration)

        self._message_api()

    def session_completed(self):
        self.finished = True
        self.status = "DONE"
        self.current_time = datetime.now()

        self._message_api()
        self._message_telegram()

    def session_failed(self):
        self.finished = True
        self.status = "session failed"
        self.current_time = datetime.now()

        self._message_api()
        self._message_telegram()

    def transaction_failed(self, error_message):
        self.status = "failed"
        self.error_message = error_message

        self._message_all()
        self._message_telegram()
        self._print_json()

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

        # TODO: fix transaction curve so it works with dashboard

        data = {
            self.STATUS: self.status,
            self.BATCH_SIZE: self.batch_size,
            self.SINGLE_AMOUNT: self.single_amount,
            self.TOTAL_EXPECTED_AMOUNT: self.total_expected_amount,
            self.TOTAL_TRANSFERRED: self.total_transferred,
            self.START_TIME: self._format_timestamp(self.start_time),
            self.CURRENT_TIME: self._format_timestamp(current_time),
            self.ELAPSED_TIME:
                str(elapsed_time - timedelta(
                    microseconds=elapsed_time.microseconds)).split(".")[0],
            self.AVERAGE_TX_DURATION: str(int(average_transaction_time)) + " sec",

            self.ESTIMATED_TIME_LEFT: str(time_left_estimate).split(".")[0],
            self.CURRENT_CYCLE: self.current_cycle,
        }
        if self.current_cycle == 1 and self.status != "completed":
            del data[self.AVERAGE_TX_DURATION]
        if self.status == "failed":
            data[self.ERROR_MESSAGE] = self.error_message
        if self.status == "completed":
            del data[self.CURRENT_CYCLE]
        if self.finished:
            del data[self.ESTIMATED_TIME_LEFT]
        if self.error_message:
            data[self.ERROR_MESSAGE] = self.error_message
        return data

    def _message_api(self):
        self.communication.message_api(self.get_json())
        self._print_json()

    def _message_all(self):
        self.communication.message_all(self.get_json())

    def _message_telegram(self):
        current_time = datetime.now()
        elapsed_time = current_time - self.start_time
        elapsed_seconds = elapsed_time.total_seconds()
        average_transaction_time = (
            elapsed_seconds / len(self.transaction_curve)
            if self.transaction_curve
            else 0
        )

        self.communication.message_telegram(
            {
                "status": self.status,
                "current cycle": self.current_cycle,
                "batch size": self.batch_size,
                "total transferred": self.total_transferred,
                "total expected amount": self.total_expected_amount,
                "average tx duration": str(
                    timedelta(seconds=average_transaction_time)),
                "total time": self._format_time(
                    (datetime.now() - self.start_time).total_seconds()),
            }
        )
        if self.error_message:
            self.communication.message_telegram(
                {"error message": self.error_message})

    def _print_json(self):
        print(json.dumps(self.get_json(), indent=4))
