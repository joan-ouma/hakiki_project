from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_whatsapp_webhook():
    print("Sending mock Twilio request to /whatsapp/webhook...")
    response = client.post(
        "/whatsapp/webhook",
        data={"From": "whatsapp:+1234567890", "Body": "Did the government build 100 schools?", "NumMedia": "0"}
    )
    print("Status Code:", response.status_code)
    print("Response Body:\n", response.text)
    
    if "Hakiki Fact Check (Mock)" in response.text and response.headers["content-type"] == "application/xml":
        print("\nPhase 1 Test Passed: Webhook returned valid TwiML mock reply.")
    else:
        print("\nPhase 1 Test Failed.")

if __name__ == "__main__":
    test_whatsapp_webhook()
