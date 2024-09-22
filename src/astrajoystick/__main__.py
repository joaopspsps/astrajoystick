import argparse
from importlib.metadata import version

from .mainlooper import Mainlooper


def main():
    parser = argparse.ArgumentParser(prog="astrajoystick")
    parser.add_argument(
        "device", type=str, metavar="DEVICE", help="the path to the joystick device"
    )
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="config.toml",
        metavar="PATH",
        help="the path to the config file",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {version('astrajoystick')}",
    )
    args = parser.parse_args()

    looper = Mainlooper(args.device, args.config)

    print("--- Press ctrl-c to stop ---")
    try:
        looper.mainloop()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
