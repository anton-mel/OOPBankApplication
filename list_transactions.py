import tkinter as tk

class TransactionsGUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Create widgets for displaying transactions
        self.transactions_label = tk.Label(self, text="Transactions", font=("TkDefaultFont", 14, "bold"))
        self.transactions_label.pack(anchor="w")

        # Empty List of Transaction
        self.empty_label = tk.Label(self, text="No transactions.")
        self.empty_label.pack(anchor="w")

        self._transaction_labels = []

    def update_transactions(self, transactions):
        self.clear_transactions()

        # If no transactions
        if not transactions:
            self.empty_label.pack()
        else:
            self.empty_label.pack_forget()

        for transaction in transactions:
            text = f"Date: {transaction.date}\nAmount: ${transaction.amount:.2f}"
            label = tk.Label(self, text=text, compound="top", justify="left")

            if transaction.amount >= 0:
                label.config(fg="lime")
            else:
                label.config(fg="red")

            label.pack(anchor="w", pady=3)
            self._transaction_labels.append(label)

    def clear_transactions(self):
        for label in self._transaction_labels:
            label.pack_forget()
            label.destroy()
