# `astrajoystick`

> It's not an alien creature -- it's the AstraJoystick! 🎮 This
> interstellar device, with its sleek, otherworldly design and mystical
> magical buttons, has come all the way from the seventh dimension to
> grant you unparalleled control over your Linux system! Navigate the
> vast expanse of your desktop from the comfort of your napzone!

## Installation

### Prerequisites

Before diving in, ensure you have the following available:

-   Python 3.11 or later
-   Git
-   A Linux compatible joystick device (tested with a DualShock 2 PS2
    controller)

### Preliminary setup

Before `astrajoystick` can be run, we need the `uinput` kernel module
and appropriate permissions for `/dev/uinput`.

1.  Load the `uinput` module:

    ``` sh
    modprobe uinput
    ```

2.  Set permissions for `/dev/uinput`:

    ``` sh
    sudo chgrp input /dev/uinput
    sudo chmod 660 /dev/uinput
    ```

    This changes group ownership of `/dev/uinput` to `input` so that
    only users in the `input` group can access uinput.

3.  Add yourself to the `input` group:

    ``` sh
    sudo usermod -aG input "$USER"
    ```

    If you were not in the `input` group before, re-login for the change
    to take effect.

### Persistent setup (optional)

To make this setup persistent across reboot, follow these steps:

1.  Create a file `/etc/modules-load.d/uinput.conf` with the following
    content:

        uinput

    This will automatically load the `uinput` module during boot.

2.  Create a udev rule file `/etc/udev/rules.d/71-uinput.rules` with the
    following content:

        KERNEL=="uinput", GROUP="input", MODE="0660"

    This will automatically change group ownership of `/dev/uinput` to
    `input` and allow read-write access for users in that group whenever
    the `uinput` module is loaded.

### Install `astrajoystick`

Now, let's install `astrajoystick` inside a virtual environment:

1.  Clone the repository:

    ``` sh
    git clone 'https://github.com/joaopspsps/astrajoystick'
    cd astrajoystick
    ```

2.  Setup the virtual environment:

    ``` sh
    python -m venv .venv
    . .venv/bin/activate
    ```

3.  Install `astrajoystick`:

    ``` sh
    pip install .
    ```

## Usage

First, find out the path to your joystick device using the `evdev`
package inside the virtualenv. The path is shown in the "Device" column.
This is also useful to see what keys/events are being sent so you can
write your own configuration.

``` sh
python -m evdev.evtest
```

Once you have your joystick's path (`PATH`), run `astrajoystick` with
the desired config file:

``` sh
astrajoystick -c examples/ds2-general.toml PATH
```

Explore the available mappings in `examples/ds2-general.toml` and
customize it to suit your needs.

## Notes

-   Currently only tested with a DualShock 2 controller.
-   The default config file (`ds2-general.toml`) is tailored for the
    DualShock 2 controller and may require adjustments for other
    joysticks.
-   If the mouse motion doesn't work with a DualShock 2, try activating
    the analog button.

## Roadmap

-   Document the syntax and the features of the config file.
-   Make the configuration syntax more friendly.
-   Test with joysticks other than DualShock 2.
-   Write a config file mapping PS2 buttons to the entire keyboard.

## Acknowledgments

-   [enjoy](https://github.com/cjacker/enjoy): The initial inspiration
    for `astrajoystick`, especially for the `MotionThread` code.
