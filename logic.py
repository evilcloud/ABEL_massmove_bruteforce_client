import desktop_interface as di
from transaction_tracker import TransactionTracker
from tqdm import tqdm
from message_dispatcher import MultiChannelCommunicator, Channel

TARGET_APP = "Your app name"

class Control:
    def __init__(self, single_amount, report: TransactionTracker):
        self.single_amount = single_amount
        self.report = report
        self.timeout = 30

    def t01_initial_entry(self):
        di.enter(self.single_amount)
        di.tab()
        di.enter()
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
                self.report.transaction_successful()
                return None
            if di.has_failed(screen_content):
                return di.get_failed_reason(screen_content)
            else:
                self.timeout -= 1
                di.pause(1)
        return "Popup timedout"

    def t04_return_to_beginning(self):
        di.tab(10)

def run_logic(single_amount: float, batch_size: int):
    communicator = MultiChannelCommunicator()
    report = TransactionTracker(batch_size, single_amount)

    print("Launching the process. Move the focus into position...")
    di.pause(5)
    di.app_in_focus(TARGET_APP)

    process = Control(single_amount, report)
    for cycle in tqdm(range(batch_size), desc="Processing transactions"):
        report.transaction_starting(cycle)
        communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])

        process.t01_initial_entry()
        process.t02_check_popup_v2()
        error = process.t03_main_popup()
        if error:
            report.transaction_failed(error)
            communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])
            break

        process.t04_return_to_beginning()
        report.transaction_completed()
        communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])

    report.session_completed()
    communicator.send_message(report.get_data(), [Channel.TELEGRAM, Channel.STDOUT])
    report.pretty_stdout()
