#!/bin/bash

set -e 

cd ~/trivium/stage-manager
if [ ! -f venv ]; then
	python3 -m venv venv
fi

source venv/bin/activate

pip install -r requirements.txt > /dev/null

echo Starting stage manager
python3 -u main.py $*
