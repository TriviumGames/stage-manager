import asyncio
import math
from datetime import datetime

import video_composition
import time
import pivid_server
import ct_spreadsheet_access
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import network_notifier
import glob
import json

from cue_file_output import CueScript


class PividControl:
    def __init__(self, args):
        self.config = dict()
        spreadsheet = ct_spreadsheet_access.CTSpreadsheetAccess()

        for filename in glob.iglob(f"{args.config_dir}/*.json"):
            print(f"Loading config json {filename}")
            with open(filename, 'r') as f:
                self.config = PividControl.merge_dicts(self.config, json.load(f))
        for filename in glob.iglob(f"{args.config_dir}/*.xlsx"):
            print(f"Loading config spreadsheet {filename}\n")
            self.config = PividControl.merge_dicts(self.config, spreadsheet.load(filename))

        self.pivid_config = self.config['pivid']
        self.osc_config = self.config['osc']

        if args.export:
            self.go = self.export
            self.export_filename = args.export
        elif args.update_cues:
            self.go = self.update_cues
            self.cues_dir = args.update_cues
            pass
        else:
            self.go = self.run_forever
            if args.mock_pivid:
                print("Mocking pivid. Neener neener")
                self.pivid_server = pivid_server.MockPividServer()
            else:
                self.pivid_server = pivid_server.PividServer(self.pivid_config['server'])
            self.network_notifier = network_notifier.NetworkNotifier(self.config)
            self.comp = video_composition.VideoComposition(self.pivid_server)
            self.comp.load_from_dict(self.config)
            self.osc_dispatcher = Dispatcher()
            self.osc_dispatcher.map('/Pivid/StartScene', self.osc_start_scene)
            self.osc_dispatcher.map('/Pivid/ChangeScene', self.osc_change_scene)
            self.comp.send_update()
            self.osc_server = None
            self.start_time = time.time()
            self.scheduler = AsyncIOScheduler()
            self.scene_jobs = dict() # map of stage_id to list of pending job

    def merge_dicts( a: dict, b: dict, path=None):
        "merges b into a"
        if path is None: path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    PividControl.merge_dicts(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    raise Exception(f"Conflict at {'.'.join(path + [str(key)])}")
            else:
                a[key] = b[key]
        return a

    def register_scene_events(self, stage_id, events):
        if stage_id in self.scene_jobs:
            for job in self.scene_jobs[stage_id]:
                if self.scheduler.get_job(job.id) is not None:
                    job.remove()
            self.scene_jobs[stage_id].clear()
        else:
            self.scene_jobs[stage_id] = []

        for evt in events:
            self.scene_jobs[stage_id].append(evt.register(self))

    def osc_start_scene(self, address, *args):
        print(f"{time.time() - self.start_time} {address}:  {args}")
        self.start_scene(args[0], args[1])

    def start_scene(self, stage_id, scene_id, start_time = None):
        events = self.comp.start_scene(stage_id, scene_id, start_time)
        self.network_notifier.send_scene_start(stage_id, scene_id)
        self.register_scene_events(stage_id, events)
        self.comp.send_update()

    def osc_change_scene(self, address, *args):
        print(f"{time.time() - self.start_time} {address}:  {args}")
        self.change_scene(args[0], args[1])

    def change_scene(self, stage_id, scene_id):
        events = self.comp.change_scene(stage_id, scene_id)
        self.register_scene_events(stage_id, events)
        self.comp.send_update()

    def tick(self):
        self.comp.start_scene('fullscreen', 'intro_star')
        self.comp.send_update()

    async def start(self):
        self.osc_server = AsyncIOOSCUDPServer(("0.0.0.0", 1337), self.osc_dispatcher, asyncio.get_event_loop())
        #self.scheduler.add_job(self.tick, 'interval', seconds=10)
        self.scheduler.start()
        transport, protocol = await self.osc_server.create_serve_endpoint()
        await asyncio.sleep(math.inf)

    def export(self):
        print(f"Exporting to {self.export_filename}\n")
        spreadsheet = ct_spreadsheet_access.CTSpreadsheetAccess()
        spreadsheet.save(self.config, self.export_filename)

    def update_cues(self):
        updateTime = datetime.now()
        for name, scene in self.config['scenes'].items():
            filename = f"{self.cues_dir}/{name}.txt"
            cue = CueScript(filename, updateTime)
            if 'stage_direction' in scene:
                cue.clear_generated_lines()
                cue.merge_with_stage_direction(scene['stage_direction'])
            cue.save()

    def run_forever(self):
        self.comp.send_update()
        asyncio.run(self.start())

