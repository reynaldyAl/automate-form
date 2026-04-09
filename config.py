import os
from dotenv import load_dotenv

load_dotenv()

# Form Configuration
FORM_URL = os.getenv("FORM_URL", "https://forms.gle/h77StnbaaogNoW4x9")
CSV_FILE = os.getenv("CSV_FILE", "data_nama_mahasiswa_sastra.csv")
NUM_SUBMISSIONS = int(os.getenv("NUM_SUBMISSIONS", "120"))
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "False").lower() == "true"
DRY_RUN = os.getenv("DRY_RUN", "False").lower() == "true"
USED_NAMES_FILE = os.getenv("USED_NAMES_FILE", "results/used_names.txt")
RESET_USED_NAMES = os.getenv("RESET_USED_NAMES", "False").lower() == "true"

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
        "description": "Supported by family/friends, low perfectionism, low proposal stress, no burnout",
        "characteristics": {
            "perfectionism_tendency": 0.3,  # 0=TS/STS, 1=SS/S
            "social_support_tendency": 0.8,  # 0=TS/STS, 1=SS/S
            "proposal_pressure_tendency": 0.25,
        }
    },
    "unsupported_high_perfectionism_burnout": {
        "count": 25,  # ~20%
        "description": "Unsupported, high perfectionism, high proposal stress, high burnout",
        "characteristics": {
            "perfectionism_tendency": 0.8,
            "social_support_tendency": 0.2,
            "proposal_pressure_tendency": 0.85,
        }
    },
    "supported_high_perfectionism_no_burnout": {
        "count": 35,  # ~29%
        "description": "Supported, high perfectionism, moderate proposal stress, no burnout",
        "characteristics": {
            "perfectionism_tendency": 0.75,
            "social_support_tendency": 0.75,
            "proposal_pressure_tendency": 0.45,
        }
    },
    "moderate_mixed": {
        "count": 30,  # ~25%
        "description": "Moderate profiles with various combinations",
        "characteristics": {
            "perfectionism_tendency": 0.5,
            "social_support_tendency": 0.5,
            "proposal_pressure_tendency": 0.5,
        }
    }
}

# Questions per scale
PERFECTIONISM_QUESTIONS_COUNT = 15
SOCIAL_SUPPORT_QUESTIONS_COUNT = 12
BURNOUT_QUESTIONS_COUNT = 15

# Scoring untuk setiap option (higher = lebih setuju)
SCORE_MAPPING = {
    "SS": 4,   # Sangat Setuju
    "S": 3,    # Setuju
    "TS": 2,   # Tidak Setuju
    "STS": 1   # Sangat Tidak Setuju
}

# Expected score ranges untuk setiap profile
PROFILE_SCORE_RANGES = {
    "supported_low_perfectionism_no_burnout": {
        "perfectionism_score": (15, 38),      # Low (15-38 dari 60)
        "social_support_score": (38, 48),     # High (38-48 dari 48)
        "burnout_score": (15, 30),            # Low (15-30 dari 60)
    },
    "unsupported_high_perfectionism_burnout": {
        "perfectionism_score": (46, 60),      # High
        "social_support_score": (12, 28),     # Low
        "burnout_score": (40, 60),            # High
    },
    "supported_high_perfectionism_no_burnout": {
        "perfectionism_score": (46, 60),      # High
        "social_support_score": (36, 48),     # High
        "burnout_score": (15, 38),            # Low-Moderate
    },
    "moderate_mixed": {
        "perfectionism_score": (30, 50),      # Medium
        "social_support_score": (24, 40),     # Medium
        "burnout_score": (28, 45),            # Moderate
    }
}

# Realism controls for a single analyzable output dataset.
# Keep consistency high but not perfect, with a small controlled outlier portion.
TARGET_CONSISTENCY_MIN = float(os.getenv("TARGET_CONSISTENCY_MIN", "0.90"))
TARGET_CONSISTENCY_MAX = float(os.getenv("TARGET_CONSISTENCY_MAX", "0.95"))
OUTLIER_RATE = float(os.getenv("OUTLIER_RATE", "0.08"))
CONTRADICTORY_RATE = float(os.getenv("CONTRADICTORY_RATE", "0.03"))
STRAIGHTLINE_RATE = float(os.getenv("STRAIGHTLINE_RATE", "0.04"))

# Burnout level mix target for synthetic data.
# Kept close to the real-data pattern: mostly Moderate, with Low still common and High limited.
BURNOUT_LEVEL_TARGET_LOW = float(os.getenv("BURNOUT_LEVEL_TARGET_LOW", "0.28"))
BURNOUT_LEVEL_TARGET_MODERATE = float(os.getenv("BURNOUT_LEVEL_TARGET_MODERATE", "0.57"))
BURNOUT_LEVEL_TARGET_HIGH = float(os.getenv("BURNOUT_LEVEL_TARGET_HIGH", "0.15"))