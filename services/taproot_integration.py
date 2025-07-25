"""Integration with Taproot Assets extension."""
from typing import Optional, Dict, Any
from loguru import logger
from lnbits.core.crud import get_installed_extensions


class TaprootIntegration:
    """Handle integration with Taproot Assets extension."""
    
    @staticmethod
    async def is_taproot_available() -> bool:
        """Check if Taproot Assets extension is installed and enabled."""
        try:
            extensions = await get_installed_extensions()
            return any(ext.id == "taproot_assets" and ext.active for ext in extensions)
        except Exception as e:
            logger.warning(f"Failed to check taproot availability: {e}")
            return False
    
    @staticmethod
    async def create_rfq_invoice(
        asset_id: str,
        amount: int,
        description: str,
        wallet_id: str,
        user_id: str,
        extra: Dict[str, Any],
        peer_pubkey: Optional[str] = None,
        expiry: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a Taproot Asset invoice using the RFQ (Request for Quote) process.
        This creates an invoice that can be paid with either sats or the specified asset.
        """
        try:
            # Simply use the invoice service which now handles peer discovery
            from lnbits.extensions.taproot_assets.services.invoice_service import InvoiceService
            from lnbits.extensions.taproot_assets.models import TaprootInvoiceRequest
            
            # Create the invoice request
            request = TaprootInvoiceRequest(
                asset_id=asset_id,
                amount=amount,
                description=description,
                expiry=expiry,
                peer_pubkey=peer_pubkey,  # Can be None - invoice service will find it
                extra=extra
            )
            
            # Let the invoice service handle everything including peer discovery
            response = await InvoiceService.create_invoice(
                data=request,
                user_id=user_id,
                wallet_id=wallet_id
            )
            
            return {
                "payment_hash": response.payment_hash,
                "payment_request": response.payment_request,
                "checking_id": response.checking_id,
                "is_rfq": True
            }
            
        except ImportError as e:
            logger.error(f"Taproot Assets extension not available: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to create RFQ invoice: {e}")
            return None