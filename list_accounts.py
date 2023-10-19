import tkinter as tk
from account import AccountItem

class AccountList(tk.Frame):
    """Graphics for accounts."""

    def __init__(self, parent, select_callback):
        super().__init__(parent)

        self._select_callback = select_callback
        self._account_labels = []

        self.transactions_label = tk.Label(self, text="Accounts", font=("TkDefaultFont", 14, "bold"))
        self.transactions_label.pack(anchor="w")

        self.empty_label = tk.Label(self, text="No accounts found.")
        self.empty_label.pack(anchor="w")

    def clear_accounts(self):
        for label in self._account_labels:
            label.destroy()
        self._account_labels = []

    def add_account(self, accounts):
        self.clear_accounts()

        if not accounts:
            self.empty_label.pack()
        else:
            self.empty_label.pack_forget()

        for account in accounts:
            account_item = AccountItem(self, account, self._select_callback)
            account_item.pack(fill="x")
            self._account_labels.append(account_item)
