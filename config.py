import os
from dotenv import load_dotenv

load_dotenv()

# Form Configuration
FORM_URL = os.getenv("FORM_URL", "https://forms.gle/h77StnbaaogNoW4x9")
CSV_FILE = os.getenv("CSV_FILE", "data_nama_mahasiswa_sastra.csv")
NUM_SUBMISSIONS = int(os.getenv("NUM_SUBMISSIONS", "120"))
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "False").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"

# Demographics
COHORTS = ["2023", "2022"]
PROGRAMS = ["BK", "Bahasa Indonesia"]
GENDERS = ["Perempuan", "Laki-laki"]

# Scale options (all use SS, S, TS, STS)
SCALE_OPTIONS = ["SS", "S", "TS", "STS"]

# Response Profiles Distribution (out of 120)
RESPONSE_PROFILES = {
    "supported_low_perfectionism_no_burnout": {
        "count": 30,  # 25%
        "description": "Supported by family/friends, low perfectionism, no burnout",
        "characteristics": {
            "perfectionism_tendency": 0.3,  # 0=TS/STS, 1=SS/S
            "social_support_tendency": 0.8,  # 0=TS/STS, 1=SS/S
            "burnout_tendency": 0.2,  # 0=STS/TS, 1=SS/S
        }
    },
    "unsupported_high_perfectionism_burnout": {
        "count": 25,  # ~20%
        "description": "Unsupported, high perfectionism, high burnout",
        "characteristics": {
            "perfectionism_tendency": 0.8,
            "social_support_tendency": 0.2,
            "burnout_tendency": 0.85,
        }
    },
    "supported_high_perfectionism_no_burnout": {
        "count": 35,  # ~29%
        "description": "Supported, high perfectionism, no burnout",
        "characteristics": {
            "perfectionism_tendency": 0.75,
            "social_support_tendency": 0.75,
            "burnout_tendency": 0.3,
        }
    },
    "moderate_mixed": {
        "count": 30,  # ~25%
        "description": "Moderate profiles with various combinations",
        "characteristics": {
            "perfectionism_tendency": 0.5,
            "social_support_tendency": 0.5,
            "burnout_tendency": 0.5,
        }
    }
}

# Questions per scale
PERFECTIONISM_QUESTIONS_COUNT = 15
SOCIAL_SUPPORT_QUESTIONS_COUNT = 12
BURNOUT_QUESTIONS_COUNT = 15