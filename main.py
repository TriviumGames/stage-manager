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
    pivid.start_scene('fullscreen', 'intro_star')
    pivid.comp.send_update()
    pivid.run_forever()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Sane ^C behavior.
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default='localhost:31415', help='Server address & port (default: localhost:31415)')
    parser.add_argument('--config_file', help='Config file to use', required=True)
    parser.add_argument('--osc_server', help='Hostname:port to send OSC messages to. Omit to disable OSC.')
    parser.add_argument('--osc_scene_start_address', help='OSC address for scene start')

    args = parser.parse_args()
    main(args)
