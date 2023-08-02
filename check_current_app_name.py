import time
import subprocess


def get_frontmost_app():
    try:
        front_app_name = subprocess.check_output(
            [
                "osascript",
                "-e",
                'tell application "System Events" to get the name of every process whose frontmost is true',
            ],
            text=True,
        ).strip()
        return front_app_name
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def main():
    last_app = ""
    while True:
        front_app = get_frontmost_app()
        if front_app and front_app != last_app:
            print(f"Frontmost app changed: {front_app}")
            last_app = front_app
        time.sleep(0.1)


if __name__ == "__main__":
    main()
