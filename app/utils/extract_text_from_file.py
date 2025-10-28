import urllib.request
import urllib.parse
from app.utils.logger_util import logger
from app.core.config import external_service_settings

def extract_text_from_file(file_name: str, env: str, file_type: str = 'jd') -> str:
    """
    Extract text from a document using external API.
    """
    base_url = external_service_settings.DOC_EXTRACT_API_URL

    params = {
        'reckFname': file_name,
        'type': file_type,
        'env': env
    }

    api_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    content = ''

    try:
        with urllib.request.urlopen(api_url) as response:
            content_bytes = response.read()
            content = content_bytes.decode('utf-8', errors='replace').strip()
        logger.info(f"Successfully extracted text from {file_name}")
    except Exception as e:
        logger.error(f"Failed to fetch from {api_url}: {e}")
        content = ''

    return content
