from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class SceneEventBase:
    time: float

    def register(self, pivid_control):
        when = datetime.fromtimestamp(self.time)
        return pivid_control.scheduler.add_job(lambda: self.do_action(pivid_control), 'date', run_date=when)

    def do_action(self, pivid_control):
        pass

@dataclass
class AutopilotEvent (SceneEventBase):
    stage_id: str
    scene_id: str
    start_time: float

    def do_action(self, pivid_control):
        pivid_control.start_scene(self.stage_id, self.scene_id, self.start_time)

@dataclass
class CueEvent (SceneEventBase):
    address: str
    args: List

    def do_action(self, pivid_control):
        pivid_control.network_notifier.send_cue(self.address, self.args)

