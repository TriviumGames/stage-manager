import video_composition
import pivid_server
import urllib

class PividControl:
    def __init__(self, args):
        if 'http://' in args.server:
            base_url = args.server
        else:
            base_url = urllib.parse.urljoin("http://", args.server)
        self.pivid_server = pivid_server.PividServer(base_url)
        self.comp = video_composition.VideoComposition(self.pivid_server, args.config_file)


