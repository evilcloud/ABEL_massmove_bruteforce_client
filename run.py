import desktop_interface as di
from transaction_data import TransactionData
import os
from tqdm import tqdm


class Control:
    def __init__(self, single_amount, api_master_pass, report: TransactionData):
        self.single_amount = single_amount
        self.api_master_pass = api_master_pass
        self.report = report
        self.timeout = 30

    def t01_initial_entry(self):
        di.enter(self.single_amount)
        di.tab()
        di.enter(self.api_master_pass)
        di.tab()
        di.enter()

    def t02_check_popup_v2(self):
        di.tab(2)
        di.enter()

    def t03_main_popup(self):
        self.timeout = 30
        while self.timeout:
            screen_content = di.get_clipboard()
            if di.is_submitted(screen_content):
                di.tab()
                di.enter()
                report.transaction_successful()
                return None
            if di.has_failed(screen_content):
                return di.get_failed_reason(screen_content)
            else:
                # report.transaction_pending()
                self.timeout -= 1
                di.pause(1)
        return "Popup timedout"

    def t04_return_to_beginning(self):
        di.tab(10)


def run_wallet(single_amount: float, api_master_pass: str, report: TransactionData, batch_size: int, target_app: str):
    print("Launching the process. Move the focus into position...")
    di.pause(5)
    di.app_in_focus(target_app)

    process = Control(single_amount, api_master_pass, report)
    for cycle in tqdm(range(batch_size), desc="Processing transactions"):
        report.transaction_starting(cycle)

        # print(f"Cycle {cycle + 1} / {batch_size}")
        process.t01_initial_entry()
        process.t02_check_popup_v2()
        error = process.t03_main_popup()
        if error:
            report.transaction_failed(error)
            break

        process.t04_return_to_beginning()
        report.transaction_completed()
    report._print_json()


api_master_pass = os.environ["API_MASTER_PASS"]
batch_size = 3
single_amount = 1000

single_amount = int(
    input(f"Enter single amount (default: {single_amount}): ") or single_amount
)
batch_size = int(input(f"Enter batch size (default: {batch_size}): ") or batch_size)

target_app = "abelian-wallet-desktop"
report = TransactionData(batch_size, single_amount)
run_wallet(single_amount, api_master_pass, report, batch_size, target_app)
