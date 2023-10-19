# iOS MacBook Air

import logging
from decimal import Decimal, setcontext, BasicContext, InvalidOperation
from datetime import datetime

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
from db import dataBase
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import create_engine

from bank import Bank
from exceptions import OverdrawError, TransactionLimitError, TransactionSequenceError

from list_accounts import AccountList
from list_transactions import TransactionsGUI

# context with ROUND_HALF_UP
setcontext(BasicContext)

logging.basicConfig(filename='bank.log', level=logging.DEBUG,
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class BankGUI:
    """Driver class for a graphic interface to the Bank application"""

    @staticmethod
    def handle_exception(exception_type, exception, traceback):
        error_message = f"An exception of type {exception_type.__name__} occurred with the following message: {exception}"
        print(error_message)  # Print the error message
        logging.error(error_message)  # Log the error message

    def __init__(self):
        # Create the window
        self._window = tk.Tk()
        self._window.title("My Bank")
        self._window.resizable(False, False)

        # Create a session
        self._session = Session()

        # Create or retrieve the bank object
        try:
            self._bank = self._session.query(Bank).first()
            logging.debug("Existing bank requested successfully.")
        except Exception as e:
            logging.error(f"Error requesting bank from the database: {e}")

        if not self._bank:
            self._bank = Bank()
            
            try:
                self._session.add(self._bank)
                logging.debug("Bank added to session.")
            except Exception as e:
                logging.error(f"Error adding bank to session: {e}")

            try:
                self._session.commit()
                logging.debug("Bank session committed successfully.")
            except Exception as e:
                logging.error(f"Error committing bank to the database: {e}")

        self._selected_account = None

        # Create the GUI content
        self.create_gui()

    def create_gui(self):
        """Function to Generate Main GUI page."""

        # Frame for GUI content & Styles
        self._gui = tk.Frame(self._window, padx=20, pady=10)
        self._gui.grid(row=2, column=0, columnspan=4)

        # Bank Header Options
        self.acct_type = tk.StringVar(value="Open Account")
        account_type_combo = ttk.Combobox(self._gui, textvariable=self.acct_type, values=["Savings", "Checking"], state="readonly")
        account_type_combo.bind("<<ComboboxSelected>>", self._open_account)
        account_type_combo.grid(row=1, column=1, columnspan=2)

        tk.Button(self._gui, text="Add Transaction", command=self._add_transaction).grid(row=1, column=3, columnspan=2)
        tk.Button(self._gui, text="Interest and Fees", command=self._monthly_triggers).grid(row=1, column=5, columnspan=2)
        self._gui.pack()

        # Create a frame for displaying transactions
        self._transaction = TransactionsGUI(self._gui) 
        self._transaction.grid(row=2, column=3, columnspan=3, sticky="wn")
        self._transaction.configure(pady=10)
        self._list_transactions()

        # Create a frame for displaying accounts
        self._body = AccountList(self._gui, self._select) 
        self._body.grid(row=2, column=1, columnspan=2, sticky="wn")
        self._body.configure(pady=10)
        self._summary()

        self._window.mainloop()

    def _open_account(self, event):
        acct_type = self.acct_type.get().lower()
        self._bank.add_account(acct_type, self._session)
        self.acct_type.set("Open Account")
        try:
            self._session.commit()
            logging.debug("Bank session committed successfully.")
        except Exception as e:
            logging.error(f"Error comitting bank to the database: {e}")

        # Update Accounts
        self._summary()

    def _list_transactions(self):
        if self._selected_account is not None:
            transactions = self._selected_account.get_transactions()
            self._transaction.update_transactions(transactions)  # Update Transactions

    def _summary(self):
        accounts = self._bank.show_accounts()
        self._body.add_account(accounts)

    def _select(self, num):
        self._selected_account = self._bank.get_account(num)
        self._list_transactions()

    def _add_transaction(self):
        """GUI and handling the trasaction function"""

        # New Window
        self._transaction_window = tk.Toplevel(self._window, padx=20, pady=20)
        self._transaction_window.title("Add Transaction")
        self._transaction_window.resizable(False, False)

        # Widget
        amount_label = tk.Label(self._transaction_window, text="Enter Amount:")
        amount_label.pack()

        self.amount_var = tk.StringVar()

        amount_entry = tk.Entry(self._transaction_window, textvariable=self.amount_var)
        amount_entry.pack()

        # One of possible eventt listeners is trace_add. For every change we call function _validate_amount
        self.amount_var.trace_add("write", lambda *args, widget=amount_entry: self._validate_amount(widget))

        date_label = tk.Label(self._transaction_window, text="Select Date:", pady=5)
        date_label.pack()

        # Create the Calendar widget
        date_picker = Calendar(self._transaction_window, selectmode="day", date_pattern="yyyy-mm-dd")
        date_picker.pack()

        ok_button = tk.Button(self._transaction_window, text="OK", command=lambda: self._process_transaction(amount_entry, date_picker))
        ok_button.pack()
    
    def _validate_amount(self, amount_entry):
        """Check whether given transaction amount is suitable."""

        amount = self.amount_var.get()
        try:
            Decimal(amount)
            amount_entry.configure({"highlightbackground": "lime"})
        except InvalidOperation:
            amount_entry.configure({"highlightbackground": "red"})

    def _process_transaction(self, amount_entry, date_picker):
        """Handle adding the transaction."""

        amount = amount_entry.get()
        selected_date_str = date_picker.get_date()

        try:
            amount = Decimal(amount)

            # Convert the selected_date string to a date object
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()

            if self._selected_account is None:
                messagebox.showinfo("Error", "This command requires that you first select an account.")
                self._transaction_window.destroy()

            else:
                self._selected_account.add_transaction(amount, selected_date, self._session)

                try:
                    self._session.commit()
                    logging.debug("Session for transactions committed successfully.")
                except Exception as e:
                    logging.error(f"Error comitting transactions to the database: {e}")

                self._transaction_window.destroy()

                self._summary()
                self._list_transactions()
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid date in the format YYYY-MM-DD.")
        except InvalidOperation:
            messagebox.showwarning("Error", "Please enter a valid dollar amount.")
        except OverdrawError:
            messagebox.showwarning("Error", "This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError as ex:
            messagebox.showwarning("Error", f"This transaction could not be completed because this account already has {ex.limit} transactions in this {ex.limit_type}.")
        except TransactionSequenceError as ex:
            messagebox.showwarning("Error", f"New transactions must be from {ex.latest_date} onward.")

    def _monthly_triggers(self):
        try:
            self._selected_account.assess_interest_and_fees(self._session)
            
            try:
                self._session.commit()
                logging.debug("Fees and Interest session committed successfully.")
            except Exception as e:
                logging.error(f"Error comitting Fees and Interest to the database: {e}")

            self._list_transactions()
            self._summary()
            logging.debug("Triggered interest and fees")
        except AttributeError:
            messagebox.showwarning("Error", "This command requires that you first select an account.")
        except TransactionSequenceError as e:
            messagebox.showwarning("Error", f"Cannot apply interest and fees again in the month of {e.latest_date.strftime('%B')}.")
        except ValueError:
            messagebox.showwarning("Error", "This command requires that you first add the transaction.")


if __name__ == "__main__":
    engine = create_engine(f"sqlite:///bank.db")
    dataBase.metadata.create_all(engine)
    Session = sessionmaker(engine)

    try:
        BankGUI()
    except Exception as e:
        messagebox.showwarning("Error", "Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(str(e.__class__.__name__) + ": " + repr(str(e)))


