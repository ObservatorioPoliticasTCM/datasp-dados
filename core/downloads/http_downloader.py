import requests
from io import BytesIO
from logging import info

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'pt-BR,pt;q=0.9',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Mobile Safari/537.36 Edg/142.0.0.0',
    'sec-ch-ua': '"Chromium";v="142", "Microsoft Edge";v="142", "Not_A Brand";v="99"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"'
}

class HttpDownloader:
    def __init__(self,
                 headers: dict | None = None,
                 request_timeout: int | None = None,
                 retries: int | None = None):
        self.headers = headers if headers is not None else DEFAULT_HEADERS
        self.request_timeout = request_timeout if request_timeout is not None else 60
        self.retries = retries if retries is not None else 3

    def download(self, url: str) -> BytesIO:
        if not url:
            raise ValueError(f"No URL defined for download.")

        for attempt in range(self.retries):
            try:
                info(f'Downloading data from {url} (Attempt {attempt + 1}/{self.retries})')
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout)
                response.raise_for_status()
                return BytesIO(response.content)
            except requests.exceptions.RequestException as e:
                info(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.retries - 1:
                    raise Exception(f"Failed to download data from {url} after {self.retries} attempts.") from e
