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
    pivid.comp.send_update()
    pivid.run_forever()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Sane ^C behavior.
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_dir', help='Config dir to use', required=True)
    parser.add_argument('--mock_pivid', help='Config dir to use', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    main(args)
