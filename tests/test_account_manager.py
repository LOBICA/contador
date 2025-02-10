from datetime import datetime
from decimal import Decimal

from contador.core.entities import Book, Payee
from contador.core.manager import AccountManager


def test_create_account_manager(book: Book):
    manager = AccountManager(book)
    assert manager
    assert manager.book is book
    assert manager.chart
    assert manager.chart.expenses
    assert manager.chart.revenue
    assert manager.chart.assets
    assert manager.chart.liabilities
    assert manager.chart.bank_account
    assert manager.chart.salaries
    assert manager.chart.taxes
    assert manager.chart.accounts_payable
    assert manager.chart.accounts_receivable


def test_repr_account_manager(account_manager: AccountManager):
    """Testing if the objet representation doesn't hang the process"""
    date = datetime.now().date()

    n = 10
    amount = 100.0
    for i in range(n):
        invoice = account_manager.add_expense_invoice(
            date, str(i), Decimal(100.0), "//invoice"
        )
        account_manager.pay_invoices([invoice], date, Decimal(amount))

    repr(account_manager.chart.bank_account)
    assert account_manager.chart.bank_account.balance == -1 * Decimal(n * amount)


def test_accounting(account_manager: AccountManager):
    initial_balance = Decimal(1000.0)
    account_manager.chart.bank_account.initial_balance = initial_balance
    date = datetime.now().date()

    # Register salaries
    salary1 = Decimal(350.0)
    account_manager.register_salary(
        date=date, amount=salary1, payee=Payee(name="Employee 1")
    )
    salary2 = Decimal(400.0)
    account_manager.register_salary(
        date=date, amount=salary2, payee=Payee(name="Employee 2")
    )
    assert account_manager.chart.salaries.balance == -1 * (salary1 + salary2)

    # Register expenses
    expense_invoice_1 = account_manager.add_expense_invoice(
        date=date,
        number="00001",
        amount=Decimal(100.0),
        invoice_url="//invoice1",
        payee=Payee(name="Vendor 1"),
    )
    expense_invoice_2 = account_manager.add_expense_invoice(
        date=date,
        number="00002",
        amount=Decimal(150.0),
        invoice_url="//invoice2",
        payee=Payee(name="Vendor 2"),
    )
    assert account_manager.chart.accounts_payable.balance == -1 * (
        expense_invoice_1.amount + expense_invoice_2.amount
    )
    assert account_manager.is_invoice_clear(expense_invoice_1) is False
    assert account_manager.is_invoice_clear(expense_invoice_2) is False

    # Register revenue
    sale_amount = Decimal(500)
    sale_taxes = sale_amount * Decimal(0.13)
    sale_invoice_1 = account_manager.add_sale_invoice(
        date=date,
        number="00001",
        amount=sale_amount,
        tax_amount=sale_taxes,
        invoice_url="//sale1",
        payee=Payee(name="Customer 1"),
    )
    assert account_manager.chart.accounts_receivable.balance == sale_amount + sale_taxes
    assert sale_invoice_1.amount == sale_amount
    assert sale_invoice_1.tax_amount == sale_taxes
    assert account_manager.is_invoice_clear(sale_invoice_1) is False

    # Pay salaries
    tax_retention1 = salary1 * Decimal(0.1)
    payment1 = salary1 - tax_retention1
    account_manager.pay_salary(
        date,
        amount=payment1,
        tax_retention=tax_retention1,
        payee=Payee(name="Employee 1"),
    )

    tax_retention2 = salary2 * Decimal(0.1)
    payment2 = salary2 - tax_retention2
    account_manager.pay_salary(
        date,
        amount=payment2,
        tax_retention=tax_retention2,
        payee=Payee(name="Employee 2"),
    )
    assert account_manager.chart.salaries.balance == 0
    new_balance = initial_balance - payment1 - payment2
    assert account_manager.chart.bank_account.balance == new_balance

    # Pay invoices
    account_manager.pay_invoices(
        invoices=[expense_invoice_1, expense_invoice_2],
        date=date,
        amount=expense_invoice_1.amount + expense_invoice_2.amount,
    )
    assert account_manager.chart.accounts_payable.balance == 0
    new_balance -= expense_invoice_1.amount + expense_invoice_2.amount
    assert account_manager.chart.bank_account.balance == new_balance
    assert account_manager.is_invoice_clear(expense_invoice_1) is True
    assert account_manager.is_invoice_clear(expense_invoice_2) is True

    # Receive payment
    account_manager.receive_payment(
        invoices=[sale_invoice_1],
        date=date,
        amount=sale_invoice_1.amount + sale_invoice_1.tax_amount,
    )
    assert account_manager.chart.accounts_receivable.balance == 0
    new_balance += sale_invoice_1.amount + sale_invoice_1.tax_amount
    assert account_manager.chart.bank_account.balance == new_balance
    assert account_manager.is_invoice_clear(sale_invoice_1) is True

    # Pay taxes
    owed_taxes = tax_retention1 + tax_retention2 + sale_taxes
    assert account_manager.chart.taxes.balance == -1 * owed_taxes
    account_manager.pay_taxes(date, owed_taxes)
    assert account_manager.chart.taxes.balance == 0
    new_balance -= owed_taxes
    assert account_manager.chart.bank_account.balance == new_balance
