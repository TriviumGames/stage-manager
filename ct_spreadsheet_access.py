from collections import OrderedDict

import pyexcel_xlsx

class CTSpreadsheetAccess:
    column_names: OrderedDict

    @staticmethod
    def add_action_default(d: dict, action: str):
        d[action + '_verb'] = None
        d[action + '_scene'] = None

    def __init__(self):
        self.input_names = ['Brake', 'Gas', 'Horn', 'Left', 'Right', 'Lever',
                            'ChainCircle', 'ChainTriangle', 'ChainSquare',
                            'Rope', 'Plunger']
        self.column_names = OrderedDict()
        self.column_names['name'] = None
        self.column_names['main_vid'] = None
        self.column_names['vid_loop'] = None
        self.column_names['invis_vid'] = None
        self.column_names['autopilot'] = None
        self.column_names['checkpoint'] = None
        self.column_names['extra_nexts'] = None
        self.column_names['timed_fail_time'] = None
        self.column_names['timed_fail_scene'] = None
        self.column_names['input_start'] = None
        self.column_names['input_stop'] = None
        for i in self.input_names:
            self.add_action_default(self.column_names, i)
        self.column_names['timer_time'] = None
        self.column_names['timer_verb'] = None
        self.column_names['timer_scene'] = None
        self.column_names['timer_len'] = None
        self.column_names['dir_event_time'] = None
        self.column_names['dir_event'] = None
        self.column_names['audio_event_time'] = None
        self.column_names['audio_event'] = None
        self.column_names['alert_on'] = None
        self.column_names['alert_off'] = None
        self.column_names['scene_length'] = None
        self.column_names['audio_offset'] = None
        self.column_names['music_directive'] = None
        self.column_names['note'] = None


        print(f"Fields: {self.column_names.keys()}\n")
        pass

    @staticmethod
    def export_action(row: dict, input: str, verb: str, scene: str):
        row[input + '_verb'] = verb
        row[input + '_scene'] = scene

    def fix_name(self, name: str):
        if name.startswith('$') or name.startswith('!'):
            return name[1:] + name[0]
        else:
            return name

    def save(self, config: dict, filename: str):
        scenes = list()
        scenes.append(list(self.column_names.keys()))
        for name, scene in config['scenes'].items():
            next_scenes = set()
            print(f"Processing scene {name}\n")
            row = OrderedDict(self.column_names)
            row['name'] = self.fix_name(name)
            if 'layers' in scene:
                if len(scene['layers']) > 2:
                    print(f"Too many layers detected. Cannot fully capture scene <{name}>\n")
                    row['notes'] += "Too many layers detected"
                elif len(scene['layers']) == 2:
                    row['main_vid'] = scene['layers'][1]['media']
                    row['invis_vid'] = scene['layers'][0]['media']
                elif len(scene['layers']) == 1:
                    row['main_vid'] = scene['layers'][0]['media']
                for layer in scene['layers']:
                    if 'play' in layer and 'repeat' in layer['play']:
                        row['vid_loop'] = layer['play']['repeat']
            if 'autopilot' in scene:
                row['autopilot'] = scene['autopilot']
                next_scenes.add(self.fix_name(scene['autopilot']))
            if 'stage_direction' in scene:
                for directive in scene['stage_direction']:
                    if directive['addr'] == '/TestDrive/Inputs':
                        if directive['args'][0] == 'None':
                            row['input_stop'] = directive['t']
                        else:
                            row['input_start'] = directive['t']
                            for i in range(0, len(directive['args']), 3):
                                self.export_action(row, directive['args'][i], directive['args'][i + 1], self.fix_name(directive['args'][i + 2]))
                                next_scenes.add(self.fix_name(directive['args'][i+2]))
                    elif directive['addr'] == '/TestDrive/Audio':
                        row['audio_event_time'] = directive['t']
                        row['audio_event'] = ' '.join(map(str, directive['args']))
                    elif directive['addr'] == '/TestDrive/Messages':
                        if directive['args'][0] == 'Start':
                            row['timed_fail_time'] = directive['t']
                            row['timed_fail_scene'] = self.fix_name(directive['args'][1])
                            next_scenes.add(self.fix_name(directive['args'][1]))
                        elif directive['args'][0] == 'Alert':
                            if directive['args'][1] == 'on':
                                row['alert_on'] = directive['t']
                            elif directive['args'][1] == 'off':
                                row['alert_off'] = directive['t']
                            else:
                                row['note'] = row['note'] + 'weird alert. '
                        elif directive['args'][0] == 'RopesTimer':
                            row['timer_verb'] = directive['args'][1]
                            row['timer_time'] = directive['t']
                            if directive['args'][1] == 'Start':
                                row['timer_scene'] = self.fix_name(directive['args'][2])
                                next_scenes.add(self.fix_name(directive['args'][2]))
                                row['timer_len'] = directive['args'][3]
                            elif directive['args'][1] == 'Stop':
                                pass
                            elif directive['args'][1] == 'Redirect':
                                row['timer_scene'] = self.fix_name(directive['args'][2])
                                next_scenes.add(self.fix_name(directive['args'][2]))
                            else:
                                row['note'] = row['note'] + 'weird RopesTimer. '
            if 'next_scenes' in scene:
                export_next_scenes = list()
                for s in scene['next_scenes']:
                    s = self.fix_name(s)
                    if s not in next_scenes:
                        export_next_scenes.append(s)
                    if len(export_next_scenes):
                        row['extra_nexts'] = ' '.join(export_next_scenes)
            scenes.append(list(row.values()))

        data = OrderedDict()
        data.update({"Scenes": scenes})
        pyexcel_xlsx.save_data(filename, data)

    def load(self, filename: str):
        spreadsheet = pyexcel_xlsx.get_data(filename)
        scenes = spreadsheet["Scenes"]
        headers = scenes[0]
        config = {'scenes':{}}
        print(f"Columns: {headers}\n")
        for raw_row in scenes[1:]:
            if len(raw_row):
                row = {}
                next_scenes = set()
                for i in range(0, len(raw_row)):
                    row[headers[i]] = raw_row[i]
                for i in range(len(raw_row), len(headers)):
                    row[headers[i]] = None
                if not row['name']:
                    continue
                scene = {'layers': [], 'stage_direction': [], 'next_scenes': []}
                if row['invis_vid']:
                    scene['layers'].append( {'media': row['invis_vid']})
                if row['main_vid']:
                    layer = {'media': row['main_vid']}
                    if row['vid_loop'] == True:
                        layer['play'] = {'repeat': True, 'v':0, 'rate': 1}
                    scene['layers'].append(layer)
                if row['autopilot']:
                    scene['autopilot'] = row['autopilot']
                if row['checkpoint']:
                    scene['stage_direction'].append({'t': 0, 'addr': '/Feature/Messages', 'args': ['Checkpoint', row['checkpoint']]})
                if row['extra_nexts']:
                    next_scenes.update(row['extra_nexts'].split(', '))
                if row['timed_fail_scene']:
                    scene['stage_direction'].append({'t': row['timed_fail_time'], 'addr': '/Feature/Messages', 'args': ["Start", row['timed_fail_scene']]})
                    next_scenes.add(row['timed_fail_scene'])
                if row['input_start'] is not None and row['input_start'] != '':
                    input_args = []
                    for input in self.input_names:
                        if row[input + '_verb']:
                            input_args.extend([input, row[input + '_verb'], row[input + '_scene']])
                            next_scenes.add(row[input + '_scene'])
                    scene['stage_direction'].append({'t': row['input_start'], 'addr': '/Feature/Inputs', 'args': input_args})
                if row['input_stop'] is not None and row['input_stop'] != '':
                    scene['stage_direction'].append({'t': row['input_stop'], 'addr': '/Feature/Inputs', 'args': ['Clear']})
                if row['timer_verb']:
                    if row['timer_verb'] == 'Start':
                        scene['stage_direction'].append(
                            {'t': row['timer_time'], 'addr': '/Feature/Messages', 'args': ['RopesTimer', row['timer_verb'], row['timer_scene'], row['timer_len']]})
                        next_scenes.add(row['timer_scene'])
                    elif row['timer_verb'] == 'Redirect':
                        scene['stage_direction'].append(
                            {'t': row['timer_time'], 'addr': '/Feature/Messages', 'args': ['RopesTimer', row['timer_verb'], row['timer_scene']]})
                        next_scenes.add(row['timer_scene'])
                    if row['timer_verb'] == 'Stop':
                        scene['stage_direction'].append(
                            {'t': row['timer_time'], 'addr': '/Feature/Messages', 'args': ['RopesTimer', row['timer_verb']]})
                if row['audio_event']:
                    scene['stage_direction'].append({'t': row['audio_event_time'], 'addr': 'Audio', 'args': row['audio_event'].split()})
                if row['music_directive']:
                    if row['music_directive'].startswith('Play'):
                        scene['stage_direction'].append({'t': 0, 'addr': 'Music', 'args': row['music_directive'].split() + [int(row['audio_offset'] * 1000)] })
                    else:
                        scene['stage_direction'].append({'t': 0, 'addr': 'Music', 'args': row['music_directive'].split() })
                if len(next_scenes):
                    scene['next_scenes'] = list(next_scenes)
                config['scenes'][row['name']] = scene
                print(f"Adding scene {row['name']}")
        return config