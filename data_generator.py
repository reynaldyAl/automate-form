import random
from config import (
    RESPONSE_PROFILES,
    PERFECTIONISM_QUESTIONS_COUNT,
    SOCIAL_SUPPORT_QUESTIONS_COUNT,
    BURNOUT_QUESTIONS_COUNT,
    SCORE_MAPPING,
    PROFILE_SCORE_RANGES,
    OUTLIER_RATE,
    CONTRADICTORY_RATE,
    STRAIGHTLINE_RATE,
    BURNOUT_LEVEL_TARGET_LOW,
    BURNOUT_LEVEL_TARGET_MODERATE,
    BURNOUT_LEVEL_TARGET_HIGH,
)


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _score_answers(answers: list) -> int:
    return sum(SCORE_MAPPING.get(a, 0) for a in answers)


def _is_consistent_with_profile(profile: str, perf_score: int, social_score: int, burnout_score: int) -> bool:
    ranges = PROFILE_SCORE_RANGES.get(profile)
    if not ranges:
        return False
    perf_ok = ranges["perfectionism_score"][0] <= perf_score <= ranges["perfectionism_score"][1]
    social_ok = ranges["social_support_score"][0] <= social_score <= ranges["social_support_score"][1]
    burnout_ok = ranges["burnout_score"][0] <= burnout_score <= ranges["burnout_score"][1]
    return perf_ok and social_ok and burnout_ok


LIKERT_ASC = ["STS", "TS", "S", "SS"]


def _clamp_idx(index: int) -> int:
    return max(0, min(len(LIKERT_ASC) - 1, index))


def _shift_answer(answer: str, delta: int) -> str:
    try:
        idx = LIKERT_ASC.index(answer)
    except ValueError:
        idx = 1
    return LIKERT_ASC[_clamp_idx(idx + delta)]


def _score_bundle(response: dict) -> tuple:
    return (
        _score_answers(response["perfectionism"]),
        _score_answers(response["social_support"]),
        _score_answers(response["burnout"]),
    )


def _mark_outlier(response: dict, outlier_type: str):
    response["outlier_type"] = outlier_type


def _burnout_level_from_score(score: int) -> str:
    if score >= 40:
        return "High"
    if score >= 28:
        return "Moderate"
    return "Low"


def _score_within_profile(profile: str, burnout_score: int) -> bool:
    ranges = PROFILE_SCORE_RANGES.get(profile)
    if not ranges:
        return False
    return ranges["burnout_score"][0] <= burnout_score <= ranges["burnout_score"][1]


def _target_burnout_counts(total: int) -> dict:
    raw = {
        "Low": total * BURNOUT_LEVEL_TARGET_LOW,
        "Moderate": total * BURNOUT_LEVEL_TARGET_MODERATE,
        "High": total * BURNOUT_LEVEL_TARGET_HIGH,
    }
    counts = {k: int(raw[k]) for k in raw}
    remaining = total - sum(counts.values())
    order = sorted(raw.keys(), key=lambda k: raw[k] - int(raw[k]), reverse=True)
    for i in range(remaining):
        counts[order[i % len(order)]] += 1
    return counts


def _nudge_burnout_score(response: dict, direction: str, max_steps: int = 4):
    # Nudge score up/down with small random edits to keep item-level variability.
    if direction not in {"up", "down"}:
        return
    delta = 1 if direction == "up" else -1
    for _ in range(max_steps):
        pos = random.randrange(len(response["burnout"]))
        original = response["burnout"][pos]
        updated = _shift_answer(original, delta)
        response["burnout"][pos] = updated

        if not _score_within_profile(response["profile"], _score_answers(response["burnout"])):
            response["burnout"][pos] = original
            continue


def _ensure_non_uniform_burnout(response: dict):
    # Prevent respondents from having exactly one repeated option for all burnout items.
    if len(set(response["burnout"])) > 1:
        return
    anchor = response["burnout"][0]
    positions = random.sample(range(len(response["burnout"])), k=2)
    response["burnout"][positions[0]] = _shift_answer(anchor, 1)
    response["burnout"][positions[1]] = _shift_answer(anchor, -1)


def _tune_burnout_mix(all_responses: list):
    total = len(all_responses)
    if total == 0:
        return

    target = _target_burnout_counts(total)

    # Keep outlier rows untouched for their intended behavior.
    adjustable_idx = [
        idx for idx, row in enumerate(all_responses)
        if row.get("outlier_type", "none") == "none"
    ]

    for _ in range(220):
        level_by_idx = {}
        counts = {"Low": 0, "Moderate": 0, "High": 0}

        for idx, row in enumerate(all_responses):
            score = _score_answers(row["burnout"])
            lvl = _burnout_level_from_score(score)
            level_by_idx[idx] = lvl
            counts[lvl] += 1

        deficits = [lvl for lvl in ["Low", "Moderate", "High"] if counts[lvl] < target[lvl]]
        surpluses = [lvl for lvl in ["Low", "Moderate", "High"] if counts[lvl] > target[lvl]]
        if not deficits or not surpluses:
            break

        deficit = deficits[0]
        surplus = surpluses[0]

        candidates = [
            idx for idx in adjustable_idx
            if level_by_idx[idx] == surplus
        ]
        if not candidates:
            break

        chosen_idx = random.choice(candidates)
        chosen = all_responses[chosen_idx]

        backup_burnout = chosen["burnout"][:]
        if deficit == "High":
            _nudge_burnout_score(chosen, "up", max_steps=3)
        elif deficit == "Low":
            _nudge_burnout_score(chosen, "down", max_steps=3)
        else:
            if surplus == "Low":
                _nudge_burnout_score(chosen, "up", max_steps=2)
            elif surplus == "High":
                _nudge_burnout_score(chosen, "down", max_steps=2)

        after = _score_answers(chosen["burnout"])
        if not _score_within_profile(chosen["profile"], after):
            # Revert if the adjustment pushed the row outside its profile range.
            chosen["burnout"] = backup_burnout


    for row in all_responses:
        _ensure_non_uniform_burnout(row)


def _apply_contradictory_pattern(response: dict):
    # Contradictory: social support appears high while burnout also appears high.
    response["social_support"] = [random.choice(["S", "SS", "S"]) for _ in response["social_support"]]
    response["burnout"] = [random.choice(["S", "SS", "S", "TS"]) for _ in response["burnout"]]


def _apply_straightline_pattern(response: dict):
    # Straight-line ringan: mostly one option on one scale with small local variation.
    target_scale = random.choice(["perfectionism", "social_support", "burnout"])
    anchor = random.choice(["TS", "S"])
    updated = []
    for _ in response[target_scale]:
        if random.random() < 0.15:
            updated.append(_shift_answer(anchor, random.choice([-1, 1])))
        else:
            updated.append(anchor)
    response[target_scale] = updated


def _apply_mild_outlier_pattern(response: dict):
    # Mild outlier: small contradictory nudges across scales.
    all_positions = []
    for scale_name in ["perfectionism", "social_support", "burnout"]:
        for idx in range(len(response[scale_name])):
            all_positions.append((scale_name, idx))

    random.shuffle(all_positions)
    changes = random.randint(6, 10)
    for scale_name, idx in all_positions[:changes]:
        delta = random.choice([-2, -1, 1, 2])
        response[scale_name][idx] = _shift_answer(response[scale_name][idx], delta)


def _force_inconsistent_with_profile(response: dict):
    # Force inconsistency via social support, because profile ranges are clearly separated here.
    profile = response["profile"]
    if profile == "unsupported_high_perfectionism_burnout":
        # Expected low support; push to high support.
        response["social_support"] = [random.choice(["S", "SS", "SS"]) for _ in response["social_support"]]
    else:
        # Expected medium/high support; push to low support.
        response["social_support"] = [random.choice(["TS", "STS", "TS"]) for _ in response["social_support"]]


def _is_response_consistent(response: dict) -> bool:
    perf_score, social_score, burnout_score = _score_bundle(response)
    return _is_consistent_with_profile(response["profile"], perf_score, social_score, burnout_score)


def _apply_controlled_outliers(all_responses: list):
    total = len(all_responses)
    if total == 0:
        return

    for response in all_responses:
        response["outlier_type"] = "none"

    total_outliers = max(1, round(total * OUTLIER_RATE))
    contradictory_count = round(total * CONTRADICTORY_RATE)
    straightline_count = round(total * STRAIGHTLINE_RATE)

    # Keep category counts feasible and non-overlapping.
    if contradictory_count + straightline_count > total_outliers:
        overflow = contradictory_count + straightline_count - total_outliers
        reduce_straight = min(overflow, straightline_count)
        straightline_count -= reduce_straight
        overflow -= reduce_straight
        contradictory_count = max(0, contradictory_count - overflow)

    generic_count = max(0, total_outliers - contradictory_count - straightline_count)

    indices = list(range(total))
    random.shuffle(indices)

    contradictory_idx = set(indices[:contradictory_count])
    straightline_idx = set(indices[contradictory_count:contradictory_count + straightline_count])
    generic_idx = set(indices[contradictory_count + straightline_count:contradictory_count + straightline_count + generic_count])

    for idx in contradictory_idx:
        response = all_responses[idx]
        _apply_contradictory_pattern(response)
        _force_inconsistent_with_profile(response)
        _mark_outlier(response, "contradictory")

    for idx in straightline_idx:
        response = all_responses[idx]
        _apply_straightline_pattern(response)
        _force_inconsistent_with_profile(response)
        _mark_outlier(response, "straightline")

    for idx in generic_idx:
        response = all_responses[idx]
        _apply_mild_outlier_pattern(response)
        _force_inconsistent_with_profile(response)
        _mark_outlier(response, "general_outlier")

    # Safety net: if a targeted outlier remains consistent, push once more.
    for idx in (contradictory_idx | straightline_idx | generic_idx):
        response = all_responses[idx]
        if _is_response_consistent(response):
            _force_inconsistent_with_profile(response)

class ResponseGenerator:
    """Generate realistic survey responses based on student profiles"""
    
    def __init__(self):
        self.profile_type = None
        self.characteristics = None
        self.response_style = None
        self.response_bias = 0.0
    
    def assign_profile(self, profile_key: str = None) -> dict:
        """Assign profile to a student (forced or weighted)."""
        if profile_key is not None:
            self.profile_type = profile_key
        else:
            profiles = list(RESPONSE_PROFILES.keys())
            weights = [RESPONSE_PROFILES[p].get("count", 1) for p in profiles]
            self.profile_type = random.choices(profiles, weights=weights, k=1)[0]

        self.characteristics = RESPONSE_PROFILES[self.profile_type]['characteristics']
        self.response_style = random.choices(
            ["balanced", "decisive", "mixed", "cautious"],
            weights=[3, 2, 3, 2],
            k=1,
        )[0]
        self.response_bias = random.uniform(-0.12, 0.12)
        return {
            "profile": self.profile_type,
            "response_style": self.response_style,
            "characteristics": self.characteristics
        }
    
    def generate_likert_response(self, tendency: float) -> str:
        """
        Generate a Likert scale response based on tendency
        tendency: 0-1, where 0.5 is neutral
        """
        # Add respondent-level style and question-level randomness.
        rand_adjustment = random.uniform(-0.15, 0.15)
        adjusted_tendency = _clamp(tendency + self.response_bias + rand_adjustment)
        
        if self.response_style == "balanced":
            if adjusted_tendency > 0.72:
                return random.choice(["SS", "S", "SS"])
            if adjusted_tendency > 0.48:
                return random.choice(["S", "S", "TS"])
            if adjusted_tendency > 0.28:
                return random.choice(["TS", "S", "TS"])
            return random.choice(["STS", "TS", "STS"])

        if self.response_style == "decisive":
            if adjusted_tendency > 0.70:
                return random.choice(["SS", "SS", "S"])
            if adjusted_tendency > 0.45:
                return random.choice(["SS", "S", "S"])
            if adjusted_tendency > 0.25:
                return random.choice(["S", "TS", "S"])
            return random.choice(["TS", "STS", "STS"])

        if self.response_style == "mixed":
            if adjusted_tendency > 0.68:
                return random.choice(["SS", "S", "SS"])
            if adjusted_tendency > 0.44:
                return random.choice(["S", "TS", "S"])
            if adjusted_tendency > 0.24:
                return random.choice(["TS", "S", "TS"])
            return random.choice(["STS", "TS", "STS"])

        # cautious
        if adjusted_tendency > 0.72:
            return random.choice(["SS", "S", "S"])
        elif adjusted_tendency > 0.50:
            return random.choice(["S", "S", "TS"])
        elif adjusted_tendency > 0.28:
            return random.choice(["TS", "TS", "S"])
        else:
            return random.choice(["TS", "STS", "STS"])  # Weighted towards STS

    def _question_tendency(self, base_tendency: float, question_index: int, scale_name: str) -> float:
        """Create a slightly different tendency for each question."""
        wave = ((question_index % 4) - 1.5) * 0.035
        style_shift = 0.0

        if self.response_style == "decisive":
            style_shift = 0.07 if base_tendency >= 0.5 else -0.05
        elif self.response_style == "mixed":
            style_shift = 0.05 if question_index % 2 == 0 else -0.05
        elif self.response_style == "cautious":
            style_shift = -0.04 if scale_name != "social_support" else 0.02
        else:
            style_shift = 0.0

        question_noise = random.uniform(-0.07, 0.07)
        return _clamp(base_tendency + wave + style_shift + question_noise)

    def generate_burnout_tendency(self) -> float:
        """Derive burnout from perfectionism, social support, and proposal pressure."""
        perfectionism = self.characteristics['perfectionism_tendency']
        social_support = self.characteristics['social_support_tendency']
        proposal_pressure = self.characteristics.get('proposal_pressure_tendency', 0.5)

        # Higher perfectionism and proposal pressure push burnout up.
        # Stronger social support pushes burnout down.
        base = 0.20 + (0.35 * perfectionism) + (0.36 * proposal_pressure) - (0.32 * social_support)

        # Profile-specific anchoring to keep generated data aligned with intended groups.
        profile_shift = {
            "supported_low_perfectionism_no_burnout": -0.12,
            "supported_high_perfectionism_no_burnout": -0.02,
            "unsupported_high_perfectionism_burnout": 0.13,
            "moderate_mixed": 0.05,
        }.get(self.profile_type, 0.0)

        noise = random.uniform(-0.05, 0.05)
        return _clamp(base + profile_shift + noise)
    
    def generate_perfectionism_responses(self) -> list:
        """Generate 15 perfectionism scale responses"""
        tendency = self.characteristics['perfectionism_tendency']
        
        responses = []
        for i in range(PERFECTIONISM_QUESTIONS_COUNT):
            current_tendency = self._question_tendency(tendency, i, "perfectionism")
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_social_support_responses(self) -> list:
        """Generate 12 social support scale responses"""
        tendency = self.characteristics['social_support_tendency']
        
        responses = []
        for i in range(SOCIAL_SUPPORT_QUESTIONS_COUNT):
            current_tendency = self._question_tendency(tendency, i, "social_support")
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_burnout_responses(self, tendency: float = None) -> list:
        """Generate 15 academic burnout scale responses"""
        if tendency is None:
            tendency = self.generate_burnout_tendency()
        
        responses = []
        for i in range(BURNOUT_QUESTIONS_COUNT):
            current_tendency = self._question_tendency(tendency, i, "burnout")
            responses.append(self.generate_likert_response(current_tendency))
        
        return responses
    
    def generate_complete_survey(self, profile_key: str = None) -> dict:
        """Generate complete survey response for a student"""
        self.assign_profile(profile_key=profile_key)

        burnout_tendency = self.generate_burnout_tendency()
        
        return {
            "profile": self.profile_type,
            "response_style": self.response_style,
            "perfectionism": self.generate_perfectionism_responses(),
            "social_support": self.generate_social_support_responses(),
            "burnout": self.generate_burnout_responses(burnout_tendency),
            "burnout_tendency": burnout_tendency,
            "proposal_pressure_tendency": self.characteristics.get('proposal_pressure_tendency', 0.5),
        }


def generate_all_responses(num_students: int) -> list:
    """Generate survey responses for all students with proportional profile quotas."""
    generator = ResponseGenerator()
    all_responses = []

    profile_keys = list(RESPONSE_PROFILES.keys())
    total_weight = sum(RESPONSE_PROFILES[k].get("count", 1) for k in profile_keys)

    raw_targets = {
        k: (num_students * RESPONSE_PROFILES[k].get("count", 1) / total_weight)
        for k in profile_keys
    }

    allocations = {k: int(raw_targets[k]) for k in profile_keys}
    assigned = sum(allocations.values())
    remaining = num_students - assigned

    if remaining > 0:
        # Fill remaining slots using largest fractional parts first.
        by_fraction = sorted(
            profile_keys,
            key=lambda k: raw_targets[k] - int(raw_targets[k]),
            reverse=True,
        )
        for i in range(remaining):
            allocations[by_fraction[i % len(by_fraction)]] += 1

    profile_plan = []
    for key in profile_keys:
        profile_plan.extend([key] * allocations[key])

    random.shuffle(profile_plan)

    for profile_key in profile_plan:
        best_candidate = None
        best_distance = float("inf")

        for _ in range(12):
            candidate = generator.generate_complete_survey(profile_key=profile_key)
            perf_score = _score_answers(candidate["perfectionism"])
            social_score = _score_answers(candidate["social_support"])
            burnout_score = _score_answers(candidate["burnout"])

            if _is_consistent_with_profile(profile_key, perf_score, social_score, burnout_score):
                best_candidate = candidate
                break

            target = PROFILE_SCORE_RANGES[profile_key]
            p_mid = sum(target["perfectionism_score"]) / 2
            s_mid = sum(target["social_support_score"]) / 2
            b_mid = sum(target["burnout_score"]) / 2
            distance = abs(perf_score - p_mid) + abs(social_score - s_mid) + abs(burnout_score - b_mid)

            if distance < best_distance:
                best_distance = distance
                best_candidate = candidate

        all_responses.append(best_candidate)

    _apply_controlled_outliers(all_responses)
    _tune_burnout_mix(all_responses)
    
    return all_responses