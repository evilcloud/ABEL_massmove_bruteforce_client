import os
import json
from navigation import Navigation
from transaction_data import TransactionData


def run_wallet(api_master_key: str, batch_size, single_amount, navigation: Navigation, report: TransactionData):
    """
    Entry point for the desktop wallet control. This function deals purley
    with the logic, while the navigation, data capture and temporal controls
    are executed from it's own class(es) in library.
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
    navigation.pause()
    navigation.app_in_focus()

    # Initial entry:
    for cycle in range(batch_size):
        report.transaction_starting(cycle + 1)
        navigation.enter(single_amount)
        navigation.tab()
        navigation.enter(api_master_key)
        navigation.pause()
        navigation.enter()

        # TODO: implement the return check, in order to accomodate the failed cases
        # that could be salvaged by closing the popup
        popup_section(report, navigation)
        if report.status == "failed":
            break
        for _ in range(7):
            navigation.tab()
        report.transaction_completed()
    return



def popup_section(report: TransactionData, navigation: Navigation):
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
    attempts = navigation.attempts_with_no_sign
    navigation.pause()
    while attempts > 0:
        screen_content = navigation.screen.capture_data()  # we don't want to run this too often
        if not navigation.in_popup():
            report.transaction_failed("Failed to open popup")
            return False
        if navigation.symbol.pending(screen_content):
            report.transaction_pending()
            navigation.pause(2)
            # Resetting attempts countdown as the operations are running normally
            attempts = navigation.attempts_with_no_sign
            continue  # no need for the rest of the code. Repeat
        elif navigation.symbol.submitted(screen_content):
            report.transaction_successful()
            # Transaction is completed, so we can exit the section
            return True
        # This final one checks both for failure or lack of information
        # The definetive failure gives the program some closure by ending this cycle
        elif failure_reason := navigation.symbol.failed_reason(screen_content):
            report.transaction_failed(failure_reason)
            return False
        # If none of the above, then the transaction is still processing
        # Attempts will always decrease while in this loop (reset if waiting)
        navigation.pause(2)
        attempts -= 1
    # Having left the wheel of samsara we are not done - we are still in the popup
    # closing which is a challenge of it's own. Luckily we have the higher powers
    # to help us with that
    closed_popup = navigation.close_popup()
    if not closed_popup:
        report.transaction_failed("Failed to close popup")
        return False
    return True



api_master_key = os.environ["API_MASTER_KEY"]
batch_size = 3
single_amount = 1000

single_amount = int(
    input(f"Enter single amount (default: {single_amount}): ") or single_amount
)
batch_size = int(input(f"Enter batch size (default: {batch_size}): ") or batch_size)

navigation = Navigation()
report = TransactionData(batch_size, single_amount)

run_wallet(api_master_key, batch_size, single_amount, navigation, report)

print(json.dumps(report.get_json(), indent=4))
