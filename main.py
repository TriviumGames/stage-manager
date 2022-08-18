#!/user/bin/env python3

import argparse
import time
import apscheduler
import pivid_server
import signal
import video_composition


def main(args):
    server = pivid_server.PividServer(args.server)
    comp = video_composition.VideoComposition(server)
    comp.load_json(args.config_file)
    comp.start_scene('fullscreen', 'cit_005')
    comp.send_update()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Sane ^C behavior.
    parser = argparse.ArgumentParser()
    parser.add_argument('--server', default='localhost:31415', help='Server address & port (default: localhost:31415)')
    parser.add_argument('--config_file', help='Config file to use', required=True)
    args = parser.parse_args()
    main(args)
