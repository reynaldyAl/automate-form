import random
import pandas as pd
from config import PROGRAMS

MALE_PREFIXES = [
    "MOH", "MOH.", "MUH", "MUH.", "MOHAMAD", "MOHAMMAD", "AHMAD",
    "I PUTU", "PUTU", "I GEDE", "GEDE", "I KOMANG", "KOMANG", "I KETUT", "KETUT"
]

FEMALE_PREFIXES = [
    "NI ", "NI LUH", "SITI", "SRI", "DWI", "TRI", "NURUL", "NUR "
]

# Indonesian feminine name patterns (last names/parts that indicate female)
FEMININE_INDICATORS = [
    'I', 'IA', 'INI', 'INA', 'AH', 'AH', 'ITI', 'IYA',
    'WAN', 'AE', 'NI', 'TRA', 'NA', 'RI', 'TA', 'DA',
    'A', 'E', 'AU', 'AH', 'INIA', 'ASYAH', 'ATI'
]

# Masculine indicators
MASCULINE_INDICATORS = [
    'AN', 'IN', 'DIN', 'RAN', 'ARIE', 'ER', 'IR',
    'MAN', 'WAR', 'HAD', 'MUH', 'MOH', 'SYAH', 'AWAN'
]

def detect_gender_from_name(name: str) -> str:
    """
    Detect gender from Indonesian name
    Returns 'Perempuan' (Female) or 'Laki-laki' (Male)
    """
    name = name.upper().strip()
    
    # Strong prefix/token checks first
    first_tokens = " ".join(name.split()[:2])
    first_token = name.split()[0] if name.split() else ""

    if any(first_tokens.startswith(prefix) for prefix in MALE_PREFIXES) or any(
        first_token.startswith(prefix) for prefix in MALE_PREFIXES
    ):
        return "Laki-laki"

    if any(first_tokens.startswith(prefix) for prefix in FEMALE_PREFIXES) or any(
        first_token.startswith(prefix) for prefix in FEMALE_PREFIXES
    ):
        return "Perempuan"

    # Check for feminine indicators
    for indicator in FEMININE_INDICATORS:
        if name.endswith(indicator):
            return "Perempuan"
    
    # Check for masculine indicators
    for indicator in MASCULINE_INDICATORS:
        if name.endswith(indicator):
            return "Laki-laki"
    
    # Check for common prefixes
    if any(prefix in name for prefix in ['NI ', 'SRI ', 'SITI ', 'DWI ', 'TRI ', 'NUR ', 'NURUL ']):
        return "Perempuan"
    
    if any(prefix in name for prefix in ['MOH', 'MUH', 'MOHAMAD', 'AHMAD', 'I PUTU', 'HADRIS', 'MUSADIQ']):
        return "Laki-laki"
    
    # Default to random if unclear
    return random.choice(["Perempuan", "Laki-laki"])


def load_student_names(csv_file: str, num_submissions: int) -> list:
    """Load and sample student names from CSV"""
    try:
        df = pd.read_csv(csv_file, header=None, names=['nama'])
        # Remove duplicates and NaN values
        df = df.dropna().drop_duplicates()
        
        # Sample the requested number
        if len(df) >= num_submissions:
            names = df['nama'].sample(n=num_submissions, random_state=42).tolist()
        else:
            print(f"Warning: Only {len(df)} unique names available, using all")
            names = df['nama'].tolist()
        
        return names
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return []


def get_demographic_for_name(name: str, cohort_distribution: dict) -> dict:
    """
    Get demographics for a student name
    """
    gender = detect_gender_from_name(name)
    
    # Determine cohort based on proportion
    cohort_rand = random.random()
    cohort = "2023" if cohort_rand < cohort_distribution.get("2023", 0.6) else "2022"
    
    # Program distribution: ~70% BK, ~30% Bahasa Indonesia
    program = "BK" if random.random() < 0.7 else "Bahasa Indonesia"
    
    return {
        "nama": name,
        "angkatan": cohort,
        "program_studi": program,
        "jenis_kelamin": gender
    }


def assign_cohort_distribution(num_students: int) -> dict:
    """Calculate cohort distribution proportionally"""
    ratio_2023 = 0.6  # 60% from 2023
    ratio_2022 = 0.4  # 40% from 2022
    
    return {
        "2023": ratio_2023,
        "2022": ratio_2022
    }