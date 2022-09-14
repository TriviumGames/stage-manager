from pythonosc import udp_client


class NetworkNotifier:
    def __init__(self, config):
        self.osc_server = config.get('osc', {}).get('server')
        if self.osc_server:
            parts = self.osc_server.split(':')
            if len(parts) != 2:
                raise ValueError(f"Incorrect osc_server parameter '{self.osc_server}'. Should be hostname:port.")
            self.osc_client = udp_client.SimpleUDPClient(parts[0], int(parts[1]))
            self.osc_scene_start_address = config.get('osc', {}).get('scene_change_address')
        else:
            self.osc_client = None


    def send_cue(self, osc_address, args):
        if self.osc_client:
            self.osc_client.send_message(osc_address, args)

    def send_scene_start(self, stage_id, scene_id):
        if self.osc_scene_start_address:
            self.send_cue(self.osc_scene_start_address, [stage_id, scene_id])