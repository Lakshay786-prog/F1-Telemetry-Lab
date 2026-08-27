import fastf1
from pathlib import Path


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# FastF1 cache directory
CACHE_DIR = BASE_DIR / "data" / "fastf1_cache"

# Create cache directory if it doesn't exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Enable FastF1 cache
fastf1.Cache.enable_cache(str(CACHE_DIR))


def get_fastf1():
    """
    Return the FastF1 package after cache initialization.
    """
    return fastf1