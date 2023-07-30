import os
import json
from transaction_tracker import TransactionData
from wallet_manager import WalletManager


def run_wallet(api_master_pass: str, batch_size, single_amount,
               wallet: WalletManager, report: TransactionData):
    print("Launching the process. Move the focus into position...")
    wallet.control.pause()
    wallet.control.app_in_focus()

    # Initial entry:
    for cycle in range(batch_size):
        report.transaction_starting(cycle + 1)

        wallet.control.type(str(single_amount))
        wallet.control.tab()
        wallet.control.type(api_master_pass)
        wallet.control.pause()
        wallet.control.tab()
        wallet.control.enter()

        # TODO: implement the return check, in order to accomodate the failed cases
        # that could be salvaged by closing the popup
        if not popup_section(report, wallet):
            break
        if report.status == "failed":
            break
        wallet.control.pause(1)
        wallet.control.tab(10)
        report.transaction_completed()


def popup_section(report: TransactionData, wallet: WalletManager):
    attempts = wallet.control.attempts_with_no_sign
    wallet.control.pause()
    aborted_attempts = 0
    while attempts > 0:
        wallet.control.confirmation_popup()
        screen_content = wallet.control.extract_clipboard()  # we don't want to run this too often
        if not wallet.control.in_popup():
            report.transaction_failed("Failed to open popup")
            return False
        if wallet.symbols.pending(screen_content):
            report.transaction_pending()
            wallet.control.pause()
            # Resetting attempts countdown as the operations are running normally
            attempts = wallet.control.attempts_with_no_sign
            continue  # no need for the rest of the code. Repeat
        elif wallet.symbols.submitted(screen_content):
            report.transaction_successful()
            break
            # Transaction is completed, but we have to just break to close popup
        # This final one checks both for failure or lack of information
        # The definitive failure gives the program some closure by ending this cycle
        elif failure_reason := wallet.symbols.failed_reason(screen_content):
            report.transaction_failed(failure_reason)
            if "Connection aborted" in failure_reason:
                if aborted_attempts > 5:
                    break
                else:
                    report.transaction_failed(f"Connection aborted Nr. {aborted_attempts}")
                    aborted_attempts += 1
            aborted_attempts = 0
        # If none of the above, then the transaction is still processing
        # Attempts will always decrease while in this loop (reset if waiting)
        wallet.control.pause(1)
        attempts -= 1
    # Having left the wheel of samsara we are not done - we are still in the popup
    # closing which is a challenge of its own. Luckily we have the higher powers
    # to help us with that
    closed_popup = wallet.control.close_popup()
    if not closed_popup:
        report.transaction_failed("Failed to close popup")
        return False
    return True


api_master_pass = os.environ["API_MASTER_PASS"]
batch_size = 3
single_amount = 1000

single_amount = int(
    input(f"Enter single amount (default: {single_amount}): ") or single_amount
)
batch_size = int(input(f"Enter batch size (default: {batch_size}): ") or batch_size)

wallet = WalletManager("abelian-wallet-desktop")
report = TransactionData(batch_size, single_amount)
try:
    run_wallet(api_master_pass, batch_size, single_amount, wallet, report)
    report.session_completed()
except Exception as e:
    if e == KeyboardInterrupt:
        report.error_message = "Keyboard interrupt"
    else:
        report.error_message = str(e)
    report.session_failed()
finally:
    print("---DONE---")
