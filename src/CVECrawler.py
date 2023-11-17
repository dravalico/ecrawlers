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
                 update_interval=0,
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
        if self.is_new_instance():
            self.download_all()
        while True:
            self.download_new_data()
            time.sleep(self.update_interval)

    def is_new_instance(self):
        if not self.retrieve_years_folders():
            return True
        return False

    def retrieve_years_folders(self):
        return [folder for folder in os.listdir(self.path_storage) if
                os.path.isdir(os.path.join(self.path_storage, folder)) and not folder.startswith('.')]

    def download_all(self, year_from=1999):
        for year in range(year_from, int(datetime.date.today().year) + 1):
            for i in range(553, 60000):
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

    def download_new_data(self):
        pass

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

    @staticmethod
    def retrieve_last_CVE_ID_online():
        endpoint_cve = 'https://services.nvd.nist.gov/rest/json/cves/1.0'
        response = requests.get(endpoint_cve)
        if response.status_code == 200:
            data = response.json()
            cve_items = data['result']['CVE_Items']
            cve_id_list = []
            if cve_items:
                for e in cve_items:
                    cve_id_list.append(int(e['cve']['CVE_data_meta']['ID'].split('-')[2]))
            return max(cve_id_list)

    def retrieve_last_CVE_ID_local(self):
        pass
