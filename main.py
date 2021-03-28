from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from random import randint
import requests
import time
import os
import csv
import re
import sys
import traceback
from twocaptcha import TwoCaptcha


def solve_img_captcha(img):
    print('Капча! Решаем...')
    api_key = os.getenv('APIKEY_2CAPTCHA', API_KEY)
    solver = TwoCaptcha(api_key)
    p = requests.get(img.get_attribute('src'))
    with open("captchaimg.jpg", "wb") as f:
        f.write(p.content)
    result = solver.normal('captchaimg.jpg')
    os.remove('captchaimg.jpg')
    driver.implicitly_wait(15)
    return result['code']


API_KEY = '68e90f633c32452ef3b7dc5111e3dc60'
try:
    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0")

    options.set_preference("dom.webdriver.enabled", False)
    options.headless = True

    driver = webdriver.Firefox(
        executable_path=GeckoDriverManager().install(),
        options=options
    )
except Exception as e:
    print('Неудачная настройка браузера!')
    print(traceback.format_exc())
    print(input('Press ENTER to close this program'))
    sys.exit()
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
urls = []
data_without_mail = []
data = []
regex = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
try:
    all_pages = list()
    try:
        with open('data.txt', mode='r') as f:
            file = f.read().split('\n')
    except Exception as e:
        print('Неудачное чтение файла!')
        print(traceback.format_exc())
        print(input('Press ENTER to close this program'))
        sys.exit()
    for i in range(len(file)):
        print(f'Ввод поисковых запросов {i + 1} из {len(file)}')
        search = file[i]
        if search != '' and search != ' ':
            for p in range(25):
                url = f'https://yandex.ru/search/?lr=20103&text={search}&p={p}'
                driver.get(url)
                driver.implicitly_wait(15)
                time.sleep(0.5)
                pages = driver.find_elements_by_xpath('//h2/a')
                if pages == []:
                    try:
                        img = driver.find_element_by_xpath('//img[@src]')
                        key = solve_img_captcha(img)
                        inp = driver.find_element_by_xpath('//input[@name="rep"]')
                        inp.send_keys(key + Keys.ENTER)
                        print('Капча решена')
                    except Exception:
                        try:
                            inp = driver.find_element_by_xpath('/html/body/div/div/div/div[3]/div/form/div/div[1]/input')
                            inp.click()
                            img = driver.find_element_by_xpath('//img[@src]')
                            key = solve_img_captcha(img)
                            inp = driver.find_element_by_xpath('//input[@id="xuniq-0-1"]')
                            inp.send_keys(key + Keys.ENTER)
                        except Exception:
                            pass
                pages = driver.find_elements_by_xpath('//h2/a')
                for j in pages:
                    all_pages.append(j.get_attribute('href'))
    driver.set_page_load_timeout(10)
    print(f'Найдено всего {len(all_pages)} сайтов')
    for q in range(len(all_pages)):
        email = 'Почта не найдена'
        print(f'Парсинг почт {q + 1} из {len(all_pages)}')
        try:
            driver.get(all_pages[q])
            driver.implicitly_wait(15)
            url = driver.current_url
        except Exception:
            pass
        try:
            body = driver.find_element_by_xpath('/html').text
            email = re.findall(regex, body)[-1]
        except Exception as e:
            email = 'Почта не найдена'
        data.append((email, all_pages[q]))
        driver.implicitly_wait(15)
    with open('result.csv', mode='w', newline='') as f:
        print('Запись в csv...')
        writer = csv.writer(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(('Почта', 'Ссылка'))
        for i in data:
            if i[0] != 'Почта не найдена':
                writer.writerow(i)
        print('Запись завершена')
    print('Парсинг завершён')
except Exception as e:
    print('Ошибка:\n', traceback.format_exc())
finally:
    driver.close()
    driver.quit()
    print(input('Press ENTER to close this program'))
