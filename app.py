from transaction_data import TransactionData
from navigation import Navigation
from tqdm import tqdm
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
# logging.disable(logging.CRITICAL)


def process_popup(payload_data, navigation):
    attempts = navigation.attempts_with_no_sign
    while attempts > 0:
        navigation.pause()
        if not navigation.screen.is_popup():
            payload_data.transaction_failed("Popup collapsed")
            return False
        elif navigation.screen.transaction_processing():
            payload_data.transaction_pending()
            navigation.pause()
            # Resetting attempts countdown as the operations are running normally
            attempts = navigation.attempts_with_no_sign
            # Transaction is still processing, so there is no need for the rest of the function to run yet
            continue
        elif navigation.screen.transaction_submitted(navigation.extract_clipboard()):
            payload_data.transaction_successful()
        elif navigation.screen.is_transaction_failed(navigation.extract_clipboard()):
            payload_data.transaction_failed(
                navigation.screen.transaction_failure_reason(
                    navigation.extract_clipboard()
                )
            )
        attempts -= 1
        closed_popup = navigation.close_popup()
        if not closed_popup:
            payload_data.transaction_failed("Failed to close popup")
            break


def perform_transaction(api_master_pass, amount, batch_size, payload_data, navigation):
    batch = tqdm(range(batch_size), desc="Batch", position=0)

    payload_data.transaction_starting(0)
    for cycle in batch:
        payload_data.transaction_starting(cycle + 1)
        navigation.app_in_focus()
        navigation.type(str(amount))  # single amount
        navigation.tab()
        navigation.type(api_master_pass)  # master password
        navigation.tab()
        navigation.enter()
        if not process_popup(payload_data, navigation):
            break
        if payload_data.status == "failed":
            break
        for _ in range(7):
            navigation.tab()
        closed_popup = navigation.close_popup()
        if not closed_popup:
            payload_data.transaction_failed("Failed to close popup")
            break
        payload_data.transaction_completed()
    print(json.dumps(payload_data.get_json(), indent=4))


api_master_pass = os.environ["API_MASTER_PASS"]

batch_size = 2
single_amount = 1000

single_amount = int(
    input(f"Enter single amount (default: {single_amount}): ") or single_amount
)

batch_size = int(input(f"Enter batch size (default: {batch_size}): ") or batch_size)
navigation = Navigation()

payload_data = TransactionData(batch_size, single_amount)

navigation.app_in_focus()

perform_transaction(
    api_master_pass, single_amount, batch_size, payload_data, navigation
)
