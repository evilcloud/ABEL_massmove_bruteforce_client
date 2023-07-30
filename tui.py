import npyscreen
from logic import run_logic
from threading import Thread
from transaction_tracker import TransactionTracker

# This form is responsible for displaying the output.
class MainForm(npyscreen.Form):
    def create(self):
        self.single_amount = self.add(npyscreen.TitleText, name="Single Amount:")
        self.batch_size = self.add(npyscreen.TitleText, name="Batch Size:")
        self.progress = self.add(npyscreen.TitleSlider, out_of=100, name="Progress:")

    def while_waiting(self):
        # Update display based on the global state.
        self.single_amount.value = str(report.single_amount)
        self.batch_size.value = str(report.batch_size)
        self.progress.value = report.transaction_count / report.batch_size * 100
        self.display()

# This is the main application.
class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', MainForm, name="MyApp")

if __name__ == "__main__":
    App = MyApp()
    AppThread = Thread(target=App.run)
    AppThread.start()

    # Update these values according to your requirements.
    single_amount = 1000
    batch_size = 10

    # Create an instance of TransactionTracker
    report = TransactionTracker(batch_size, single_amount)

    run_logic(single_amount, batch_size, report)  # Run the logic
