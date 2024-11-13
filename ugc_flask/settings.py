import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).parent

JWT_PUBLIC_KEY = BASE_DIR / 'certs' / 'public.pem'
JWT_ALGORITHM = 'RS256'

BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS')


class ClickTrackingTopics(Enum):
    QUALITY_CHANGE_CLICK = 'tracking.clicks_on_video.quality_changes'
    PAUSE_CLICK = 'tracking.clicks_on_video.pauses'
    FULL_VIEW = 'tracking.clicks_on_video.full_views'
