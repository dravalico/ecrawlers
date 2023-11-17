![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

# cve-crawler

This is a web crawler that downloads all existing [CVE from MITRE](https://cve.mitre.org/). It can be used both as a
normal Python program and via Docker.

## Parameters

When it starts downloading for the first time, it will start from the first existing CVEs, dating back to 1999. If its
execution is interrupted, at its next execution, if the output folder is the same, it will start again from the last
downloaded one. If all CVEs are downloaded completely, the script will download new data once every `update_interval`
seconds (default is 3600 seconds).

it is also possible to configure the `path_storage` path (default is `/usr/src/data`) in which to save the downloaded
files and the `retry_interval` time (default is 60 seconds), in case the request limit is reached.

## Usage

Running without Docker can be done as a regular Python program (conda or venv). Simply install the requirements via `pip
install requirements.txt`.

Running via [Docker](https://www.docker.com/), however, obviously requires its installation. The build must then be
performed via:

```
docker build --tag cve-crawler .
```

Subsequently, you can run the application via:

```
docker run -v <local output directory>:/usr/src/data cve-crawler
```

### Output folder

The files are saved in the specified folder and are organized by year, month and then a jsonl file per day. The date
refers to how much the CVE in question has been reserved.

It should be noted that for correct execution, a (hidden) file is created and used, called `last_cve.txt`, in which the
next CVE to be downloaded is saved. If this file is deleted, the download will start again from the beginning the next
time the software is run (only if not already running).