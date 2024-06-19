#!/usr/bin/python3

import argparse
import os
import re
import signal
import subprocess

def main(args):
    source_dir = args.source_dir
    target_dir = args.target_dir
    source_files = []
    target_files = []
    to_delete = []
    to_transcode = []
    file_filter = re.compile('[^.].*\.(mov|mp4|mkv)$', re.IGNORECASE)
    os.makedirs(target_dir, exist_ok=True)

    for root, dirs, files in os.walk(source_dir):
        for name in files:
            if file_filter.match(name):
                fqn = os.path.join(root, name)
                source_files.append(fqn.removeprefix(source_dir).removeprefix("/"))

    for root, dirs, files in os.walk(target_dir):
        for name in files:
            fqn = os.path.join(root, name)
            if file_filter.match(name):
                source_files.append(fqn.removeprefix(target_dir).removeprefix("/"))

    for f in target_files:
        if f not in source_files:
            to_delete.append(f)

    for f in source_files:
        target_file = os.path.join(target_dir, f)
        source_file = os.path.join(source_dir, f)
        if not os.path.exists(target_file) or os.path.getmtime(target_file) < os.path.getmtime(source_file):
            to_transcode.append((source_file, target_file))

    for it in to_transcode:
        os.makedirs(os.path.dirname(it[1]), exist_ok=True)
        command_line = ['ffmpeg', '-y', '-hide_banner', '-i', it[0], '-c:v', 'libx265', '-vtag', 'hvc1', it[1]]
        subprocess.check_call(command_line)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)  # Sane ^C behavior.
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dir', help='Directory to scan for input files', default=os.environ.get("sm_import_source"))
    parser.add_argument('--target_dir', help='Diretory to output files to', default=os.environ.get("sm_import_target"))

    args = parser.parse_args()
    main(args)

