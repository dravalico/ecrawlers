import logging
import os
import datetime
import requests
import time


class EPSSCrawler:
    ENDPOINT_EPSS = 'https://epss.cyentia.com/epss_scores-{}.csv.gz'

    def __init__(self,
                 path_storage='/Users/dravalico/PycharmProjects/crawlers/epss-crawler/test',
                 request_timeout=10,
                 interval_between_requests=5,
                 update_interval=86400,
                 retry_interval=300,
                 retries_for_request=9):
        self.path_storage = path_storage
        self.request_timeout = request_timeout
        self.interval_between_requests = interval_between_requests
        self.update_interval = update_interval
        self.retry_interval = retry_interval
        self.retries_for_request = retries_for_request
        log_format = f'[%(asctime)s] [%(levelname)s] %(message)s'
        logging.basicConfig(level=logging.INFO, format=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    def run(self):
        logging.info("Crawler up")
        if not os.path.exists(self.path_storage):
            os.makedirs(self.path_storage)
        logging.info('Initialisation of the data population')
        self.download_or_maintain_data()
        logging.info('Initialisation completed')
        logging.info(f'Going to sleep for {self.update_interval} seconds due to normal stand-by mode')
        time.sleep(self.update_interval)
        logging.info('Crawler woke up from stand-by mode')
        while True:
            logging.info(f'Starting the cycle...')
            self.download_or_maintain_data(maintain=True)
            logging.info(f'Going to sleep for {self.update_interval} seconds due to normal stand-by mode')
            time.sleep(self.update_interval)
            logging.info('Crawler woke up from stand-by mode')

    def download_or_maintain_data(self, maintain=False):
        delta = datetime.timedelta(days=1)
        if maintain:
            date_from = datetime.date.today() - delta
        else:
            local_date = self.retrieve_last_local_date()
            date_from = datetime.date(2021, 4, 14) if local_date is None else local_date
        date_to = datetime.date.today()
        actual_retries = 0
        while date_from < date_to:
            url = self.ENDPOINT_EPSS.format(str(date_from))
            logging.info(f'Request for {date_from}')
            try:
                response = requests.get(url, timeout=self.request_timeout)
                if response.status_code == 200:
                    logging.info(f'Data obtained for {date_from}')
                    self.save_compressed_data(response.content)
                    logging.info(f'Data saved for {date_from}')
                    date_from += delta
                else:
                    logging.error(f'Cannot obtain data for {date_from}, status code={response.status_code}')
                    if response.status_code == 429 or response.status_code == 503:
                        logging.info(f'Going to sleep for {self.retry_interval} seconds due to too many requests')
                        time.sleep(self.retry_interval)
                    actual_retries += 1
                    if actual_retries == self.retries_for_request:
                        actual_retries = 0
                        date_from += delta
            except Exception as e:
                logging.exception(e)
                date_from += delta
            logging.info(f'Going to sleep for {self.interval_between_requests} seconds before the next request')
            time.sleep(self.interval_between_requests)
            logging.info('Crawler woke up')

    def retrieve_last_local_date(self):
        return None

    def save_compressed_data(self, date, content):
        pass
