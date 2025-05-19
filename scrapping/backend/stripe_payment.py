import os
from fastapi import APIRouter, Request
import stripe

router = APIRouter()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@router.post("/create-checkout-session")
async def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "AI Web-Scraper Paid Tier",
                    },
                    "unit_amount": 999,  # $9.99 in cents
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=os.getenv("SUCCESS_URL"),
            cancel_url=os.getenv("CANCEL_URL"),
        )
        return {"sessionId": session.id, "url": session.url}
    except Exception as e:
        return {"error": str(e)}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError:
        return {"error": "Invalid payload"}, 400
    except stripe.error.SignatureVerificationError:
        return {"error": "Invalid signature"}, 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print(f"Payment successful for session: {session['id']}")

    return {"status": "success"}
