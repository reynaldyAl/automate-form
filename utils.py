import random
import os
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


def _read_used_names(used_names_file: str) -> set:
    if not used_names_file or not os.path.exists(used_names_file):
        return set()

    used = set()
    try:
        with open(used_names_file, "r", encoding="utf-8") as f:
            for line in f:
                name = line.strip()
                if name:
                    used.add(name)
    except Exception as e:
        print(f"Warning: Could not read used names file: {e}")
    return used


def _append_used_names(used_names_file: str, names: list):
    if not used_names_file or not names:
        return

    try:
        folder = os.path.dirname(used_names_file)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with open(used_names_file, "a", encoding="utf-8") as f:
            for name in names:
                f.write(f"{name}\n")
    except Exception as e:
        print(f"Warning: Could not update used names file: {e}")


def load_student_names(
    csv_file: str,
    num_submissions: int,
    used_names_file: str = None,
    reset_used_names: bool = False,
) -> list:
    """Load and sample student names from CSV"""
    try:
        df = pd.read_csv(csv_file, header=None, names=['nama'])
        # Remove duplicates and NaN values
        df = df.dropna()
        df['nama'] = df['nama'].astype(str).str.strip()
        df = df[df['nama'] != ""].drop_duplicates(subset=['nama'])

        if reset_used_names and used_names_file and os.path.exists(used_names_file):
            os.remove(used_names_file)
            print(f"Used names reset: {used_names_file}")

        used_names = _read_used_names(used_names_file) if used_names_file else set()
        all_names = df['nama'].tolist()
        available_names = [name for name in all_names if name not in used_names]

        if not available_names:
            print("Warning: No new names available (all names already used).")
            return []

        take_count = min(num_submissions, len(available_names))
        if take_count < num_submissions:
            print(
                f"Warning: Only {take_count} unused names available, "
                f"requested {num_submissions}."
            )

        names = random.sample(available_names, take_count)
        _append_used_names(used_names_file, names)

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