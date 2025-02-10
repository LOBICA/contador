from datetime import datetime
from decimal import Decimal

from .accounting import ChartOfAccounts
from .entities import Account, Book, Document, Entry, Payee, Transaction


class AccountManager:
    def __init__(self, book: Book):
        self.book = book
        self.chart = ChartOfAccounts(book)

    def put_expense(
        self, payable_account: Account, amount: Decimal
    ) -> tuple[Entry, Entry]:
        """Put expenses into a payable account"""
        credit = payable_account.credit(amount)
        debit = self.chart.expenses.debit(amount)  # Put money into expenses
        return (credit, debit)

    def get_revenue(
        self, receivable_account: Account, amount: Decimal
    ) -> tuple[Entry, Entry]:
        """Get money from revenue into a receivable account"""
        credit = self.chart.revenue.credit(amount)  # take money out of revenue
        debit = receivable_account.debit(amount)
        return (credit, debit)

    def add_expense_invoice(
        self,
        date: datetime.date,
        number: str,
        amount: Decimal,
        invoice_url: str,
        payee: Payee = None,
    ) -> Document:
        invoice = Document(
            date=date,
            number=number,
            type_="expense invoice",
            amount=amount,
            location=invoice_url,
            book=self.book,
            payee=payee,
        )

        transaction = Transaction(
            date=date,
            description=f"Invoice {number}",
            book=self.book,
        )

        transaction.add_entries(self.put_expense(self.chart.accounts_payable, amount))

        invoice.transactions.add(transaction)
        transaction.documents.add(invoice)

        return invoice

    def pay_invoices(
        self, invoices: list[Document], date: datetime.date, amount: Decimal
    ) -> Document:
        transaction = Transaction(
            date=date,
            description="Payment for invoices",
            book=self.book,
        )

        credit = self.chart.bank_account.credit(amount)
        debit = self.chart.accounts_payable.debit(amount)
        transaction.add_entries([credit, debit])

        for invoice in invoices:
            transaction.documents.add(invoice)
            invoice.transactions.add(transaction)

        return transaction

    def register_salary(
        self, date: datetime.date, amount: Decimal, payee: Payee
    ) -> Transaction:
        transaction = Transaction(
            date=date,
            description=f"Salary for {payee.name}",
            book=self.book,
        )

        transaction.add_entries(self.put_expense(self.chart.salaries, amount))

        return transaction

    def pay_salary(
        self,
        date: datetime.date,
        amount: Decimal,
        payee: Payee,
        tax_retention: Decimal = Decimal(0.0),
    ) -> Transaction:
        transaction = Transaction(
            date=date,
            description=f"Salary payment to {payee.name}",
            book=self.book,
        )

        credit = self.chart.bank_account.credit(amount)
        if tax_retention:
            tax = self.chart.taxes.credit(tax_retention)
        debit = self.chart.salaries.debit(amount + tax_retention)
        transaction.add_entries([credit, tax, debit])

        return transaction

    def add_sale_invoice(
        self,
        date: datetime.date,
        number: str,
        amount: Decimal,
        invoice_url: str,
        payee: Payee,
        tax_amount: Decimal = Decimal(0.0),
    ) -> Document:
        invoice = Document(
            date=date,
            number=number,
            type_="sale invoice",
            amount=amount,
            tax_amount=tax_amount,
            location=invoice_url,
            book=self.book,
            payee=payee,
        )

        transaction = Transaction(
            date=date,
            description=f"Invoice {number}",
            book=self.book,
        )

        transaction.add_entries(
            self.get_revenue(self.chart.accounts_receivable, amount)
        )
        if tax_amount:
            tax_credit = self.chart.taxes.credit(tax_amount)
            tax_debit = self.chart.accounts_receivable.debit(tax_amount)
            transaction.add_entries([tax_debit, tax_credit])

        invoice.transactions.add(transaction)
        transaction.documents.add(invoice)

        return invoice

    def receive_payment(
        self, invoices: list[Document], date: datetime.date, amount: Decimal
    ) -> Transaction:
        transaction = Transaction(
            date=date,
            description="Payment for invoices",
            book=self.book,
        )

        credit = self.chart.bank_account.debit(amount)
        debit = self.chart.accounts_receivable.credit(amount)
        transaction.add_entries([credit, debit])

        for invoice in invoices:
            transaction.documents.add(invoice)
            invoice.transactions.add(transaction)

        return transaction

    def pay_taxes(self, date: datetime.date, amount: Decimal) -> Transaction:
        transaction = Transaction(
            date=date,
            description="Payment for taxes",
            book=self.book,
        )

        credit = self.chart.bank_account.credit(amount)
        debit = self.chart.taxes.debit(amount)
        transaction.add_entries([credit, debit])

        return transaction

    def is_invoice_clear(self, invoice: Document) -> bool:
        """Check if entries on accounts payable and receivable are cleared"""
        entries = []
        for transaction in invoice.transactions.values():
            entries.extend(transaction.entries.values())

        account_payable_entries = []
        account_receivable_entries = []

        for entry in entries:
            if entry.account == self.chart.accounts_payable:
                account_payable_entries.append(entry)
            elif entry.account == self.chart.accounts_receivable:
                account_receivable_entries.append(entry)

        # If entries indicate a negative balance, the invoice is not clear
        if sum([entry.amount for entry in account_payable_entries]) < 0:
            return False

        # If entries indicate a positive balance, the invoice is not clear
        if sum([entry.amount for entry in account_receivable_entries]) > 0:
            return False

        return True
