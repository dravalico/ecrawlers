import logging
import os
import datetime
import requests
import time


class EPSSCrawler:
    def __init__(self,
                 storage_path='/usr/src/data',
                 request_timeout=60,
                 interval_between_requests=6,
                 update_interval=86400,
                 retry_interval=300,
                 retries_for_request=9):
        self.storage_path = storage_path
        self.request_timeout = request_timeout
        self.interval_between_requests = interval_between_requests
        self.update_interval = update_interval
        self.retry_interval = retry_interval
        self.retries_for_request = retries_for_request
        self.MISSING_DATES = 'missing_dates.txt'
        log_format = f'[%(asctime)s] [%(levelname)s] %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt='%Y-%m-%d %H:%M:%S')

    def run(self):
        logging.info('Crawler up')
        os.makedirs(self.storage_path, exist_ok=True)
        logging.info('Initialisation of the data population')
        self.download_or_maintain_data()
        logging.info('Initialisation completed')
        logging.info(f'Going to sleep for {self.update_interval} seconds due to normal stand-by mode')
        time.sleep(self.update_interval)
        logging.info('Crawler woke up from stand-by mode')
        while True:
            logging.info(f'Maintaining...')
            self.download_or_maintain_data(maintain=True)
            logging.info(f'Going to sleep for {self.update_interval} seconds due to normal stand-by mode')
            time.sleep(self.update_interval)
            logging.info('Crawler woke up from stand-by mode')

    def download_or_maintain_data(self, maintain=False):
        endpoint_epss = 'https://epss.cyentia.com/epss_scores-{}.csv.gz'
        delta = datetime.timedelta(days=1)
        if maintain:
            date_from = datetime.date.today() - delta
        else:
            local_date = self.retrieve_last_local_date()
            date_from = datetime.date(2021, 4, 14) if local_date is None else local_date.date()
            date_from += delta
        logging.info(f'Retrieving EPSS from {date_from}')
        date_to = datetime.date.today()
        actual_retries = 0
        while date_from < date_to:
            url = endpoint_epss.format(str(date_from))
            is_exception_or_too_many_request = False
            logging.info(f'Request for {date_from}')
            try:
                response = requests.get(url, timeout=self.request_timeout)
                if response.status_code == 200:
                    logging.info(f'Data obtained for {date_from}')
                    self.save_compressed_data(str(date_from), response.content)
                    logging.info(f'Data saved for {date_from}')
                    date_from += delta
                else:
                    logging.error(f'Request failed for {date_from}, status code={response.status_code}')
                    is_exception_or_too_many_request = True
                    actual_retries += 1
            except Exception as e:
                logging.exception(e)
                is_exception_or_too_many_request = True
                actual_retries += 1
            if actual_retries == self.retries_for_request:
                logging.error(f'Maximum number of retries reached for date={date_from}, this request is skipped')
                with open(os.path.join(self.storage_path, self.MISSING_DATES), 'a') as f:
                    f.write(str(date_from) + '\n')
                logging.info(f'Missing date={date_from} saved into {self.MISSING_DATES}')
                actual_retries = 0
                date_from += delta
            if is_exception_or_too_many_request:
                logging.warning(
                    f'Going to sleep for {self.retry_interval} seconds due to too many requests or an exception')
                time.sleep(self.retry_interval)
            else:
                logging.info(f'Going to sleep for {self.interval_between_requests} seconds before the next request')
                time.sleep(self.interval_between_requests)
            logging.info('Crawler woke up')

    def retrieve_last_local_date(self):
        highest_date = None
        for year in os.listdir(self.storage_path):
            year_path = os.path.join(self.storage_path, year)
            if os.path.isdir(year_path):
                for month in os.listdir(year_path):
                    month_path = os.path.join(year_path, month)
                    if os.path.isdir(month_path):
                        for file in os.listdir(month_path):
                            if file.endswith('.csv.gz'):
                                try:
                                    file_date = datetime.datetime.strptime(file[:-7], '%Y-%m-%d')
                                except ValueError:
                                    continue
                                if highest_date is None or file_date > highest_date:
                                    highest_date = file_date
        return highest_date

    def save_compressed_data(self, date_str, content):
        try:
            date = date_str.split('-')
            year = date[0]
            month = date[1]
            year_path = os.path.join(self.storage_path, year)
            os.makedirs(year_path, exist_ok=True)
            month_path = os.path.join(year_path, month)
            os.makedirs(month_path, exist_ok=True)
            with open(os.path.join(month_path, f'{date_str}.csv.gz'), 'wb') as file:
                file.write(content)
        except:
            raise RuntimeError('Cannot save data')


if __name__ == '__main__':
    EPSSCrawler().run()
