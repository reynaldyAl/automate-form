import csv
import math
import os
from config import SCORE_MAPPING, PROFILE_SCORE_RANGES


class ResultAnalyzer:
    """Analyze survey responses and validate consistency"""
    
    def __init__(self, output_dir="results"):
        self.output_dir = output_dir
        self.results = []
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def add_result(self, demographics, survey_responses, status="success"):
        """Add a completed survey result"""
        # Score jawaban
        perf_score = self._score_answers(survey_responses['perfectionism'])
        social_score = self._score_answers(survey_responses['social_support'])
        burnout_score = self._score_answers(survey_responses['burnout'])
        burnout_level = self._get_burnout_level(burnout_score)
        
        # Check konsistensi dengan profile
        profile_type = survey_responses['profile']
        is_consistent = self._check_consistency(
            profile_type, perf_score, social_score, burnout_score
        )
        
        result = {
            "nama": demographics['nama'],
            "angkatan": demographics['angkatan'],
            "program_studi": demographics['program_studi'],
            "jenis_kelamin": demographics['jenis_kelamin'],
            "profile_assigned": profile_type,
            "response_style": survey_responses.get('response_style', 'balanced'),
            "perfectionism_score": perf_score,
            "perfectionism_max": 15 * 4,
            "social_support_score": social_score,
            "social_support_max": 12 * 4,
            "burnout_score": burnout_score,
            "burnout_max": 15 * 4,
            "burnout_level": burnout_level,
            "proposal_pressure_tendency": round(survey_responses.get('proposal_pressure_tendency', 0.5), 2),
            "is_consistent": is_consistent,
            "status": status,
        }
        
        self.results.append(result)
        return result
    
    @staticmethod
    def _score_answers(answers):
        """Calculate total score from answer list"""
        total = sum(SCORE_MAPPING.get(ans, 0) for ans in answers)
        return total
    
    @staticmethod
    def _check_consistency(profile, perf_score, social_score, burnout_score):
        """Check if scores match the assigned profile"""
        if profile not in PROFILE_SCORE_RANGES:
            return False
        
        ranges = PROFILE_SCORE_RANGES[profile]
        
        perf_ok = ranges["perfectionism_score"][0] <= perf_score <= ranges["perfectionism_score"][1]
        social_ok = ranges["social_support_score"][0] <= social_score <= ranges["social_support_score"][1]
        burnout_ok = ranges["burnout_score"][0] <= burnout_score <= ranges["burnout_score"][1]
        
        return perf_ok and social_ok and burnout_ok

    @staticmethod
    def _get_burnout_level(score):
        """Classify burnout intensity from the score."""
        if score >= 40:
            return "High"
        if score >= 28:
            return "Moderate"
        return "Low"

    @staticmethod
    def _pearson(x_values, y_values):
        """Compute Pearson correlation safely for small samples."""
        n = len(x_values)
        if n < 2:
            return 0.0

        mean_x = sum(x_values) / n
        mean_y = sum(y_values) / n
        num = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, y_values))
        den_x = math.sqrt(sum((x - mean_x) ** 2 for x in x_values))
        den_y = math.sqrt(sum((y - mean_y) ** 2 for y in y_values))
        if den_x == 0 or den_y == 0:
            return 0.0
        return num / (den_x * den_y)
    
    def export_csv(self, filename="survey_results.csv"):
        """Export results to CSV"""
        if not self.results:
            print("No results to export")
            return
        
        filepath = f"{self.output_dir}/{filename}"
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.results[0].keys())
                writer.writeheader()
                writer.writerows(self.results)
            print(f"✓ Exported {len(self.results)} results to {filepath}")
        except Exception as e:
            print(f"Error exporting CSV: {e}")
    
    def print_summary(self):
        """Print summary statistics"""
        if not self.results:
            print("No results to summarize")
            return
        
        print("\n" + "=" * 80)
        print("SURVEY RESULTS SUMMARY & ANALYSIS")
        print("=" * 80)
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        consistent = sum(1 for r in self.results if r['is_consistent'])
        
        print(f"\nTotal Responses: {total}")
        print(f"Successful Submissions: {successful} ({successful/total*100:.1f}%)")
        print(f"Consistent with Profile: {consistent} ({consistent/total*100:.1f}%)")

        quality_rate = consistent / total * 100
        quality_label = "Excellent" if quality_rate >= 92 else "Good" if quality_rate >= 82 else "Needs Tuning"
        print(f"Data Quality Label: {quality_label}")
        
        # Score statistics
        perf_scores = [r['perfectionism_score'] for r in self.results]
        social_scores = [r['social_support_score'] for r in self.results]
        burnout_scores = [r['burnout_score'] for r in self.results]
        
        print("\nPERFECTIONISM SCALE (15-60)")
        print(f"  Mean: {sum(perf_scores)/len(perf_scores):.1f}")
        print(f"  Range: {min(perf_scores)}-{max(perf_scores)}")
        
        print("\nSOCIAL SUPPORT SCALE (12-48)")
        print(f"  Mean: {sum(social_scores)/len(social_scores):.1f}")
        print(f"  Range: {min(social_scores)}-{max(social_scores)}")
        
        print("\nBURNOUT SCALE (15-60)")
        print(f"  Mean: {sum(burnout_scores)/len(burnout_scores):.1f}")
        print(f"  Range: {min(burnout_scores)}-{max(burnout_scores)}")

        perf_burn_corr = self._pearson(perf_scores, burnout_scores)
        support_burn_corr = self._pearson(social_scores, burnout_scores)
        print("\nRELATIONSHIP CHECK")
        print(f"  Corr(Perfectionism, Burnout): {perf_burn_corr:.3f} (expected positive)")
        print(f"  Corr(Social Support, Burnout): {support_burn_corr:.3f} (expected negative)")

        burnout_levels = {}
        for r in self.results:
            level = r['burnout_level']
            burnout_levels[level] = burnout_levels.get(level, 0) + 1

        print("\nBURNOUT LEVEL DISTRIBUTION")
        for level in ["High", "Moderate", "Low"]:
            count = burnout_levels.get(level, 0)
            if count:
                print(f"  {level}: {count} ({count/total*100:.1f}%)")
        
        # Profile distribution
        print("\nPROFILE DISTRIBUTION")
        profiles = {}
        for r in self.results:
            profile = r['profile_assigned']
            profiles[profile] = profiles.get(profile, 0) + 1
        
        for profile, count in sorted(profiles.items()):
            print(f"  {profile}: {count} ({count/total*100:.1f}%)")

        print("\nRESPONSE STYLE DISTRIBUTION")
        styles = {}
        for r in self.results:
            style = r['response_style']
            styles[style] = styles.get(style, 0) + 1
        for style, count in sorted(styles.items()):
            print(f"  {style}: {count} ({count/total*100:.1f}%)")
        
        # Consistency per profile
        print("\nCONSISTENCY BY PROFILE")
        for profile in sorted(profiles.keys()):
            prof_results = [r for r in self.results if r['profile_assigned'] == profile]
            consistent_count = sum(1 for r in prof_results if r['is_consistent'])
            consistency_rate = consistent_count / len(prof_results) * 100
            print(f"  {profile}: {consistent_count}/{len(prof_results)} ({consistency_rate:.1f}%)")
        
        # Show sample inconsistent responses
        inconsistent = [r for r in self.results if not r['is_consistent']]
        if inconsistent:
            print("\n⚠ INCONSISTENT RESPONSES (First 3)")
            for r in inconsistent[:3]:
                print(f"\n  {r['nama']}")
                print(f"    Profile: {r['profile_assigned']}")
                print(f"    Style: {r['response_style']}")
                print(f"    Perfectionism: {r['perfectionism_score']}/60")
                print(f"    Social Support: {r['social_support_score']}/48")
                print(f"    Burnout: {r['burnout_score']}/60")
                print(f"    Burnout Level: {r['burnout_level']}")

        print("\nINTERPRETATION")
        print("  - Higher perfectionism and higher proposal pressure are designed to raise academic burnout.")
        print("  - Higher social support is designed to reduce academic burnout.")
        print("  - 'Consistent' means the synthetic scores match the assigned latent profile, not that the form proves causality.")
        
        print("\n" + "=" * 80)
