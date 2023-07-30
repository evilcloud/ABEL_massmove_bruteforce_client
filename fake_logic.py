from transaction_tracker import TransactionTracker
from tqdm import tqdm
from message_dispatcher import MultiChannelCommunicator, Channel
import time
import random

def run_logic(single_amount: float, batch_size: int, report: TransactionTracker):
    communicator = MultiChannelCommunicator()

    print("Simulating the process...")
    time.sleep(5)

    for cycle in tqdm(range(batch_size), desc="Processing transactions"):
        time.sleep(1)  # Simulate some delay
        report.transaction_starting(cycle)
        communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])

        time.sleep(1)  # Simulate some delay
        if random.random() < 0.05:  # 5% chance of a transaction failing
            report.transaction_failed("Random error")
            communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])
            break

        time.sleep(1)  # Simulate some delay
        report.transaction_successful()
        communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])

    report.session_completed()
    communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])
    report.pretty_stdout()
