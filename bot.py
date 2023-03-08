import asyncio
import datetime
import random
import time
import multiprocessing

from bs4 import BeautifulSoup
from loguru import logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import undetected_chromedriver.v2 as uc

NOPECHA_KEY = ''


def timer(process):
    today = datetime.datetime.today()
    deadline = datetime.datetime(today.year, today.month, today.day, 10, 0)
    now = datetime.datetime.now()
    timeout = deadline - now
    timeout =timeout.seconds
    # timeout = timeout.seconds + timeout.microseconds / 1000000
    logger.debug(f'{process.name} остановлен на {timeout} секунд...')
    time.sleep(timeout)


async def initSession():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--no-first-run --no-service-autorun --password-store=basic')
    # options.add_argument('--headless=chrome')
    # options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36")

    options.add_argument("--load-extension=C:\\Users\\Administrator\\Desktop\\bezkolejki_bot\\nopecha")
    driver = uc.Chrome(options=options)
    driver.get(f"https://nopecha.com/setup#{NOPECHA_KEY}")

    return driver


async def clickOnElementByTextUsingJS(type='', text='', driver=None):
    xpath = f"//{type}[text()='{text}']"
    try:
        driver.execute_script(f"""
        let getElementByXpath = path => document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
        getElementByXpath("{xpath}").click()
        """)
    except Exception as ex:
        return ex
    return True


async def closeModal(driver):
    _ = "//*[@id='app']/div[2]/div[1]/div/div[2]/div/div[1]"
    driver.execute_script(f"""
                        let getElementByXpath = path => document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;       
                        getElementByXpath("{_}").click()
                        """)
    return True


async def asyncChoice(options):
    return random.choice(options)


async def getDateTime(driver, url, button, BezkolejkiCalendar):
    page = driver.page_source
    soap = BeautifulSoup(page, 'lxml')
    spans = soap.findAll('span', class_='vc-focusable')
    for span in spans:
        if 'is-disabled' not in str(span):
            day = span.get('aria-label')
            _ = f"//span[@aria-label='{day}']"
            driver.execute_script(f"""
                    let getElementByXpath = path => document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;       
                    getElementByXpath("{_}").click()
                    """)
            await asyncio.sleep(0.5)

            select = Select(driver.find_element(By.ID, 'selectTime'))
            for option in select.options:
                time = option.text

                data = {
                        "url": url,
                        "button": button,
                        "day": day,
                        "time": time
                    }

                condition = data in BezkolejkiCalendar
                if not condition:
                    BezkolejkiCalendar.append(data)

                if not condition:
                    option.click()
                    return data
            await closeModal(driver)
    else:
        return False


async def getDatetime(driver, url, buttonText, buttonNext, BezkolejkiCalendar):

    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f"//button[text()='{buttonNext}']")))

    response = await clickOnElementByTextUsingJS(type='button', text=buttonText, driver=driver)

    response = await clickOnElementByTextUsingJS(type='button', text=buttonNext, driver=driver)
    await asyncio.sleep(1)

    title = driver.find_element(By.XPATH, '// *[ @ id = "Dataiczas3"] / div / div[1] / div[1] / div / h5').text

    if title == ' Brak dostępnych terminów do rezerwacji ':
        return None

    response = await getDateTime(driver, url, buttonText, BezkolejkiCalendar)

    return response


async def passFreeRecord(config, BezkolejkiCalendar):
    currentProcess = multiprocessing.current_process()

    logger.debug(
        f'Процесс "{currentProcess.name}" запущен...'
    )
    url = config['url']
    buttonText = config['button']
    buttonNext = "Dalej"

    driver = await initSession()

    firstTime = True

    while True:

        driver.get(url)

        if firstTime:
            timer(process=currentProcess)
            firstTime = False

        logger.debug(f'{currentProcess.name} - Начат поиск дат на кнопке - {buttonText}')

        response = await getDatetime(driver, url, buttonText, buttonNext, BezkolejkiCalendar)

        if response is None:
            logger.error(f'{currentProcess.name} - IP заблокирован, повторная попытка... - {buttonText}')
            continue
        break

    if not response:
        logger.error(f'{currentProcess.name} - {buttonText} - В календаре нет мест.')
        # session.close()
    else:
        logger.info(f'{currentProcess.name} - Время найдено: {response}')
        logger.debug(f'{currentProcess.name} - Капча в процессе....')
        try:
            iframe = WebDriverWait(driver, 120).until(EC.visibility_of_element_located(
                (By.CSS_SELECTOR, 'iframe[data-hcaptcha-response]:not([data-hcaptcha-response=""]')))
            token = iframe.get_attribute('data-hcaptcha-response')

            logger.warning(f'{currentProcess.name} - Капча решена | Результат - {response}')
            response = await clickOnElementByTextUsingJS(type='button', text=buttonNext, driver=driver)
            await asyncio.sleep(60000)
        except Exception as error:
            logger.error(f'{currentProcess.name} - Капча не решена за 2 минуты: {response}')


def main(config, BezkolejkiCalendar):
    asyncio.run(passFreeRecord(config, BezkolejkiCalendar))
