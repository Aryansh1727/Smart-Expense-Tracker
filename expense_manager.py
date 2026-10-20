
import json
from pathlib import Path
from datetime import date
from uuid import uuid4

class Transaction:
    """Represent a single income or expense transaction."""

    def __init__(
        self,
        amount,
        transaction_type,
        category,
        description,
        transaction_date,
    ):
        amount = float(amount)

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if transaction_type not in ("Income", "Expense"):
            raise ValueError("Type must be Income or Expense.")

        category = str(category).strip()
        description = str(description).strip()

        if not category:
            raise ValueError("Category cannot be empty.")

        parsed_date = date.fromisoformat(str(transaction_date))

        self.__transaction_id = str(uuid4())
        self.__amount = amount
        self.__transaction_type = transaction_type
        self.__category = category
        self.__description = description
        self.__transaction_date = parsed_date.isoformat()

    def to_dict(self):
        """Convert a transaction into a dictionary."""
        return {
            "id": self.__transaction_id,
            "amount": self.__amount,
            "type": self.__transaction_type,
            "category": self.__category,
            "description": self.__description,
            "date": self.__transaction_date,
        }

    @classmethod
    def from_dict(cls, record):
        """Create a transaction from a saved dictionary."""
        transaction = cls(
            amount=record["amount"],
            transaction_type=record["type"],
            category=record["category"],
            description=record.get("description", ""),
            transaction_date=record["date"],
        )

        # Preserve the original ID when loading or editing.
        transaction.__transaction_id = str(
            record.get("id") or uuid4()
        )

        return transaction

class ExpenseManager:
    """Manage transactions and save them in JSON format."""

    def __init__(self, data_file="data/transactions.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.transactions = []
        self.load_transactions()

    def load_transactions(self):
        """Load transactions without overwriting unreadable data."""
        if not self.data_file.exists():
            self.transactions = []
            return

        try:
            with self.data_file.open("r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                raise ValueError(
                    "Transaction data must be a JSON list."
                )

            loaded_transactions = [
                Transaction.from_dict(record)
                for record in records
            ]

            self.transactions = loaded_transactions

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
            # Do not replace a damaged file with an empty transaction list.
            raise ValueError(
                f"Unable to load transaction data from "
                f"{self.data_file}: {error}. "
                "The original file has been preserved."
            ) from error

    def save_transactions(self):
        """Save transactions safely using a temporary file."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        temporary_file = self.data_file.with_suffix(".tmp")

        try:
            with temporary_file.open("w", encoding="utf-8") as file:
                json.dump(
                    [
                        transaction.to_dict()
                        for transaction in self.transactions
                    ],
                    file,
                    indent=4,
                    ensure_ascii=False,
                )

            # Replace the previous file only after writing succeeds.
            temporary_file.replace(self.data_file)

        except OSError:
            if temporary_file.exists():
                temporary_file.unlink()
            raise

    def add_transaction(
        self,
        amount,
        transaction_type,
        category,
        description,
        transaction_date,
    ):
        """Add a new transaction and persist it."""
        transaction = Transaction(
            amount=amount,
            transaction_type=transaction_type,
            category=category,
            description=description,
            transaction_date=transaction_date,
        )

        self.transactions.append(transaction)

        try:
            self.save_transactions()
        except OSError:
            self.transactions.pop()
            raise

        return transaction

    def update_transaction(
        self,
        transaction_id,
        amount,
        transaction_type,
        category,
        description,
        transaction_date,
    ):
        """Edit an existing transaction while preserving its ID."""
        for index, existing in enumerate(self.transactions):
            if existing.to_dict()["id"] == transaction_id:
                updated = Transaction(
                    amount=amount,
                    transaction_type=transaction_type,
                    category=category,
                    description=description,
                    transaction_date=transaction_date,
                )

                updated_data = updated.to_dict()
                updated_data["id"] = transaction_id

                replacement = Transaction.from_dict(updated_data)
                self.transactions[index] = replacement

                try:
                    self.save_transactions()
                except OSError:
                    self.transactions[index] = existing
                    raise

                return True

        return False

    def delete_transaction(self, transaction_id):
        """Delete a transaction by its unique ID."""
        for index, transaction in enumerate(self.transactions):
            if transaction.to_dict()["id"] == transaction_id:
                removed = self.transactions.pop(index)

                try:
                    self.save_transactions()
                except OSError:
                    self.transactions.insert(index, removed)
                    raise

                return True

        return False

    def get_summary(self, month=None):
        """Calculate income, expenses, balance, and savings rate."""
        records = [
            transaction.to_dict()
            for transaction in self.transactions
            if month is None
            or transaction.to_dict()["date"].startswith(month)
        ]

        income = sum(
            record["amount"]
            for record in records
            if record["type"] == "Income"
        )

        expenses = sum(
            record["amount"]
            for record in records
            if record["type"] == "Expense"
        )

        balance = income - expenses
        savings_rate = (
            balance / income * 100 if income > 0 else 0.0
        )

        return {
            "income": income,
            "expenses": expenses,
            "balance": balance,
            "savings_rate": savings_rate,
        }

    def get_transactions(self):
        """Return all transactions as dictionaries."""
        return [
            transaction.to_dict()
            for transaction in self.transactions
        ]
