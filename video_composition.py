import json


class VideoComposition:
    def __init__(self, pivid_server):
        self.pivid_server = pivid_server
        self.duration_cache = dict()

    def get_media_duration(self, filename):
        if filename in self.duration_cache:
            return self.duration_cache[filename]
        else:
            duration = self.pivid_server.get_media_duration(filename)
            return duration

    def load_json(self, filename):
        with open(filename, 'r') as f:
            self.source = json.load(f)
        assert 'ouputs' in self.source
        assert 'viewports' in self.source
        assert 'scenes' in self.source
