import requests
from django.conf import settings


def fetch_external_products():
    url = f"{settings.EXTERNAL_API_BASE_URL}/api/v1/products/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erro ao buscar produtos externos: {e}")
        return []
