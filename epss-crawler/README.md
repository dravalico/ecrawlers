![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

# epss-crawler

This is a web crawler that downloads all existing [EPSS from FIRST](https://www.first.org/). It can be used both as a
normal Python program and via Docker, whose container can be obtained
from [here](https://hub.docker.com/r/dravalico/epss-cralwer).

## Parameters

When it starts downloading for the first time, it will start from the first existing EPSS, dating back to 14/04_2021. If
its execution is interrupted, at its next execution, if the output folder is the same, it will start again from the last
downloaded one. If all EPSSs are downloaded completely, the script will download new data once every `update_interval`
seconds (default is 86400 seconds).

it is also possible to configure the `path_storage` path (default is `/usr/src/data`) in which to save the downloaded
files, the timeout `request_timeout` for a single request (default is 2 seconds), the `retry_interval` time (default
is 300 seconds), in case the rate limit is reached and the `retries_for_request` (default is 9 but is from 0 to 9), for
the request that raises some errors but maybe can be obtained.

## Usage

Running without Docker can be done as a regular Python program (conda or venv). Simply install the requirements via `pip
install requirements.txt`.

Running via [Docker](https://www.docker.com/), however, obviously requires its installation. The build must then be
performed via:

```
docker build --tag <tag> .
```

Subsequently, you can run the application via:

```
docker run --restart unless-stopped -v <local output directory>:/usr/src/data <tag>
```

### Output folder

The data is saved in the specified folder and is organized in a tree, starting with the year and then the month. The
data from each EPSS is then saved in a `.csv.gz` file.