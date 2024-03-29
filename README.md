# Stage Manager

## Introduction
Stage Manager is an intermediary layer for controlling [Pivid](https://github.com/egnor/pivid/).  It is meant to be run on the same Raspberry Pi as Pivid.  Like Pivid, Stage Manager has no user interface, and is meant to be controlled by other software, over through a network API.  Pivid's API is low level and maximally powerful and flexible.  Stage Manager, on the other hand, provides a high level API, allowing an application to use simple messages to access and combine various user-defined presets, and to update the client application via callbacks.

Stage Manager is currently designed to streamline the use cases _I_ need in _my_ use case. It will probably only be suitable if _your_ use case has significant similarities to mine.

* [Running Stage Manager](doc/running.md)
* [Scripts & Configuration](doc/scripts.md)

## Basic Features
Stage Manager aims to streamline certain use cases:
* Seamlessly playing one video when another is done.
* Reporting when a video has started.
* Reporting when a time-based "marker" into a video has been passed.
* Independently controlling playback on different displays, different regions of the same display, or even overlapping regions of the same display.  Each region could even be controlled by a separate process!
* Video is controlled by network commands.
* Managing preloaded media based on hints for "next playback" candidates.  
* Seemlessly transitioning out of a looping video.

Here's some examples of applications that Stage Manager might be useful for:

* A visual Choose Your Own Adventure type game (e.g., [A Heist with Markiplier](https://www.youtube.com/watch?v=9TjfkXmwbTs))
* A video game with "quick time" events (e.g., [Dragon's Lair](https://en.wikipedia.org/wiki/Dragon%27s_Lair))
* A fictitious (and fairly simple) industrial control system for an Escape Room

## Further documentation

* [Running Stage Manager](doc/running.md)
* [Scripts](doc/scripts.md)

## Todo-list features

* Parameterized values (e.g., position)
