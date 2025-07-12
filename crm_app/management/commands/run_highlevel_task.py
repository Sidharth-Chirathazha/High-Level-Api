from django.core.management.base import BaseCommand
import logging
import requests
import urllib.parse
from django.conf import settings
from crm_app.services.highlevel_service import HighLevelService

logger = logging.getLogger(__name__)


CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URI = settings.REDIRECT_URI
CUSTOM_FIELD_NAME = settings.CUSTOM_FIELD_NAME

class Command(BaseCommand):
    help = "Run HighLevel contact update task"

    def handle(self, *args, **kwargs):

        logger.info("STEP 1 : Visit the URL to get authorization code")
        auth_url = (
            "https://marketplace.leadconnectorhq.com/oauth/chooselocation?"
            f"response_type=code&"
            f"client_id={CLIENT_ID}&"
            f"redirect_uri={urllib.parse.quote(REDIRECT_URI)}&"
            f"scope=contacts.readonly+contacts.write+locations%2FcustomFields.readonly"
        )
        logger.info(f"Visit this URL and login: {auth_url}")
        auth_code = input("Paste the code from redirected URL: ").strip()

        token_data = self.exchange_code_for_token(auth_code)
        if not token_data:
            logger.error("Failed to get access token.")
            return
        
        access_token = token_data["access_token"]
        location_id = token_data["locationId"]
        client = HighLevelService(access_token, location_id)

        contact = client.get_random_contact()
        if not contact:
            return
        
        field_id = client.get_custom_field_id_by_name(CUSTOM_FIELD_NAME)
        if not field_id:
            return
        
        success = client.update_contact_custom_field(contact["id"], field_id, "TEST")
        if success:
            logger.info("Custom field updated successfully.")
        else:
            logger.error("Failed to update custom field.")


    def exchange_code_for_token(self, code):
        token_url = "https://services.leadconnectorhq.com/oauth/token"
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "redirect_uri": REDIRECT_URI,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            res = requests.post(token_url, data=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            logger.info("Access token retrieved successfully")
            return data
        except requests.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            logger.error(f"Response: {res.text if 'res' in locals() else 'No response'}")
            return None
