import os
import json
from transaction_data import TransactionData
from wallet_manager import WalletManager

def run_wallet(api_master_pass: str, batch_size, single_amount, wallet: WalletManager, report: TransactionData):
    """
    Entry point for the desktop wallet control. This function deals purley
    with the logic, while the navigation, data capture and temporal controls
    are executed from its own class(es) in library.
    One complex part - navigations and operations with the transactions within
    its own popup are executed ina separate function.

    The main steps are:
    1. Preparations
    2. Initial entry (amount, master pass, confirmation)
    3. Transaction section (done in a separate function)
    4. Returning to the initial position (7 tabs)
    5. Report of completion of the cycle
    6. Move to the next cycle or final report and exit if done or failed
    """
    # Preparations:
    # 1. Wait couple of seconds to let the user move the focus into the app
    # 2. Check if the app is in focus
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
        for _ in range(7):
            wallet.control.tab()
        report.transaction_completed()




def popup_section(report: TransactionData, wallet: WalletManager):
    """
    This function deals with the popup section of the transaction.
    After having validated the position, it launches a loop.
    Within that loop it captures the content of the screen (processing
    is done in another library) and first checks if we are in the popup at all.
    if not, it reports the failure and leaves the function.
    If the popup displays symbols of pending transaction, this state is reported,
    the rest of the loop is ignored the loop is repeated (after the wait)
    If the popup displays symbols of successful transaction, this state is reported
    and returned True
    If the popup displays symbols of failed transaction, the reason for failure
    is reported and the function is exited with False return
    If none of this is the case, the case is considered pending, but potentially
    problematic. The counter is engaged (limited by predetermined number of attempts),
    and the loop repeats.
    Once the number of allowed attempts have been exhausted, the function will report
    failure and will attempt to close the popup.

    :param report:
    :return:
    """
    attempts = wallet.control.attempts_with_no_sign
    wallet.control.pause()
    while attempts > 0:
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
        # The definetive failure gives the program some closure by ending this cycle
        elif failure_reason := wallet.symbols.failed_reason(screen_content):
            report.transaction_failed(failure_reason)
            break
        # If none of the above, then the transaction is still processing
        # Attempts will always decrease while in this loop (reset if waiting)
        wallet.control.pause(1)
        attempts -= 1
    # Having left the wheel of samsara we are not done - we are still in the popup
    # closing which is a challenge of its own. Luckily we have the higher powers
    # to help us with that
    closed_popup = wallet.control.close_popup()
    report._print_json()
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

run_wallet(api_master_pass, batch_size, single_amount, wallet, report)

print(json.dumps(report.get_json(), indent=4))
