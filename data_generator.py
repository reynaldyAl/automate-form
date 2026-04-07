import random
from config import (
    SCALE_OPTIONS, 
    RESPONSE_PROFILES,
    PERFECTIONISM_QUESTIONS_COUNT,
    SOCIAL_SUPPORT_QUESTIONS_COUNT,
    BURNOUT_QUESTIONS_COUNT
)

class ResponseGenerator:
    """Generate realistic survey responses based on student profiles"""
    
    def __init__(self):
        self.profile_type = None
        self.characteristics = None
    
    def assign_profile(self) -> dict:
        """Randomly assign a profile to a student"""
        profiles = list(RESPONSE_PROFILES.keys())
        self.profile_type = random.choice(profiles)
        self.characteristics = RESPONSE_PROFILES[self.profile_type]['characteristics']
        return {
            "profile": self.profile_type,
            "characteristics": self.characteristics
        }
    
    def generate_likert_response(self, tendency: float) -> str:
        """
        Generate a Likert scale response based on tendency
        tendency: 0-1, where 0.5 is neutral
        """
        # Add some randomness even within a tendency
        rand_adjustment = random.uniform(-0.15, 0.15)
        adjusted_tendency = max(0, min(1, tendency + rand_adjustment))
        
        if adjusted_tendency > 0.75:
            return random.choice(["SS", "SS", "S"])  # Weighted towards SS
        elif adjusted_tendency > 0.5:
            return random.choice(["SS", "S", "S"])  # More S than SS
        elif adjusted_tendency > 0.25:
            return random.choice(["S", "TS", "TS"])  # More TS than S
        else:
            return random.choice(["TS", "STS", "STS"])  # Weighted towards STS
    
    def generate_perfectionism_responses(self) -> list:
        """Generate 15 perfectionism scale responses"""
        tendency = self.characteristics['perfectionism_tendency']
        
        # Add some variation - not all the same
        variations = [
            tendency,
            max(0, tendency - 0.1),
            min(1, tendency + 0.1),
            max(0, tendency - 0.05),
            min(1, tendency + 0.15),
        ]
        
        responses = []
        for i in range(PERFECTIONISM_QUESTIONS_COUNT):
            # Vary which tendency to use
            current_tendency = variations[i % len(variations)]
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_social_support_responses(self) -> list:
        """Generate 12 social support scale responses"""
        tendency = self.characteristics['social_support_tendency']
        
        # Same pattern: vary the responses
        variations = [
            tendency,
            max(0, tendency - 0.1),
            min(1, tendency + 0.1),
            max(0, tendency - 0.05),
            min(1, tendency + 0.15),
        ]
        
        responses = []
        for i in range(SOCIAL_SUPPORT_QUESTIONS_COUNT):
            current_tendency = variations[i % len(variations)]
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_burnout_responses(self) -> list:
        """Generate 15 academic burnout scale responses"""
        tendency = self.characteristics['burnout_tendency']
        
        # For burnout, the scale is slightly different (STS=1, TS=2, S=3, SS=4)
        # But we still use the same options
        variations = [
            tendency,
            max(0, tendency - 0.1),
            min(1, tendency + 0.1),
            max(0, tendency - 0.05),
            min(1, tendency + 0.15),
        ]
        
        responses = []
        for i in range(BURNOUT_QUESTIONS_COUNT):
            current_tendency = variations[i % len(variations)]
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_complete_survey(self) -> dict:
        """Generate complete survey response for a student"""
        self.assign_profile()
        
        return {
            "profile": self.profile_type,
            "perfectionism": self.generate_perfectionism_responses(),
            "social_support": self.generate_social_support_responses(),
            "burnout": self.generate_burnout_responses()
        }


def generate_all_responses(num_students: int) -> list:
    """Generate survey responses for all students"""
    generator = ResponseGenerator()
    all_responses = []
    
    for _ in range(num_students):
        all_responses.append(generator.generate_complete_survey())
    
    return all_responses