from datetime import datetime, timezone
from typing import Optional

from lnbits.db import Database
from lnbits.helpers import urlsafe_short_hash

from .models import (
    Bitcoinswitch,
    BitcoinswitchPayment,
    CreateBitcoinswitch,
)

db = Database("ext_bitcoinswitch")


async def create_bitcoinswitch(
    bitcoinswitch_id: str,
    data: CreateBitcoinswitch,
) -> Bitcoinswitch:
    bitcoinswitch_key = urlsafe_short_hash()
    device = Bitcoinswitch(
        id=bitcoinswitch_id,
        key=bitcoinswitch_key,
        title=data.title,
        wallet=data.wallet,
        currency=data.currency,
        switches=data.switches,
        default_accepts_assets=getattr(data, 'default_accepts_assets', False),
    )
    await db.insert("bitcoinswitch.switch", device)
    return device


async def update_bitcoinswitch(device: Bitcoinswitch) -> Bitcoinswitch:
    device.updated_at = datetime.now(timezone.utc)
    await db.update("bitcoinswitch.switch", device)
    return device


async def get_bitcoinswitch(bitcoinswitch_id: str) -> Optional[Bitcoinswitch]:
    return await db.fetchone(
        "SELECT * FROM bitcoinswitch.switch WHERE id = :id",
        {"id": bitcoinswitch_id},
        Bitcoinswitch,
    )


async def get_bitcoinswitches(wallet_ids: list[str]) -> list[Bitcoinswitch]:
    if not wallet_ids:
        return []
    placeholders = ",".join([f":wallet_{i}" for i in range(len(wallet_ids))])
    params = {f"wallet_{i}": wallet_id for i, wallet_id in enumerate(wallet_ids)}
    return await db.fetchall(
        f"""
        SELECT * FROM bitcoinswitch.switch WHERE wallet IN ({placeholders})
        ORDER BY id
        """,
        params,
        model=Bitcoinswitch,
    )


async def delete_bitcoinswitch(bitcoinswitch_id: str) -> None:
    await db.execute(
        "DELETE FROM bitcoinswitch.switch WHERE id = :id",
        {"id": bitcoinswitch_id},
    )


async def create_bitcoinswitch_payment(
    bitcoinswitch_id: str,
    payment_hash: str,
    payload: str,
    pin: int,
    amount_msat: int = 0,
) -> BitcoinswitchPayment:
    bitcoinswitchpayment_id = urlsafe_short_hash()
    payment = BitcoinswitchPayment(
        id=bitcoinswitchpayment_id,
        bitcoinswitch_id=bitcoinswitch_id,
        payload=payload,
        pin=pin,
        payment_hash=payment_hash,
        sats=amount_msat,
    )
    await db.insert("bitcoinswitch.payment", payment)
    return payment


async def update_bitcoinswitch_payment(
    bitcoinswitch_payment: BitcoinswitchPayment,
) -> BitcoinswitchPayment:
    bitcoinswitch_payment.updated_at = datetime.now(timezone.utc)
    await db.update("bitcoinswitch.payment", bitcoinswitch_payment)
    return bitcoinswitch_payment


async def delete_bitcoinswitch_payment(bitcoinswitch_payment_id: str) -> None:
    await db.execute(
        "DELETE FROM bitcoinswitch.payment WHERE id = :id",
        {"id": bitcoinswitch_payment_id},
    )


async def get_bitcoinswitch_payment(
    bitcoinswitchpayment_id: str,
) -> Optional[BitcoinswitchPayment]:
    return await db.fetchone(
        "SELECT * FROM bitcoinswitch.payment WHERE id = :id",
        {"id": bitcoinswitchpayment_id},
        BitcoinswitchPayment,
    )
