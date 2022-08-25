import json
import math
import time
import copy
import scene_events

class VideoComposition:
    def __init__(self, pivid_server):
        self.pivid_server = pivid_server
        self.duration_cache = dict()
        self.stages = dict()

    def get_media_duration(self, filename) -> float:
        if filename in self.duration_cache:
            return self.duration_cache[filename]
        else:
            duration = self.pivid_server.get_media_duration(filename)
            self.duration_cache[filename] = duration
            return duration

    def load_json(self, filename) -> dict:
        self.duration_cache.clear()
        with open(filename, 'r') as f:
            self.source = json.load(f)
        assert 'outputs' in self.source
        assert 'stages' in self.source
        assert 'scenes' in self.source
        # precache media durations, so we're ready to go without a million queries
        self.source['scenes']['None'] = {}
        for scene_id, scene in self.source['scenes'].items():
            if 'layers' not in scene:
                scene['layers'] = []
            for layer in scene['layers']:
                if 'play' not in layer :
                    layer['play'] = {
                        't': [0, self.get_media_duration(layer['media'])],
                        'rate': 1
                    }
                if 't' not in layer['play']:
                    layer['play']['t'] = [0, self.get_media_duration(layer['media'])]
            if 'next_scenes' not in scene:
                scene['next_scenes'] = []
        for scene_id, scene in self.source['scenes'].items():
            scene['preloads'] = set()
            self.get_scene_duration(scene_id)
            for next_scene in scene['next_scenes']:
                for layer in self.source['scenes'][next_scene]['layers']:
                    scene['preloads'].add(layer['media'])
            if 'autopilot' in scene:
                for layer in self.source['scenes'][scene['autopilot']]['layers']:
                    scene['preloads'].add(layer['media'])

        for vp in self.source['stages']:
            vp['current_scene'] = 'None'
            vp['time_base'] = 0
            self.stages[vp['name']] = vp

    def get_layer_duration(self, layer) -> float:
        if 'opacity' in layer and layer['opacity'] is 0:
            return 0
        if 'repeat' in layer and layer['repeat']:
            return math.inf
        return self.get_media_duration(layer['media'])

    def get_scene_duration(self, scene_id) -> float:
        scene = self.source['scenes'][scene_id]
        if not scene['layers']:
            return math.inf
        return max(map(lambda l: self.get_layer_duration(l), scene['layers']))

    def start_scene(self, stage_id, scene_id, start_time = None):
        if start_time is None:
            start_time = time.time()
        vp = self.stages[stage_id]
        vp['current_scene'] = scene_id
        vp['time_base'] = start_time
        scene = self.source['scenes'][scene_id]
        events = []
        if self.get_scene_duration(scene_id) < math.inf and 'autopilot' in scene:
            next_autopilot_time = vp['time_base'] + self.get_scene_duration(scene_id)
            events.append(scene_events.AutopilotEvent(next_autopilot_time, stage_id, scene['autopilot'], next_autopilot_time))
        return events

    def change_scene(self, stage_id, scene_id):
        vp = self.stages[stage_id]
        vp['current_scene'] = scene_id
        scene = self.source['scenes'][scene_id]
        events = []
        if self.get_scene_duration(scene_id) < math.inf and 'autopilot' in scene:
            next_autopilot_time = vp['time_base'] + self.get_scene_duration(scene_id)
            events.append(scene_events.AutopilotEvent(next_autopilot_time, stage_id, scene['autopilot'], next_autopilot_time))
        return events

    def time_shift_layer(self, layer, start_time):
        l = copy.deepcopy(layer)
        l['play']['t'] = [t + start_time for t in l['play']['t']]
        return l

    def send_update(self):
        update = \
            {
                'screens': copy.deepcopy(self.source['outputs']),
                'zero_time': 0,
                'buffer_tuning': {}
            }
        for id, screen in update['screens'].items():
            screen['layers'] = list()
        preloads = set()
        for vp in self.source['stages']:
            screen = update['screens'][vp['output']]
            scene = self.source['scenes'][vp['current_scene']]
            preloads.update(scene['preloads'])
            scene_start = vp['time_base']
            for layer in scene['layers']:
                screen['layers'].append(self.time_shift_layer(layer, scene_start))
            next_scene_start = scene_start + self.get_scene_duration(vp['current_scene'])
            if 'autopilot' in scene and next_scene_start < math.inf:
                next_scene_id = scene['autopilot']
                next_scene = self.source['scenes'][next_scene_id]
                for layer in next_scene['layers']:
                    screen['layers'].append(self.time_shift_layer(layer, next_scene_start))
        for media in preloads:
            update['buffer_tuning'][media] = {'pin': 1}
        self.pivid_server.send_script(update)

