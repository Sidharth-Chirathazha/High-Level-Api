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
        scopes = [
            "contacts.readonly",
            "contacts.writeonly",
            "locations/customFields.readonly",
            "locations/customFields.writeonly"
        ]
        scope_param = urllib.parse.quote(" ".join(scopes))

        logger.info("STEP 1 : Visit the URL to get authorization code")
        auth_url = (
            "https://marketplace.gohighlevel.com/oauth/chooselocation?response_type=code&redirect_uri=http%3A%2F%2F127.0.0.1%2F&client_id=6870dbd5219830588889ff2f-mcyylbg6&scope=contacts.readonly+contacts.write+locations%2FcustomFields.readonly+locations%2FcustomFields.write"
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

        try:
            res = requests.post(token_url, json=payload)
            res.raise_for_status()
            data = res.json()
            logger.info(f"Access token retrieved successfully")
            return data
        except requests.RequestException as e:
            logger.error(f"Token exchange failed: {e}")
            return None