import time
import os
from config import FORM_URL, CSV_FILE, NUM_SUBMISSIONS, BROWSER_HEADLESS, DRY_RUN
from utils import load_student_names, get_demographic_for_name, assign_cohort_distribution
from data_generator import generate_all_responses
from form_filler import GoogleFormFiller
from result_analyzer import ResultAnalyzer

def main():
    print("=" * 60)
    print("FORM FILLER AUTOMATION - ACADEMIC BURNOUT SURVEY")
    print("=" * 60)
    
    # Step 1: Load student names
    print("\n[Step 1] Loading student names from CSV...")
    student_names = load_student_names(CSV_FILE, NUM_SUBMISSIONS)
    
    if not student_names:
        print("Failed to load student names. Exiting.")
        return
    
    print(f"✓ Loaded {len(student_names)} student names")
    
    # Step 2: Generate survey responses
    print("\n[Step 2] Generating realistic survey responses...")
    all_responses = generate_all_responses(len(student_names))
    print(f"✓ Generated {len(all_responses)} complete survey responses")
    
    # Step 3: Get cohort distribution
    print("\n[Step 3] Determining demographic distribution...")
    cohort_dist = assign_cohort_distribution(len(student_names))
    print(f"✓ Cohort distribution - 2023: {cohort_dist['2023']*100:.0f}%, 2022: {cohort_dist['2022']*100:.0f}%")
    
    # Step 4: Fill forms
    print("\n[Step 4] Starting form automation...")
    print(f"Mode: {'DRY_RUN (no submit)' if DRY_RUN else 'LIVE (submit)'}")
    print(f"Submissions to complete: {len(student_names)}")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = ResultAnalyzer()
    
    filler = GoogleFormFiller(FORM_URL, headless=BROWSER_HEADLESS)
    filler.setup_driver()
    filler.open_form()
    
    successful = 0
    failed = 0
    
    for idx, (name, responses) in enumerate(zip(student_names, all_responses), 1):
        print(f"\n[{idx}/{len(student_names)}] Processing: {name}")
        
        # Get demographics for this student
        demographics = get_demographic_for_name(name, cohort_dist)
        print(f"  → Cohort: {demographics['angkatan']}")
        print(f"  → Program: {demographics['program_studi']}")
        print(f"  → Gender: {demographics['jenis_kelamin']}")
        print(f"  → Profile: {responses['profile']}")
        
        # Fill the form
        if filler.fill_complete_survey(demographics, responses):
            successful += 1
            analyzer.add_result(demographics, responses, status="success")
        else:
            failed += 1
            analyzer.add_result(demographics, responses, status="failed")
        
        # Small delay between submissions
        if idx < len(student_names):
            filler.reset_form()
            print("  → Waiting before next submission...")
            time.sleep(3)
    
    # Summary
    print("\n" + "=" * 60)
    print("SURVEY COMPLETION SUMMARY")
    print("=" * 60)
    print(f"Total Attempted: {len(student_names)}")
    print(f"✓ Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(successful/len(student_names)*100):.1f}%")
    print("=" * 60)
    
    # Analysis and export
    analyzer.export_csv()
    analyzer.print_summary()
    
    filler.close()
    print("\n✓ Form filler automation completed!")

if __name__ == "__main__":
    main()