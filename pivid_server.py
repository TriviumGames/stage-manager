import urllib.parse
import requests


class PividServer:
    def __init__(self, url):
        self.url = url
        self.play_url = urllib.parse.urljoin(url, "/play")

    def get_media_duration(self, filename):
        media_url = urllib.parse.urljoin(self.url, '/media/' + filename)
        r = requests.get(media_url)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise ValueError(f"{media_url}: {r.json().get('error', 'Not OK')}")
        duration = r.json().get("media").get("duration")
        return duration

    def send_script(self, script):
        r = requests.post(self.play_url, json=script)
        r.raise_for_status()
        if not r.json().get("ok"):
            raise ValueError(f"{self.play_url}: {r.json().get('error', 'Not OK')}")
