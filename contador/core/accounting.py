from .entities import Account, Book


class ChartOfAccounts:
    ACCOUNT_NAMES = [
        "Expenses",
        "Revenue",
        "Assets",
        "Liabilities",
        "Bank Account",
        "Salaries",
        "Taxes",
        "Accounts Payable",
        "Accounts Receivable",
    ]

    def __init__(self, book: Book):
        self.book = book

        self._chart = {name: None for name in self.ACCOUNT_NAMES}

        for account in book.accounts.values():
            if account.name in self._chart:
                self._chart[account.name] = account

        for name, account in self._chart.items():
            if not account:
                self._chart[name] = Account(name=name, book=book)

    @property
    def expenses(self) -> Account:
        return self._chart["Expenses"]

    @property
    def revenue(self) -> Account:
        return self._chart["Revenue"]

    @property
    def assets(self) -> Account:
        return self._chart["Assets"]

    @property
    def liabilities(self) -> Account:
        return self._chart["Liabilities"]

    @property
    def bank_account(self) -> Account:
        return self._chart["Bank Account"]

    @property
    def salaries(self) -> Account:
        return self._chart["Salaries"]

    @property
    def taxes(self) -> Account:
        return self._chart["Taxes"]

    @property
    def accounts_payable(self) -> Account:
        return self._chart["Accounts Payable"]

    @property
    def accounts_receivable(self) -> Account:
        return self._chart["Accounts Receivable"]
