import urllib.parse
import requests
import time
import pprint

class MockPividServer:

    def get_media_duration(self, filename):
        return 5.

    def send_script(self, script):
        pp = pprint.PrettyPrinter()
        pp.pprint(script)


class PividServer:
    def __init__(self, url):
        if ':' not in url:
            url = f"http://{url}:31415"
        if 'http' not in url:
            url = urllib.parse.urljoin('http://', url)
        self.url = url
        self.play_url = urllib.parse.urljoin(url, "/play")

    def get_media_duration(self, filename):
        now = time.time()
        media_url = urllib.parse.urljoin(self.url, '/media/' + filename)
        r = requests.get(media_url)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise ValueError(f"{media_url}: {r.json().get('error', 'Not OK')}")
        duration = r.json().get("media").get("duration")
        print(f"Media duration took {time.time() - now}s\n")
        return duration

    def send_script(self, script):
        pp = pprint.PrettyPrinter()
        pp.pprint(script)
        now = time.time()
        print(f"starting update {now}\n")
        r = requests.post(self.play_url, json=script)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise ValueError(f"{self.play_url}: {r.json().get('error', 'Not OK')}")
        print(f"update done, took {time.time() - now}s\n")