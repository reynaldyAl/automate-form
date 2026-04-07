from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from config import DRY_RUN

class GoogleFormFiller:
    """Automate filling the Google Form"""
    
    def __init__(self, form_url: str, headless: bool = False):
        self.form_url = form_url
        self.driver = None
        self.wait = None
        self.headless = headless
    
    def setup_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def open_form(self):
        """Open the Google Form"""
        print(f"Opening form: {self.form_url}")
        self.driver.get(self.form_url)
        time.sleep(2)

    def reset_form(self):
        """Reload the form to the first page."""
        self.open_form()
    
    def fill_demographics(self, demographics: dict) -> bool:
        try:
            print(f"Filling demographics for: {demographics['nama']}")

            # Google Form text answer bisa input atau textarea tergantung render
            name_input = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "input[type='text'], textarea")
                )
            )
            name_input.click()
            name_input.clear()
            name_input.send_keys(demographics["nama"])
            time.sleep(0.5)

            if not self.select_option(demographics["angkatan"]):
                return False
            time.sleep(0.5)

            if not self.select_option(demographics["program_studi"]):
                return False
            time.sleep(0.5)

            if not self.select_option(demographics["jenis_kelamin"]):
                return False
            time.sleep(0.5)

            return True
        except Exception as e:
            print(f"Error filling demographics: {e}")
            return False
    
    def select_option(self, option_text: str) -> bool:
        try:
            xpath = (
                f"//*[@role='radio' or @role='checkbox']"
                f"[@data-value='{option_text}' or @aria-label='{option_text}']"
            )
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"Could not select option {option_text}: {e}")
            return False
    
    def fill_scales(self, survey_responses: dict) -> bool:
        """
        Fill the three scales (Perfectionism, Social Support, Burnout)
        Returns True if successful
        """
        try:
            all_answers = (
                survey_responses["perfectionism"]
                + survey_responses["social_support"]
                + survey_responses["burnout"]
            )

            answered_count = 0
            total_needed = len(all_answers)

            while answered_count < total_needed:
                question_blocks = self._get_radio_question_blocks()
                if not question_blocks:
                    print("No radio question blocks found on current page.")
                    return False

                remaining = total_needed - answered_count
                to_answer_here = min(len(question_blocks), remaining)
                print(
                    f"Filling {to_answer_here} question(s) on current page "
                    f"(answered {answered_count}/{total_needed})..."
                )

                for local_idx in range(to_answer_here):
                    global_idx = answered_count + local_idx
                    answer = all_answers[global_idx]
                    if not self.select_scale_response_for_question(question_blocks[local_idx], answer):
                        print(f"Failed to answer question #{global_idx + 1} with value '{answer}'")
                        return False
                    time.sleep(0.2)

                answered_count += to_answer_here

                if answered_count < total_needed:
                    if not self.click_next():
                        print(
                            f"Could not navigate to next scale page. "
                            f"Progress={answered_count}/{total_needed}"
                        )
                        return False
                    time.sleep(1)
            
            return True
        except Exception as e:
            print(f"Error filling scales: {e}")
            return False

    def _get_radio_question_blocks(self):
        """Get listitem blocks that contain radio choices (one block per question)."""
        blocks = self.driver.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
        radio_blocks = []
        for block in blocks:
            radios = block.find_elements(By.CSS_SELECTOR, "div[role='radio'][data-value]")
            if radios:
                radio_blocks.append(block)
        return radio_blocks

    def select_scale_response_for_question(self, question_block, response_value: str) -> bool:
        """Select answer for a specific question block only."""
        try:
            option = question_block.find_element(
                By.CSS_SELECTOR,
                f"div[role='radio'][data-value='{response_value}']"
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
            self.driver.execute_script("arguments[0].click();", option)
            return True
        except Exception as e:
            print(f"Could not select response '{response_value}' for question block: {e}")
            return False
    
    def select_scale_response(self, response_value: str) -> bool:
        """Select a response (SS, S, TS, STS) from the scale"""
        try:
            # Find radio button with the matching data-value
            xpath = f"//div[@data-value='{response_value}' and @role='radio']"
            element = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception as e:
            print(f"Could not select response {response_value}: {e}")
            return False
    
    def click_next(self) -> bool:
        """Click Next button to go to next page"""
        try:
            next_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//span[contains(., 'Next') or contains(., 'Berikutnya')]"
                ))
            )
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Could not click Next: {e}")
            return False
    
    def click_submit(self) -> bool:
        """Click Submit button to submit the form"""
        try:
            submit_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//span[contains(., 'Submit') or contains(., 'Kirim')]"
                ))
            )
            self.driver.execute_script("arguments[0].click();", submit_button)
            time.sleep(2)
            return True
        except Exception as e:
            print(f"Could not click Submit: {e}")
            return False
    
    def fill_complete_survey(self, demographics: dict, survey_responses: dict) -> bool:
        """
        Fill the complete survey (demographics + all scales)
        """
        try:
            # Page 1: Fill demographics
            if not self.fill_demographics(demographics):
                return False
            
            time.sleep(1)
            
            # Click Next to go to scales page
            if not self.click_next():
                return False
            
            time.sleep(1)
            
            # Page 2: Fill all scales
            if not self.fill_scales(survey_responses):
                return False
            
            time.sleep(1)
            
            if DRY_RUN:
                print(f"[DRY RUN] Form filled for {demographics['nama']} (submit skipped)")
                return True

            if not self.click_submit():
                return False

            print(f"✓ Successfully submitted survey for {demographics['nama']}")
            return True
        
        except Exception as e:
            print(f"Error filling complete survey: {e}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()