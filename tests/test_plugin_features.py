"""Test file for new plugin features"""

class BankAccount:
    def __init__(self):
        self.balance = 0
        self.account_number = "123"
        self._internal_id = "xyz"

    def deposit(self, amount):
        self.balance += amount

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount

class Order:
    def __init__(self):
        self.customer_name = ""
        self.customer_address = ""
        self.customer_phone = ""
        self.total = 0

class Invoice:
    def __init__(self):
        self.customer_name = ""
        self.customer_address = ""
        self.customer_phone = ""
        self.amount = 0
