from transaction_data import TransactionData
from navigation import Navigation
from tqdm import tqdm
import os
import logging
import json

logging.basicConfig(level=logging.INFO)
# logging.disable(logging.CRITICAL)


def popup_state(payload_data, navigation):
    attempts = navigation.attempts_with_no_sign
    while attempts > 0:
        navigation.pause()
        clipboard_content = navigation.extract_clipboard()
        if not navigation.in_popup():
            logging.info("Popup not found")
            payload_data.update_failed("Popup collapsed")
            return False
        elif any(
            symbol in clipboard_content for symbol in ["⏳", "⌛", "Unlocking account"]
        ):
            logging.info("Waiting for transaction to be signed")
            payload_data.update_running()
            navigation.pause()
            attempts = navigation.attempts_with_no_sign
            continue
        elif "✅ Transaction submitted." in clipboard_content:
            logging.info("Transaction submitted")
            payload_data.update_transacted()
        elif "❌" in clipboard_content:
            logging.info("Transaction failed")
            error_messages = {
                "Failed getting balance": "Wallet is not connected",
                "Insufficient balance": "Balance insufficient",
            }

            error_message = next(
                (
                    error_messages[key]
                    for key in error_messages
                    if key in clipboard_content
                ),
                "Transaction failed",
            )
            payload_data.update_failed(error_message)
        else:
            logging.info("No expected symbols found")
            attempts -= 1

        closed_popup = navigation.close_popup()
        if not closed_popup:
            logging.info("Failed to close popup")
            payload_data.update_failed("Failed to close popup")
        return closed_popup

    logging.info("Too many consecutive attempts with no expected symbols")
    payload_data.update_failed("Too many consecutive attempts with no expected symbols")
    return False


def perform_transaction(api_master_pass, amount, batch_size, payload_data, navigation):
    batch = tqdm(range(batch_size), desc="Batch", position=0)

    payload_data.update_starting(0)
    for cycle in batch:
        payload_data.update_starting(cycle + 1)
        navigation.app_in_focus()
        navigation.type(str(amount))  # single amount
        navigation.tab()
        navigation.type(api_master_pass)  # master password
        navigation.tab()
        navigation.enter()
        if not popup_state(payload_data, navigation):
            break
        # if payload_data.status == "failed":  # Check if the transaction failed
        #     break  # Break out of the loop if failed
        if payload_data.status == "failed":
            break  # Replace the commented code with this line
        for _ in range(7):
            navigation.tab()
        payload_data.update_completed()
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
