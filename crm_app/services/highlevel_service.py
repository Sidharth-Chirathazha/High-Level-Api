import requests
import logging
import random
from django.conf import settings

logger = logging.getLogger(__name__)

class HighLevelService:
    BASE_URL = settings.BASE_URL

    def __init__(self, access_token:str, location_id: str):
        self.access_token = access_token
        self.location_id = location_id
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Version": "2021-07-28"
        }

    def get_contacts(self):
        url = f"{self.BASE_URL}/contacts/"
        params = {
            "locationId": self.location_id
        }
        logger.info(f"GET {url} with headers: {self.headers} and params: {params}")
    
        response = requests.get(url, headers=self.headers, params=params)
        logger.error(f"Response: {response.status_code} - {response.text}")
        response.raise_for_status()

        contacts = response.json().get("contacts", [])
        logger.info(f"Retrieved {len(contacts)} contacts.")
        return contacts
    
    def get_random_contact(self):
        contacts = self.get_contacts()
        if not contacts:
            logger.warning("No contacts found.")
            return None
        contact = random.choice(contacts)
        logger.info(f"Selected contact id: {contact['id']}")
        return contact
    
    def get_custom_fields(self):
        url = f"{self.BASE_URL}/locations/{self.location_id}/customFields"
        params = {
            "model": "contact"
        }
        logger.info(f"GET {url} with params: {params}")
    
        response = requests.get(url, headers=self.headers, params=params)
        logger.error(f"Response: {response.status_code} - {response.text}")
        response.raise_for_status()

        fields = response.json().get("customFields", [])
        logger.info(f"Retrieved {len(fields)} custom fields.")
        return fields
    
    def get_custom_field_id_by_name(self, name):
        fields = self.get_custom_fields()
        for field in fields:
            if field["name"] == name:
                logger.info(f"Found custom field ID: {field['id']}")
                return field["id"]
        logger.warning(f"Custom field '{name}' not found.")
        return None 
    
    def update_contact_custom_field(self, contact_id, field_id, value):
        url = f"{self.BASE_URL}/contacts/{contact_id}"
        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        payload = {
            "customFields": [
                {
                    "id": field_id,
                    "field_value": value
                }
            ]
        }
        response = requests.put(url, json=payload, headers=headers)
        logger.info(f"Update contact response: {response.status_code} - {response.text}")
        return response.status_code == 200