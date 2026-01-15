import datetime
import os
import pprint


class CueScript:
    filename: str
    relativeFilename: str
    lines: list
    update_time: datetime

    def __init__(self, filename, update_time):
        self.filename = filename
        self.update_time = update_time
        try:
            with open(self.filename, 'r') as f:
                self.lines = f.readlines()
            self.lines = [line.rstrip('\n') for line in self.lines]
        except FileNotFoundError:
            self.lines = []

    def clear_generated_lines(self):
        idx = 0
        while idx < len(self.lines):
            if len(self.lines[idx]) and self.lines[idx][0].isspace():
                self.lines.pop(idx)
            else:
                idx = idx + 1

    def merge_with_stage_direction(self, stage_direction_input: list):
        stage_direction = []
        try:
            stage_direction = sorted(stage_direction_input, key = lambda x: x['t'])
        except:
            pprint.pprint(stage_direction_input)
            raise
        total_delay = 0
        cur_time = 0
        next_time = cur_time
        my_idx = 0
        stage_idx = 0

        while stage_idx < len(stage_direction):
            next_stage_time = int(stage_direction[stage_idx]['t'] * 1000)

            while next_stage_time > next_time and my_idx < len(self.lines):
                line_bits = self.lines[my_idx].split()
                if len(line_bits) > 0 and line_bits[0] == 'Time':
                    val = float(line_bits[1])
                    if line_bits[1].startswith('+'):
                        next_time = next_time + val
                    else:
                        next_time = val + total_delay
                    if next_time <= next_stage_time:
                        cur_time = next_time
                        my_idx = my_idx + 1
                elif len(line_bits) > 0 and line_bits[0] == 'Delay':
                    val = float(line_bits[1])
                    total_delay = total_delay + val
                    next_time = next_time + val
                    if next_time <= next_stage_time:
                        cur_time = next_time
                        my_idx = my_idx + 1
                else:
                    my_idx = my_idx + 1

            if next_stage_time != cur_time:
                self.lines.insert(my_idx, f"\tTime {next_stage_time}")
                my_idx = my_idx + 1
                cur_time = next_stage_time
            self.lines.insert(my_idx, f"\t{stage_direction[stage_idx]['addr']} {' '.join(map(str, stage_direction[stage_idx]['args']))}")
            my_idx = my_idx + 1
            stage_idx = stage_idx + 1
        self.lines.insert(0, f"\tTRACE\tStarting scene: {os.path.basename(self.filename)} (updated at {self.update_time})")

    def save(self):
        with open(self.filename, 'w') as f:
            for line in self.lines:
                f.write(line + '\n')

