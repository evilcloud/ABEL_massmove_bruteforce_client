import npyscreen
from logic import run_logic
from threading import Thread
from transaction_tracker import TransactionData


# This form is responsible for displaying the output.
class MainForm(npyscreen.ActionFormMinimal):
    def create(self):
        self.single_amount = self.add(npyscreen.TitleText, name="Single Amount (default: 1000):", value="1000")
        self.batch_size = self.add(npyscreen.TitleText, name="Batch Size (default: 10):", value="10")
        self.progress = self.add(npyscreen.TitleSlider, out_of=100, name="Progress:")

    def on_ok(self):
        # Get values from the form and create the report instance
        self.parentApp.report = TransactionData(int(self.batch_size.value), float(self.single_amount.value))

    def while_waiting(self):
        # Update display based on the global state.
        report = self.parentApp.report.get_data()
        self.single_amount.value = str(report["single_amount"])
        self.batch_size.value = str(report["batch_size"])
        self.progress.value = report["transaction_count"] / report["batch_size"] * 100
        self.display()


# This is the main application.
class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.report = None
        self.addForm('MAIN', MainForm, name="ABEL brute force")


def run_tui():
    App = MyApp()
    AppThread = Thread(target=App.run)
    AppThread.start()

    while App.report is None:  # Wait until the form is filled
        pass

    # Add a print statement here
    print("Running the logic function now")

    # Run the logic, convert batch_size to an integer
    run_logic(int(App.report.get_data()["batch_size"]), App.report.get_data()["single_amount"])
