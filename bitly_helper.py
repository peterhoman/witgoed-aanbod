"""
Bit.ly API integration for shortening affiliate URLs
"""

import requests
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

class BitlyClient:
    """Bit.ly URL shortener"""

    def __init__(self, api_token):
        self.api_token = api_token
        self.base_url = "https://api-ssl.bitly.com/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def shorten_url(self, long_url, title=None):
        """
        Shorten a URL using Bit.ly API

        Args:
            long_url: The full URL to shorten
            title: Optional title for the short link

        Returns:
            Shortened URL or original URL if error
        """
        if not long_url or not self.api_token:
            logger.warning("[!] No URL or API token provided for Bit.ly")
            return long_url

        try:
            payload = {
                "long_url": long_url,
                "domain": "bit.ly"
            }

            if title:
                payload["title"] = title

            response = requests.post(
                f"{self.base_url}/shorten",
                json=payload,
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 201:
                data = response.json()
                short_url = data.get('link')
                logger.debug(f"[+] Shortened URL: {short_url}")
                return short_url
            else:
                logger.warning(f"[!] Bit.ly error {response.status_code}: {response.text}")
                return long_url

        except requests.exceptions.Timeout:
            logger.error("[!] Bit.ly timeout")
            return long_url
        except Exception as e:
            logger.error(f"[!] Bit.ly error: {e}")
            return long_url


def get_bitly_client(api_token):
    """Factory function for Bit.ly client"""
    if not api_token:
        logger.warning("[!] BITLY_TOKEN not set - URL shortening disabled")
        return None
    return BitlyClient(api_token)
