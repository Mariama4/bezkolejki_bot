from multiprocessing import cpu_count, Manager, Process
from zipfile import ZipFile
import requests
from loguru import logger
import bot as bot

PARSE_CONFIG = [
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },    {
        'url': 'https://www.bezkolejki.eu/luwlodz',
        'button': 'SIERADZ - Pobyt i praca - Złożenie wniosku'
    },
]


def updateExtansion():
    # Download and load the NopeCHA extension
    with open('chrome.zip', 'wb') as f:
        f.write(requests.get('https://nopecha.com/f/chrome.zip').content)

    # loading the temp.zip and creating a zip object
    with ZipFile("chrome.zip", 'r') as zObject:
        # Extracting all the members of the zip
        # into a specific location.
        zObject.extractall(
            path="nopecha/")


if __name__ == '__main__':
    updateExtansion()

    logger.info(
        'Запуск скрипта...'
    )

    task_count = len(PARSE_CONFIG)
    max_tasks = cpu_count()

    if task_count <= max_tasks:
        with Manager() as manager:
            BezkolejkiCalendar = manager.list()
            processes = [Process(target=bot.main, args=(PARSE_CONFIG[i], BezkolejkiCalendar)) for i in range(task_count)]
            # start all processes
            for process in processes:
                process.start()
            # wait for all processes to complete
            for process in processes:
                process.join()
            logger.critical(f'Результат: {BezkolejkiCalendar}')

    else:
        logger.error(f'Слишком много задач! Максимально: {max_tasks}')

