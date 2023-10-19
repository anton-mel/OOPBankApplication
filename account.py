import tkinter as tk
from accounts import SavingsAccount

class AccountItem(tk.Frame):
    """Graphics for the account item."""

    def __init__(self, parent, account, select_callback):
        super().__init__(parent)
        self._account = account
        self._select_callback = select_callback

        self.create_widgets()

    def create_widgets(self):
        text = f"ID: {self.format()}\nBalance: ${self._account.get_balance():.2f}"
        
        # Check Polymorphism
        account_type = "Savings" if isinstance(self._account, SavingsAccount) else "Checkings"
        text += f"\n{account_type}"

        label = tk.Radiobutton(self, text=text, value=self._account.id, compound="top", padx=5, justify="left")
        label.pack(anchor="w", pady=3)
        label.bind("<Button-1>", self.handle_select)

    def handle_select(self, event):
        self._select_callback(self._account.id)

    def format(self):
        """Formats the account number and balance of the account.
        For example, '#000000001,<tab>balance: $50.00'
        """
        return f"#{self._account.id:09}"
