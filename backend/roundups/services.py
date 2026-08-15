from decimal import Decimal

from django.db import IntegrityError, transaction as db_transaction

from .models import RoundupLedgerEntry, Transaction
from .roundup_math import calculate_roundup


def ingest_transactions(user, bank_item, plaid_transactions):
    """Persist newly-synced Plaid transactions and generate round-up ledger
    entries for them. Idempotent: re-syncing the same transaction is a no-op
    thanks to the unique plaid_transaction_id constraint.

    Returns the number of new transactions ingested.
    """
    created_count = 0
    for txn in plaid_transactions:
        try:
            with db_transaction.atomic():
                transaction = Transaction.objects.create(
                    user=user,
                    bank_item=bank_item,
                    plaid_transaction_id=txn.transaction_id,
                    merchant_name=txn.merchant_name,
                    category=txn.category,
                    amount=txn.amount,
                    date=txn.date,
                )
                roundup = calculate_roundup(txn.amount)
                if roundup > 0:
                    RoundupLedgerEntry.objects.create(
                        user=user, transaction=transaction, roundup_amount=roundup
                    )
                created_count += 1
        except IntegrityError:
            continue  # already synced this transaction
    return created_count


def pending_roundup_balance(user):
    entries = RoundupLedgerEntry.objects.filter(user=user, invested=False)
    return sum((e.roundup_amount for e in entries), start=Decimal("0.00"))
