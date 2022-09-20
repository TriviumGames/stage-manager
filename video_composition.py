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

    def load_from_dict(self, dict):
        self.duration_cache.clear()
        self.source = copy.deepcopy(dict)
        assert 'outputs' in self.source
        assert 'stages' in self.source
        assert 'scenes' in self.source
        # precache media durations, so we're ready to go without a million queries
        self.source['scenes']['None'] = {}
        for scene_id, scene in self.source['scenes'].items():
            if 'layers' not in scene:
                scene['layers'] = []
            for layer in scene['layers']:
                layer_duration = self.get_layer_duration(layer)
                if 'play' not in layer :
                    layer['play'] = {
                        't': [0]
                    }
                    if layer_duration:
                        layer['play']['t'].append(layer_duration)
                        layer['play']['rate'] =  1

                if 't' not in layer['play']:
                    layer['play']['t'] = [0]
                    if layer_duration:
                        layer['play']['t'].append(layer_duration)
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

        for stage in self.source['stages']:
            stage['current_scene'] = 'None'
            stage['time_base'] = 0
            if 'rect' in stage:
                rect = stage['rect']
                stage['to_xy'] = rect[0:2]
                stage['to_size'] = [rect[2] - rect[0], rect[3] - rect[1]]
            output = self.source['outputs'][stage['output']]
            stage['reflect'] = (stage.get('reflect') or False) ^ (output.get('reflect') or False)
            stage['rotate'] = (stage.get('rotate') or 0) + (output.get('rotate') or 0)
            self.stages[stage['name']] = stage

        for outputid, output in self.source['outputs'].items():
            print(f"{output}")
            output.pop('rotate', None)
            output.pop('reflect', None)

    def get_layer_duration(self, layer) -> float:
        if 'opacity' in layer and layer['opacity'] == 0:
            return 0
        if 'repeat' in layer and layer['repeat']:
            return math.inf
        return self.get_media_duration(layer['media'])

    def get_scene_duration(self, scene_id) -> float:
        scene = self.source['scenes'][scene_id]
        if 'duration' in scene:
            return scene['duration']
        if not scene['layers']:
            return math.inf
        duration = 0
        for layer in scene['layers']:
            layer_duration = self.get_layer_duration(layer)
            if layer_duration:
                duration = max(duration, layer_duration)
        return duration

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
        if 'stage_direction' in scene:
            for sd in scene['stage_direction']:
                sd_time = vp['time_base'] + sd['t']
                events.append(scene_events.CueEvent(sd_time, sd['addr'], sd['args']))
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

    def adjust_layer(self, layer, start_time, stage):
        l = copy.deepcopy(layer)
        if 'to_size' not in l:
            l['to_size'] = stage['to_size']
        if 'to_xy' not in l:
            l['to_xy'] = stage['to_xy']
        l['play']['t'] = [t + start_time for t in l['play']['t']]
        reflect = (l.get('reflect') or False) ^ (stage.get('reflect') or False)
        rotate = (l.get('rotate') or 0) + (stage.get('rotate') or 0) % 360
        if reflect:
            l['reflect'] = True
        if rotate:
            l['rotate'] = rotate
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
        scenes = list()
        print("**************Sending update**************")
        for stage in self.source['stages']:
            print(f"Stage {stage['name']}: {stage['current_scene']}")
            screen = update['screens'][stage['output']]
            scene = self.source['scenes'][stage['current_scene']]
            preloads.update(scene['preloads'])
            scene_start = stage['time_base']
            for layer in scene['layers']:
                screen['layers'].append(self.adjust_layer(layer, scene_start, stage))
            next_scene_start = scene_start + self.get_scene_duration(stage['current_scene'])
            if 'autopilot' in scene and next_scene_start < math.inf:
                next_scene_id = scene['autopilot']
                next_scene = self.source['scenes'][next_scene_id]
                for layer in next_scene['layers']:
                    screen['layers'].append(self.adjust_layer(layer, next_scene_start, stage))
        for media in preloads:
            update['buffer_tuning'][media] = {'pin': 0.5}
        self.pivid_server.send_script(update)

