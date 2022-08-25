from dataclasses import dataclass
from datetime import datetime

@dataclass
class AutopilotEvent:
    time: float
    stage_id: str
    scene_id: str
    start_time: float

    def register(self, pivid_control):
        when = datetime.fromtimestamp(self.time)
        return pivid_control.scheduler.add_job(lambda: pivid_control.start_scene(self.stage_id, self.scene_id, self.start_time), 'date', run_date=when)
