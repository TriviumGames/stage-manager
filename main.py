#!/user/bin/env python3

import argparse
import time
import apscheduler

import pivid_control
import pivid_server
import signal
import video_composition


def main(args):
    pivid = pivid_control.PividControl(args)
    pivid.go()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Sane ^C behavior.
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_dir', help='Config dir to use', required=True)
    parser.add_argument('--mock_pivid', help='Boolean: mock up pivid for testing', action='store_true',)
    parser.add_argument('--export', help='Read config, export to a file [name follows], and exit')
    parser.add_argument('--update_cues', help='Update cue data from script/spreadsheet [dir follows], and exit')
    args = parser.parse_args()
    main(args)
