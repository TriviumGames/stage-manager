import asyncio
import math
import video_composition
import time
import pivid_server
from pythonosc.osc_server import AsyncIOOSCUDPServer
from pythonosc.dispatcher import Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import network_notifier
import glob
import json


class PividControl:
    def __init__(self, args):
        self.config = dict()

        for filename in glob.iglob(f'{args.config_dir}/*.json'):
            print(f"Loading config file {filename}")
            with open(filename, 'r') as f:
                self.config.update(json.load(f))

        self.pivid_config = self.config['pivid']
        self.osc_config = self.config['osc']

        if args.server == "mock":
            self.pivid_server = pivid_server.MockPividServer()
        else:
            self.pivid_server = pivid_server.PividServer(args.server)
        self.network_notifier = network_notifier.NetworkNotifier(args)
        self.comp = video_composition.VideoComposition(self.pivid_server)
        self.comp.load_json(self.config)
        self.osc_dispatcher = Dispatcher()
        self.osc_dispatcher.map('/Pivid/StartScene', self.osc_start_scene)
        self.osc_dispatcher.map('/Pivid/ChangeScene', self.osc_change_scene)
        self.comp.send_update()
        self.osc_server = None
        self.start_time = time.time()
        self.scheduler = AsyncIOScheduler()
        self.scene_jobs = dict() # map of stage_id to list of pending job

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
        self.register_scene_events(stage_id, events)
        self.comp.send_update()
        self.network_notifier.send_scene_start(stage_id, scene_id)

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

    def run_forever(self):
        asyncio.run(self.start())

