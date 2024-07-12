# Stage Manager Configuration

Stage Manager loads all of the `*.json` files from the `config_dir` specified on the command line. It does its best to merge all such files, but if a setting is defined differently in two different places, that will be treated as an error.

This means that any file can contain any setting and/or scene data.  It is useful (though not necessary) to separate things by meaning. Here's the conventions I use:

## `display.json` 
This defines 'outputs' and 'stages'.
Example
```{
	"outputs":
	{
		"HDMI-1": {
			"mode": [1920, 1080, 60],
			"update_hz": 30
		}
	},
	"stages":
	[
		{
			"name": "GameScene",
			"output": "HDMI-1",
			"rect": [0,0,1920,1080]
		},
		{
			"name": "ThoughtBubbleOverlay",
			"output": "HDMI-1",
			"rect": [1228,164, 1652, 495]
		}
	]
}
```

* `network.json`
This configures network settings
Example
```{
	"pivid":
	{
		"server": "localhost:31415"
	},
	"osc":{
		"server": "192.168.123.4:6789",
		"scene_change_address": "/Pivid/start"
	}
}```

