import os
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def setup_teardown():
    # Setup directory for failure screenshots
    os.makedirs("docs/screenshots/failures", exist_ok=True)
    yield

@pytest.fixture
def driver(request, setup_teardown):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=options)
    # Using explicit waits mostly, but a small implicit wait for generic element finding
    driver.implicitly_wait(2)
    
    yield driver
    
    # Simple screenshot capture on failure
    if request.node.rep_call.failed:
        screenshot_name = f"docs/screenshots/failures/{request.node.name}_failure.png"
        driver.save_screenshot(screenshot_name)
        print(f"\nScreenshot saved to {screenshot_name}")
        
    driver.quit()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
