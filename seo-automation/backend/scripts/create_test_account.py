"""
One-time helper to create a Google Ads TEST account under your Manager
account, using the credentials already saved in backend/.env. Prints the
resulting Customer ID to paste into GOOGLE_ADS_CUSTOMER_ID.

Run from the backend/ directory with the venv active:
    python scripts/create_test_account.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings  # noqa: E402

MANAGER_CUSTOMER_ID = "2379918178"  # ZeOrbit Ads Manager, dashes stripped


def main():
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException

    client_config = {
        "developer_token": settings.GOOGLE_ADS_DEVELOPER_TOKEN,
        "client_id": settings.GOOGLE_ADS_CLIENT_ID,
        "client_secret": settings.GOOGLE_ADS_CLIENT_SECRET,
        "refresh_token": settings.GOOGLE_ADS_REFRESH_TOKEN,
        "login_customer_id": MANAGER_CUSTOMER_ID,
        "use_proto_plus": True,
    }
    client = GoogleAdsClient.load_from_dict(client_config)

    customer_service = client.get_service("CustomerService")
    customer = client.get_type("Customer")
    customer.descriptive_name = "ZeOrbit Test Account"
    customer.currency_code = "USD"
    customer.time_zone = "America/Los_Angeles"
    customer.test_account = True

    try:
        response = customer_service.create_customer_client(
            customer_id=MANAGER_CUSTOMER_ID,
            customer_client=customer,
        )
        resource_name = response.resource_name  # e.g. "customers/1234567890"
        new_customer_id = resource_name.split("/")[-1]
        print("\n" + "=" * 60)
        print("Test account created!")
        print(f"Customer ID (paste into GOOGLE_ADS_CUSTOMER_ID): {new_customer_id}")
        print("=" * 60)
    except GoogleAdsException as ex:
        print("Google Ads API error:")
        for error in ex.failure.errors:
            print(f"  - {error.message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
