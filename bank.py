import logging
from accounts import SavingsAccount, CheckingAccount

from decimal import Decimal
from datetime import datetime

from db import dataBase
from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship


SAVINGS = "savings"
CHECKING = "checking"

class Bank(dataBase):

    __tablename__ = "banks"

    _id = Column(Integer, primary_key=True)
    _accounts = relationship("Account")
    
    def add_account(self, acct_type, session):
        """Creates a new Account object and adds it to this bank object. The Account will be a SavingsAccount or CheckingAccount, depending on the type given.

        Args:
            type (string): "Savings" or "Checking" to indicate the type of account to create
        """
        acct_num = self._generate_account_number()
        if acct_type == SAVINGS:
            a = SavingsAccount(acct_num)
        elif acct_type == CHECKING:
            a = CheckingAccount(acct_num)
        else:
            return None
        
        self._accounts.append(a)

        try:
            self._session.add(a)
            logging.debug("Account added to session.")
        except Exception as e:
            logging.error(f"Error adding account to session: {e}")

    def _generate_account_number(self):
        return len(self._accounts) + 1

    def show_accounts(self):
        "Accessor method to return accounts"
        return self._accounts

    def get_account(self, account_num):
        """Fetches an account by its account number.

        Args:
            account_num (int): account number to search for

        Returns:
            Account: matching account or None if not found
        """        

        for x in self._accounts:
            if x._account_number == account_num:
                return x
        return None
