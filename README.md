# Macro-Now
Macro Now is a Window's desktop application that records macros in real time.

![](https://i.imgur.com/zCgFmLX.png)
![](https://i.imgur.com/ykLozzY.png)

Macro Now's GUI is written using [PyQt5](https://pypi.org/project/PyQt5/), 
and the recording of macros
is handled by [pynput](https://github.com/moses-palmer/pynput). The playback
of macros is mostly handled raw using `ctypes`. This is so we can use scan codes
rather than the virtual keycodes that pynput uses. Although, arrow keys are
still played back by pynput for reasons that don't really matter for most
people.

**Warning:** This application is far from finished. The base functionality of
recording and playing back macros, serializing the macros to write to disc,
and reading the macros back from disc is there. However, more thorough
testing needs to be done and many of the intended functionalities have yet
to been added (like actually deleting a macro). I wouldn't even say it's
ready for an alpha release.

## Testing Locally
This was developed using Python 3.6 on a Windows 10 machine.
1. `pip install -r requirements.txt`
2. In the `src` direcory, `python MacroNow.py`

## Usage
![](https://i.imgur.com/cmLNL0r.gif)\
In an effort to create a minimal GUI, a good portion of the functionality is
reliant on double clicking components of the interface. Anything I clicked
in the gif that wasn't a button needs a double click. Really, if it isn't
a button, try double clicking on it and see what it does.

## TODO List
This is a list of things I need to do / features that'll eventually be added.
Or at least the things I can think of right now as I write this.

### Features
In no particular order...
- [ ] Delete macros.
- [ ] Undo edit.
- [ ] Redo edit.
- [ ] Delete macro step.
- [ ] Manually add a macro step.
- [ ] Manually edit macro step.
- [ ] Drag and drop macros for organizing.
- [ ] Drag and drop macro steps for manual macro editing.
- [ ] Lots o' configuration options.
- [ ] Display the total time a macro takes to run.
- [ ] Make application look less ugly.
- [x] Shortcut to toggle recording.
- [ ] Start recording under focused macro step. Don't even know if this is.
    a good feature. We'll see.

### TODO
- [ ] Phase out Active Wait step type. Kinda useless.
- [ ] Prevent hotkey activiation when typing something in the application.
- [ ] Do something about conflicting hotkeys / shortcuts.
- [ ] Get rid of some of the QLCDNumber widgets. Don't need them anymore.
- [ ] Whatever other TODOs I left in the code.
- [ ] Port to C++ (Very last thing to do).
