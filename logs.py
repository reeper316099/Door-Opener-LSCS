import os
import sys
import tty
import termios

options = ["Unfiltered", "Date", "IP address"]


def clear():
    os.system("clear")

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def process_selection(choice):
    if choice == 0:
        print("")
        with open("./logs.txt", "r") as logs:
            print(logs.read())
        print("")
    elif choice == 1:
        date = input("Date: ")

    elif choice == 2:
        ip_address = input("address: ")

        print("")
        with open("./logs.txt", "r") as logs:
            lines = logs.read().split("\n")
            filtered_lines = [line for line in lines if ip_address in line]
            print("\n".join(filtered_lines))
        print("")

def main():
    selection = 0

    while True:
        clear()

        print("--- Door Opener Logs ---\n")
        for i, option in enumerate(options):
            if i == selection:
                print(f"> {option}")
            else:
                print(f"  {option}")
        print("\nArrow keys to navigate, ENTER to select, Q to exit")

        key = getch()
        if key == '\x1b[A':
            selection = (selection - 1) % len(options)
        elif key == '\x1b[B':
            selection = (selection + 1) % len(options)
        elif key in ("\r", "\n"):
            process_selection(selection)
            break
        elif key.lower() == 'q':
            break


if __name__ == "__main__":
    main()
