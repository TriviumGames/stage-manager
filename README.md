# pivid-control
Layer for controlling pivid.

## General architecture
Objects

* `outputs`
  * These are like HDMI-1, etc, and control the physical resolution and refresh rate.
* `viewports`
  * These define areas that `scenes` can be played on.  For now they are just associated with a output.
* `scenes`
  * Each scene is multiple `layers`, along with some hints for what other scenes might be coming up next (and should thus be pre-loaded).  Scenes have a duration, and an `autopilot` setting, which defines what to play after the scene finishes
* `layers`
  * A layer is a piece of media, possibly with playback parameters, position and scaling info, opacity, and so on.

## Todo

* Command line argument parsing
* Play a single scene
* OSC / MQTT control interface
  * Play a scene on a viewport
  * Play a scene on a viewport without changing time
  * Produce warning if non-preloaded scene
  * OSC / MQTT callback interface
* Autopilot between scenes
  
## Deferred features

* `viewports` as a subset of a screen
* Fancy control over position
* Monitor config file for changes