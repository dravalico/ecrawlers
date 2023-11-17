import os
import requests
import time
import datetime
import json
import calendar
import logging


class CVECrawler:
    def __init__(self,
                 path_storage='/Users/dravalico/PycharmProjects/CVECrawler/CVE',
                 update_interval=3600,
                 retry_interval=60):
        self.path_storage = path_storage
        self.update_interval = update_interval
        self.retry_interval = retry_interval
        self.endpoint_cve = 'https://cveawg.mitre.org/api/cve/CVE-'
        log_format = f'[%(levelname)s at %(asctime)s] %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    def run(self):
        if not os.path.exists(self.path_storage):
            os.makedirs(self.path_storage)
        while True:
            try:
                with open(os.path.join(self.path_storage, '.last_cve.txt'), 'r', encoding='utf-8') as file:
                    content = file.read()
                splitted_content = content.split(',')
                year = splitted_content[0]
                index = splitted_content[1]
                self.download_data(int(year), int(index))
            except FileNotFoundError:
                self.download_data()
            time.sleep(self.update_interval)

    def is_new_instance(self):
        if not self.retrieve_years_folders():
            return True
        return False

    def retrieve_years_folders(self):
        return [folder for folder in os.listdir(self.path_storage) if
                os.path.isdir(os.path.join(self.path_storage, folder)) and not folder.startswith('.')]

    def download_data(self, year_from=1999, cve_from=1):
        for year in range(year_from, int(datetime.date.today().year) + 1):
            for i in range(cve_from, 60000):
                with open(os.path.join(self.path_storage, '.last_cve.txt'), 'w', encoding='utf-8') as file:
                    file.write(f'{year},{i}')
                url = self.endpoint_cve + str(year) + '-' + str(i).zfill(4)
                try:
                    response = requests.get(url)
                    if response.status_code == 200:
                        self.save_data(response.json())
                        logging.info(f'Data obtained for {url.split("/")[-1]}')
                    elif response.status_code == 404:
                        logging.info(f'{url.split("/")[-1]} does not exists, error {response.status_code}')
                    elif response.status_code == 429:
                        time.sleep(self.retry_interval)
                    else:
                        logging.warning(f'Cannot obtain data for {url.split("/")[-1]}')
                except:
                    logging.exception(f'Error for {url.split("/")[-1]} during GET')

    def save_data(self, json_data):
        date = json_data['cveMetadata']['dateReserved']
        splitted_date = date.split('-')
        year = splitted_date[0]
        month = splitted_date[1]
        month_full = month + "-" + calendar.month_name[int(month.lstrip('0'))]
        day = splitted_date[2].split('T')[0]
        year_path = os.path.join(self.path_storage, year)
        if not os.path.exists(year_path):
            os.makedirs(year_path)
        month_path = os.path.join(year_path, month_full[:6])
        if not os.path.exists(month_path):
            os.makedirs(month_path)
        with open(os.path.join(month_path, f'{year}_{month}_{day}.jsonl'), 'a', encoding='utf-8') as file:
            file.write(json.dumps(json_data) + '\n')
