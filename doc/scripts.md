# Stage Manager Scripting

Stage Manager scripts are loaded from json files in the `config_dir`.  See [configuration](config.md) for more details.

## Concepts

### `outputs`
These are physical outputs like HDMI-1, etc, and control the physical resolution and refresh rate, which must be supported by the display device. These settings are directly passed through to Pivid.
For details see the [Pivid documentation](https://github.com/egnor/pivid/blob/main/doc/script.md)

Outputs can be tagged with `"rotate": 180` and/or `"reflect": true` to affect everything played on that output. 

### `stages`
By analog with a theatrical stage, these define regions that `scenes` can be played out on.  They specify an `output`, and optionally a `rect` within that output device.  

A `scene` can never be played without a `stage` to play it on, and each `stage` can be controlled independently.  

`stages` do not have a direct Pivid equivalent.

Stages can be tagged with `"rotate": 180` and/or `"reflect": true` to affect everything played on that stage.  These will not override the output's settings, but will combine with them.  (i.e., of both the stage and the scene says reflect:true, that will end up doubly reflected, i.e. normal)

### `scenes`
A scene represents a some group of media that plays, with various playback parameters, timed markers (`cues`) for callbacks, and hints for which scenes to prebuffer.

#### `layers`
An array of layers, each with a `media` filename, and various position and time parameters. If no position parameters are specified, the layer will be expanded to fit the `stage`'s area (maintaining aspect ratio). 

If no time parameters are specified, the media will start at the beginning of the scene, and play at regular speed until it is over.  

A layer can be set to `repeat` in which case it will loop forever.  

#### `duration`

A scene's `duration` can be set explicitly. If it is not set, it will automatically be set to the duration of the longest piece of media with non-zero transparency.  For media marked `"repeat": true` this is infinite.  If the only layer is a static image, it will also be infinite.

Currently if any layers have non-default time parameters, the `duration` will be miscalculated, so this should be set explicitly.

#### `autopilot`

When this scene is done, `autopilot` specifies which other `scene` to immediately play on the same `stage`.  This ought to be frame-perfect.

#### `next_scenes`

`next_scenes` is an optional array of `scene` names, indicating which `scenes`' `media` should be preloaded. Use this to hint which `scenes` we may suddenly transition to, so that a smooth and instant transition is possible.  If an `autopilot` target is specificed, it will automatically be included to this list.

#### `cues`

`cues` is an optional array of timed markers, and network messages to be sent when said marker is reached.  If the `scene` changes before the timestamp is reached, then the message will not be sent. Similarly if the `scene` is entered after the timestamp, then that message will not be sent.

Each message has a time `t`, an OSC address `addr`, and an array of `args`, and will be sent to the configured host/port (see [network configuration](config.md))
