"""
Browser Controller for Item AI Assistant
Controls web browser automation using Selenium.
"""

import time
from typing import Optional, Dict
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.firefox.service import Service as FirefoxService

from item_assistant.config import get_config
from item_assistant.logging import get_log_manager

logger = get_log_manager().get_logger()
log_manager = get_log_manager()


class BrowserController:
    """Controls web browser automation"""
    
    def __init__(self):
        """Initialize browser controller"""
        self.config = get_config()
        self.driver = None
        self.default_browser = self.config.get("desktop.browser.default", "chrome")
        logger.info(f"Browser controller initialized (default: {self.default_browser})")
    
    def _init_driver(self, browser: Optional[str] = None):
        """
        Initialize browser driver
        
        Args:
            browser: Browser to use ('chrome', 'edge', 'firefox')
        """
        if self.driver is not None:
            return  # Already initialized
        
        browser = browser or self.default_browser
        browser = browser.lower()
        
        try:
            options = None
            
            if browser == "chrome":
                options = webdriver.ChromeOptions()
                options.add_argument("--start-maximized")
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                
            elif browser == "edge":
                options = webdriver.EdgeOptions()
                options.add_argument("--start-maximized")
                service = EdgeService(EdgeChromiumDriverManager().install())
                self.driver = webdriver.Edge(service=service, options=options)
                
            elif browser == "firefox":
                options = webdriver.FirefoxOptions()
                service = FirefoxService(GeckoDriverManager().install())
                self.driver = webdriver.Firefox(service=service, options=options)
            
            else:
                raise ValueError(f"Unsupported browser: {browser}")
            
            logger.info(f"Initialized {browser} browser driver")
            
        except Exception as e:
            log_manager.log_error("browser_init", f"Failed to initialize browser: {str(e)}")
            raise
    
    def open_url(self, url: str, browser: Optional[str] = None) -> Dict:
        """
        Open a URL in the browser
        
        Args:
            url: URL to open
            browser: Browser to use (optional)
        
        Returns:
            Dictionary with status and message
        """
        try:
            self._init_driver(browser)
            
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = f'https://{url}'
            
            self.driver.get(url)
            log_manager.log_action("open_url", url, "completed")
            
            return {
                "success": True,
                "message": f"Opened {url}"
            }
        
        except Exception as e:
            log_manager.log_error("open_url", str(e))
            return {
                "success": False,
                "message": f"Failed to open URL: {str(e)}"
            }
    
    def search_google(self, query: str) -> Dict:
        """
        Search on Google
        
        Args:
            query: Search query
        
        Returns:
            Dictionary with status and message
        """
        try:
            self._init_driver()
            
            # Go to Google
            self.driver.get("https://www.google.com")
            
            # Find search box and enter query
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            search_box.clear()
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            log_manager.log_action("search_google", query, "completed")
            
            return {
                "success": True,
                "message": f"Searched Google for: {query}"
            }
        
        except Exception as e:
            log_manager.log_error("search_google", str(e))
            return {
                "success": False,
                "message": f"Search failed: {str(e)}"
            }
    
    def navigate_to_youtube(self, video_name: Optional[str] = None) -> Dict:
        """
        Navigate to YouTube and optionally search for a video
        
        Args:
            video_name: Video name to search for (optional)
        
        Returns:
            Dictionary with status and message
        """
        try:
            self._init_driver()
            
            # Go to YouTube
            self.driver.get("https://www.youtube.com")
            time.sleep(2)
            
            if video_name:
                # Find search box and enter video name
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "search_query"))
                )
                search_box.clear()
                search_box.send_keys(video_name)
                search_box.send_keys(Keys.RETURN)
                
                time.sleep(3)
                
                # Click first video
                try:
                    first_video = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "video-title"))
                    )
                    first_video.click()
                    
                    log_manager.log_action("navigate_to_youtube", f"Playing: {video_name}", "completed")
                    
                    return {
                        "success": True,
                        "message": f"Playing video: {video_name}"
                    }
                except:
                    return {
                        "success": True,
                        "message": f"Searched for: {video_name} (couldn't auto-play)"
                    }
            else:
                log_manager.log_action("navigate_to_youtube", "home", "completed")
                return {
                    "success": True,
                    "message": "Navigated to YouTube"
                }
        
        except Exception as e:
            log_manager.log_error("navigate_to_youtube", str(e))
            return {
                "success": False,
                "message": f"YouTube navigation failed: {str(e)}"
            }
    
    def click_element(self, selector: str, by: str = "css") -> Dict:
        """
        Click an element on the page
        
        Args:
            selector: CSS selector, XPath, or ID
            by: Selector type ('css', 'xpath', 'id')
        
        Returns:
            Dictionary with status and message
        """
        try:
            if self.driver is None:
                return {
                    "success": False,
                    "message": "No browser session active"
                }
            
            by_type = {
                'css': By.CSS_SELECTOR,
                'xpath': By.XPATH,
                'id': By.ID
            }.get(by.lower(), By.CSS_SELECTOR)
            
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            
            log_manager.log_action("click_element", selector, "completed")
            
            return {
                "success": True,
                "message": f"Clicked element: {selector}"
            }
        
        except Exception as e:
            log_manager.log_error("click_element", str(e))
            return {
                "success": False,
                "message": f"Click failed: {str(e)}"
            }
    
    def get_page_title(self) -> Optional[str]:
        """Get current page title"""
        if self.driver:
            return self.driver.title
        return None
    
    def get_current_url(self) -> Optional[str]:
        """Get current page URL"""
        if self.driver:
            return self.driver.current_url
        return None
    
    def go_back(self) -> Dict:
        """Navigate back"""
        try:
            if self.driver is None:
                return {"success": False, "message": "No browser session active"}
            
            self.driver.back()
            return {"success": True, "message": "Navigated back"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def go_forward(self) -> Dict:
        """Navigate forward"""
        try:
            if self.driver is None:
                return {"success": False, "message": "No browser session active"}
            
            self.driver.forward()
            return {"success": True, "message": "Navigated forward"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def refresh(self) -> Dict:
        """Refresh page"""
        try:
            if self.driver is None:
                return {"success": False, "message": "No browser session active"}
            
            self.driver.refresh()
            return {"success": True, "message": "Page refreshed"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def close_browser(self) -> Dict:
        """Close the browser"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                log_manager.log_action("close_browser", "all", "completed")
                return {"success": True, "message": "Browser closed"}
            return {"success": True, "message": "No browser to close"}
        except Exception as e:
            return {"success": False, "message": str(e)}


# Global browser controller instance
_browser_controller_instance = None


def get_browser_controller() -> BrowserController:
    """Get the global browser controller instance"""
    global _browser_controller_instance
    if _browser_controller_instance is None:
        _browser_controller_instance = BrowserController()
    return _browser_controller_instance
