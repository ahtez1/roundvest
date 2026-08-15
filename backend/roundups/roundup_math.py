import math
from decimal import ROUND_HALF_UP, Decimal


def calculate_roundup(amount: Decimal) -> Decimal:
    """The amount needed to round a purchase up to the next whole dollar.

    A purchase that's already a whole dollar amount produces no round-up.
    Never returns a negative number.
    """
    if amount <= 0:
        return Decimal("0.00")

    rounded_up = Decimal(math.ceil(amount))
    roundup = (rounded_up - amount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return roundup if roundup > 0 else Decimal("0.00")
