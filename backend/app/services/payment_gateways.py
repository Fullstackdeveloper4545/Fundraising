from typing import Dict, Any, Optional
import logging
import stripe
import requests
from decimal import Decimal

from app.core.config import settings

logger = logging.getLogger(__name__)


class PaymentGatewayService:
    """Service for handling payment gateway integrations"""
    
    def __init__(self):
        self.stripe_secret_key = settings.STRIPE_SECRET_KEY
        self.paypal_client_id = settings.PAYPAL_CLIENT_ID
        self.paypal_client_secret = settings.PAYPAL_CLIENT_SECRET
        self.square_app_id = settings.SQUARE_APPLICATION_ID
        self.square_access_token = settings.SQUARE_ACCESS_TOKEN
        
        # Initialize Stripe
        if self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key

    async def process_stripe_payment(self, amount: Decimal, currency: str = "usd", **kwargs) -> Dict[str, Any]:
        """Process payment through Stripe"""
        try:
            if not self.stripe_secret_key:
                raise Exception("Stripe not configured")
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=kwargs.get('metadata', {})
            )
            
            return {
                "success": True,
                "transaction_id": intent.id,
                "client_secret": intent.client_secret,
                "status": intent.status
            }
        except Exception as e:
            logger.error(f"Stripe payment error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_paypal_payment(self, amount: Decimal, currency: str = "USD", **kwargs) -> Dict[str, Any]:
        """Process payment through PayPal"""
        try:
            if not self.paypal_client_id or not self.paypal_client_secret:
                raise Exception("PayPal not configured")
            
            # Get access token
            token_response = requests.post(
                "https://api.sandbox.paypal.com/v1/oauth2/token",
                auth=(self.paypal_client_id, self.paypal_client_secret),
                data={"grant_type": "client_credentials"},
                headers={"Accept": "application/json"}
            )
            
            if token_response.status_code != 200:
                raise Exception("Failed to get PayPal access token")
            
            access_token = token_response.json()["access_token"]
            
            # Create payment
            payment_data = {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "transactions": [{
                    "amount": {
                        "total": str(amount),
                        "currency": currency
                    },
                    "description": kwargs.get('description', 'Donation')
                }],
                "redirect_urls": {
                    "return_url": kwargs.get('return_url', ''),
                    "cancel_url": kwargs.get('cancel_url', '')
                }
            }
            
            payment_response = requests.post(
                "https://api.sandbox.paypal.com/v1/payments/payment",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=payment_data
            )
            
            if payment_response.status_code != 201:
                raise Exception("Failed to create PayPal payment")
            
            payment_result = payment_response.json()
            
            return {
                "success": True,
                "transaction_id": payment_result["id"],
                "approval_url": next(link["href"] for link in payment_result["links"] if link["rel"] == "approval_url"),
                "status": payment_result["state"]
            }
        except Exception as e:
            logger.error(f"PayPal payment error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def process_square_payment(self, amount: Decimal, currency: str = "USD", **kwargs) -> Dict[str, Any]:
        """Process payment through Square"""
        try:
            if not self.square_access_token:
                raise Exception("Square not configured")
            
            # Create payment request
            payment_data = {
                "source_id": kwargs.get('source_id'),
                "amount_money": {
                    "amount": int(amount * 100),  # Convert to cents
                    "currency": currency
                },
                "idempotency_key": kwargs.get('idempotency_key', ''),
                "note": kwargs.get('note', 'Donation')
            }
            
            payment_response = requests.post(
                "https://connect.squareupsandbox.com/v2/payments",
                headers={
                    "Authorization": f"Bearer {self.square_access_token}",
                    "Content-Type": "application/json",
                    "Square-Version": "2023-10-18"
                },
                json=payment_data
            )
            
            if payment_response.status_code != 200:
                raise Exception("Failed to process Square payment")
            
            payment_result = payment_response.json()
            
            return {
                "success": True,
                "transaction_id": payment_result["payment"]["id"],
                "status": payment_result["payment"]["status"]
            }
        except Exception as e:
            logger.error(f"Square payment error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def verify_payment(self, gateway: str, transaction_id: str) -> Dict[str, Any]:
        """Verify payment status with gateway"""
        try:
            if gateway == "stripe":
                if not self.stripe_secret_key:
                    raise Exception("Stripe not configured")
                
                intent = stripe.PaymentIntent.retrieve(transaction_id)
                return {
                    "success": True,
                    "status": intent.status,
                    "amount": intent.amount / 100,  # Convert from cents
                    "currency": intent.currency
                }
            
            elif gateway == "paypal":
                if not self.paypal_client_id or not self.paypal_client_secret:
                    raise Exception("PayPal not configured")
                
                # Get access token
                token_response = requests.post(
                    "https://api.sandbox.paypal.com/v1/oauth2/token",
                    auth=(self.paypal_client_id, self.paypal_client_secret),
                    data={"grant_type": "client_credentials"},
                    headers={"Accept": "application/json"}
                )
                
                if token_response.status_code != 200:
                    raise Exception("Failed to get PayPal access token")
                
                access_token = token_response.json()["access_token"]
                
                # Get payment details
                payment_response = requests.get(
                    f"https://api.sandbox.paypal.com/v1/payments/payment/{transaction_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                )
                
                if payment_response.status_code != 200:
                    raise Exception("Failed to verify PayPal payment")
                
                payment_result = payment_response.json()
                
                return {
                    "success": True,
                    "status": payment_result["state"],
                    "amount": float(payment_result["transactions"][0]["amount"]["total"]),
                    "currency": payment_result["transactions"][0]["amount"]["currency"]
                }
            
            elif gateway == "square":
                if not self.square_access_token:
                    raise Exception("Square not configured")
                
                payment_response = requests.get(
                    f"https://connect.squareupsandbox.com/v2/payments/{transaction_id}",
                    headers={
                        "Authorization": f"Bearer {self.square_access_token}",
                        "Square-Version": "2023-10-18"
                    }
                )
                
                if payment_response.status_code != 200:
                    raise Exception("Failed to verify Square payment")
                
                payment_result = payment_response.json()
                
                return {
                    "success": True,
                    "status": payment_result["payment"]["status"],
                    "amount": payment_result["payment"]["amount_money"]["amount"] / 100,  # Convert from cents
                    "currency": payment_result["payment"]["amount_money"]["currency"]
                }
            
            else:
                raise Exception(f"Unsupported payment gateway: {gateway}")
                
        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
