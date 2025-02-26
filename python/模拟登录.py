import os, re, time
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class Get_ROLEID_and_sessionID():
    def __init__(self, path):
        self.path = path

        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        prefs = {
            'download.default_directory': self.path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True
        }

        chrome_options.add_experimental_option('prefs', prefs)
        self.browser = webdriver.Chrome(options=chrome_options)

    def main(self, username, password):
        url = "https://zhlgd.whut.edu.cn/tpass/login?service=https%3A%2F%2Fjwxt.whut.edu.cn%2Fjwapp%2Fsys%2Fhomeapp%2Findex.do%3FforceCas%3D1"
        self.browser.get(url)

        WebDriverWait(self.browser, 20, 1).until(EC.presence_of_element_located((By.ID, "index_login_btn")))
        self.browser.find_element(By.ID, "un").send_keys(username)
        self.browser.find_element(By.ID, "pd").send_keys(password)
        self.browser.find_element(By.ID, "index_login_btn").click()

        url = "https://jwxt.whut.edu.cn/jwapp/sys/homeapp/home/index.html?av=1739265855174&contextPath=/jwapp#/"
        self.browser.get(url)

        yx = "/html/body/div/div/div/div[1]/div[2]/div[2]/div//div[@title='运行']"
        WebDriverWait(self.browser, 20, 1).until(EC.presence_of_element_located((By.XPATH, yx)))
        self.browser.find_element(By.XPATH, yx).click()

        kb = "/html/body/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div[1]//div[@title='我的课表（本研）']"
        WebDriverWait(self.browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, kb)))
        self.browser.find_element(By.XPATH, kb).click()

        cb = "/html/body/div/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div[1]//div[@title='学生课程表']"
        WebDriverWait(self.browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, cb)))
        self.browser.find_element(By.XPATH, cb).click()

        WebDriverWait(self.browser, 20, 1).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div[2]/div/div[2]/iframe")))
        iframe = self.browser.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[2]/div[2]/div/div[2]/iframe")
        print("pageMeta.params.ROLEID(_yhz):", iframe.get_attribute("src"))

        url = iframe.get_attribute("src")
        self.browser.get(url)

        WebDriverWait(self.browser, 60, 1).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/article/h2/a")))
        self.browser.find_element(By.XPATH, "/html/body/main/article/h2/a").click()
        WebDriverWait(self.browser, 20, 1).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[7]/div[2]/div[1]/div/div[2]/div")))
        self.browser.find_element(By.XPATH, "/html/body/div[7]/div[2]/div[1]/div/div[2]/div").click()
        WebDriverWait(self.browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[9]/div/div/div/div[2]/div/div[2]")))
        self.browser.find_element(By.XPATH, "/html/body/div[9]/div/div/div/div[2]/div/div[2]").click()
        WebDriverWait(self.browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[7]/div[2]/div[2]/button[2]")))
        self.browser.find_element(By.XPATH, "/html/body/div[7]/div[2]/div[2]/button[2]").click()
        WebDriverWait(self.browser, 20, 1).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/article/section/div[2]/a[1]")))
        self.browser.find_element(By.XPATH, "/html/body/main/article/section/div[2]/a[1]").click()

        WebDriverWait(self.browser, 60, 1).until(EC.presence_of_element_located((By.ID, "printForm")))
        self.browser.switch_to.frame(self.browser.find_element(By.ID, "printForm"))

        WebDriverWait(self.browser, 20, 1).until(EC.presence_of_element_located((By.XPATH, "//script[4]")))
        script_element = self.browser.find_element(By.XPATH, "//script[4]")

        match = re.search(r"FR\.SessionMgr\.register\('(\d+)', contentPane\);", script_element.get_attribute('innerHTML'))
        print("FR.SessionMgr.getSessionID()(sessionID):", match.group(1))

        url = f"https://jwxt.whut.edu.cn/jwapp/sys/frReport2/show.do?op=export&sessionID={match.group(1)}&format=excel&extype=simple"
        self.browser.get(url)

        downloaded_file = self.wait_for_download(self.path)
        print(downloaded_file)

    def wait_for_download(self, download_dir, timeout=30):
        start_time = time.time()
        previous_files = os.listdir(download_dir)
        while time.time() - start_time < timeout:
            current_files = os.listdir(download_dir)
            new_files = set(current_files) - set(previous_files)
            if new_files:
                for file in new_files:
                    if file.endswith('.xlsx'):
                        return os.path.join(download_dir, file)
            previous_files = current_files
            time.sleep(1)
        return "ERROR"


if __name__ == "__main__":
    obj = Get_ROLEID_and_sessionID(path=r"D:\Work Files\examine")
    obj.main(username="******", password="******")
