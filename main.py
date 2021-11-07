from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import requests
import os
from time import sleep
import random

SO_LOGIN = 'https://stackoverflow.com/users/login'
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.2 Safari/605.1.15',
    'Mozilla/5.0 (Linux; Android 7.1.2; AFTMM Build/NS6265; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/70.0.3538.110 Mobile Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/601.7.7 (KHTML, like Gecko) Version/9.1.2 Safari/601.7.7',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/601.5.17 (KHTML, like Gecko) Version/9.1 Safari/601.5.17',
]

class GmailPicDownloader:
    """
    Download Profile Picture of a Gmail account. If a webdriver already exists pass it as an argument. Firefox is preferred
    as it was used for developing this script. If webdriver doesn't exists or you want create a new one, you must pass the 
    address of geckodriver for Firefox as key argument.
    username and password arguments are for logging in to gmail.
    target_email is the profile which its picture will be downloaded.

    Note: If mouse hover doesn't work when the target email is entered in the field, run script again and move your mouse out of browser screen.
    """
    def __init__(self, username, password, target_email='', firefox_executable_path='./geckodriver', driver=None):
        self.username = username
        self.password = password
        self.target_email = target_email
        if driver:
            self.driver = driver
        else:
            profile = webdriver.FirefoxProfile()
            profile.set_preference('general.useragent.override', random.choice(USER_AGENTS))
            self.driver = webdriver.Firefox(executable_path=firefox_executable_path)
        self.wait = WebDriverWait(self.driver, 20)
    
    def __exit__(self):
        self.driver.close()


    def set_target_email(self, email):
        """
        Set the target email address.
        """
        self.target_email = email

    def login_gmail(self):
        """
        Login to gmail using Stackoverflow website then going to mail.google.com. The reason for this
        is google doesn't allow direct login to gmail using Selenium.
        """
        self.driver.get(SO_LOGIN)
        google_login = self.driver.find_element_by_css_selector('button.s-btn__icon:nth-child(1)')
        google_login.click()
        self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="identifierNext"]')))
        login_field = self.driver.find_element_by_xpath('//*[@id="identifierId"]')
        login_field.send_keys(self.username)
        next_button = self.driver.find_element_by_xpath('//*[@id="identifierNext"]')
        next_button.click()
        self.wait.until(expected_conditions.element_to_be_clickable((By.XPATH, '//*[@type="password"]')))
        password_field = self.driver.find_element_by_xpath('//*[@type="password"]')
        password_field.send_keys(self.password)
        next_button = self.driver.find_element_by_xpath('//*[@id="passwordNext"]')
        next_button.click()
        sleep(1)
        self.driver.get('https://mail.google.com/#inbox')
        sleep(1)

    def get_img_url(self):
        """
        Get the profile picture URL when the script has logged in to gmail.
        """
        compose = self.driver.find_elements_by_css_selector('.T-I-KE')[-1]
        compose.click()
        self.wait.until(
            expected_conditions.element_to_be_clickable((By.XPATH, './/textarea[contains(@aria-label, "To")]'))
        )
        to = self.driver.find_element_by_xpath('.//textarea[contains(@aria-label, "To")]')
        to.send_keys(self.target_email + ' ')
        self.wait.until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, '.vT'))
        )
        mail_field = self.driver.find_element_by_css_selector('.vT')
        mail_field.click()
        sleep(0.3)
        mail_field = self.driver.find_element_by_css_selector('.vT')
        hover = ActionChains(self.driver).move_to_element(mail_field)
        hover.perform()
        self.wait.until(
            expected_conditions.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, '#__HC_94253229 > iframe:nth-child(1)'))
        )
        self.wait.until(
            expected_conditions.visibility_of_element_located((By.XPATH, './/*[@alt= "Profile Photo"]'))
        )
        photo = self.driver.find_element_by_xpath('.//*[@alt= "Profile Photo"]')
        return photo.get_attribute('src')


    def profile_has_pic(self, url):
        """
        If a google user doesn't have a photo, a default picture is used. This method
        checks if the image url is not the default picture url.
        """
        if 'default-user' in url:
            return False
        return True
        
    def download_profile_pic(self):
        """
        Gets image url and if the target user had profile picture, downloads the full size image.
        """
        url = self.get_img_url()
        if self.profile_has_pic(url):
            full_size_url = ''
            if url[-10:] == 's70-p-k-no':
                full_size_url = url[:-11]
            else:
                full_size_url = url[:url.find('s70') + 3] + '0' + url[url.find('s70') + 3:]
            img = requests.get(full_size_url)
            with open(os.path.dirname(os.path.abspath(__file__)) +  '/' + self.target_email + '.png', 'wb') as fp:
                fp.write(img.content)
                print('Downloaded Image!')
        else:
            print('User doesn\'t a profile picture!')


    
    def close(self):
        """
        Close the browser.
        """
        self.driver.close()



def main():
    target_email = input('Enter Mail: ') # eg. test@gmail.com
    downloader = GmailPicDownloader(username='gmail_username', password='password', target_email=target_email)
    downloader.login_gmail()
    downloader.download_profile_pic()
    downloader.close()

if __name__ == '__main__':
    main()
