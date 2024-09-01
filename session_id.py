from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass
import os


login = input("Enter your login : ")
password = getpass.getpass(prompt='Enter your password : ')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get('https://auth.42.fr/auth/realms/students-42/protocol/openid-connect/auth?client_id=intra&redirect_uri=https%3A%2F%2Fprofile.intra.42.fr%2Fusers%2Fauth%2Fkeycloak_student%2Fcallback&response_type=code&state=f43bc76d9ce9a0b8046c0c02cab73df701947019a9b5016c')

    wait = WebDriverWait(driver, 10)
    username_field = wait.until(EC.presence_of_element_located((By.ID, 'username')))
    
    username_field.send_keys(login)

    password_field = driver.find_element(By.ID, 'password')
    password_field.send_keys(password)
    login_button = driver.find_element(By.ID, 'kc-login')
    login_button.click()

    wait = WebDriverWait(driver, 15)
    cookie_name = '_intra_42_session_production'
    cookie = driver.get_cookie(cookie_name)

    if cookie:
        cookie_value = cookie['value']
        print(f'Your "{cookie_name}" is: {cookie_value}')
    else:
        print(f'"{cookie_name}" not found or login/password is incorrect.')
    file_path = 'cookies.json'
    if os.path.exists(file_path):
        os.remove(file_path)

finally:
    driver.quit()
