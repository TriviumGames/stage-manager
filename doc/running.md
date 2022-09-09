# Running Stage Manager

## Prerequesites

Stage Manager requires python3.  Probably use the latest version.  It also requires several packages. Each can be installed with the Pacakge Installer for Python (pip)
```
$ pip3 install <package name>
```

The following packages are needed. Install them using pip3 (see above)

* `[python-osc](https://python-osc.readthedocs.io/en/latest/)`, an OSC communication library
* `[apscheduler](https://apscheduler.readthedocs.io/en/3.x/index.html)`, a task scheduling library

## Running

The main program is called `main.py`. From the stage-manager directory, run

```
$ python3 main.py
```

Notable arguments:
* `--config_file=«script file»` - Required.  A json [script](scripts.md) to run
* `--server=«server»` - the address and optionally port of the pivid server. Default `http://localhost:31415`
* `--osc_server=address:port` - Required for callbacks. The IP or hostname and port of the OSC server
* `--osc_scene_start_address=«OSC address»` Required for automatic scene change callbacks. The OSC address that said callbacks are sent to. The payload is a string containing the name of the new scene.

Note that upon startup, Stage Manager reads the script file, and then caches media metadata from Pivid, which has the following implications
* Pivid must be running before Stage Manager is started.  However, it is okay to exit and re-start Pivid once Stage Manager is running
* If the script file is changed, Stage Manager must be restarted for those changes to take effect.
* If the lenghts of the media files have changed, Stage Manager must be restarted to recognize those changes.
