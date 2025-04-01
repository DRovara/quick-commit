"""Provides functionality for prompting the user for input."""

# ruff: noqa: T201
from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from types import ModuleType

termios: ModuleType | None
try:
    import termios
    import tty
except ImportError:
    termios = None
    import msvcrt

if TYPE_CHECKING:
    from collections.abc import Callable


COLOUR_YELLOW = "\033[33m"
STYLE_BOLD = "\033[1m"
COLOUR_RESET = "\033[0m"


def get_filter_rule(options: list[str]) -> Callable[[str, int, list[str], dict[str, Any]], tuple[list[str], int]]:
    """A simple filter function for prompts.

    Args:
        options (list[str]): The list of options to filter

    Returns:
        Callable[[str, int, list[str], dict[str, Any]], tuple[list[str], int]]: The filter function.
    """

    def fun(state: str, index: int, current_options: list[str], _tags: dict[str, Any]) -> tuple[list[str], int]:
        """The filter function the be returned.

        Args:
            state (str): The current state of the prompt.
            index (int): The current index of the prompt.
            current_options (list[str]): The current options of the prompt.
            _tags (dict[str, Any]): The tags of the prompt.

        Returns:
            tuple[list[str], int]: The filter result.
        """
        old_item = current_options[index]
        filtered = [option for option in options if state.lower() in option.lower()]
        index = filtered.index(old_item) if old_item in filtered else 0
        return filtered, index

    return fun


def getchar() -> str:
    """Get a single character from the user.

    Returns:
        str: The character entered by the user.
    """
    if termios is not None:
        return getchar_unix()
    return getchar_windows()


def getchar_windows() -> str:
    """Get a single character from the user on windows systems.

    Returns:
        str: The character entered by the user.
    """
    char = msvcrt.getch()
    if char == b"\xe0":
        char = msvcrt.getch()
        return _get_windows_special_key(char)[0]
    if char == b"\x00":
        char = msvcrt.getch()
        return _get_windows_special_key(char)[0]
    try_translate = _get_windows_special_key(char)
    if try_translate[1]:
        return try_translate[0]
    return char.decode("utf-8")


def _get_windows_special_key(key: bytes) -> tuple[str, bool]:
    """Map Windows special keys to their names.

    Args:
        key: bytearray: The special key code.

    Returns:
        str: The name of the special key.
    """
    special_keys = {
        b"H": "up",
        b"P": "down",
        b"K": "left",
        b"M": "right",
        b"G": "home",
        b"O": "end",
        b"R": "insert",
        b"S": "delete",
        b"\x08": "backspace",
        b"\r": "return",
        b"\t": "tab",
        b"\x1b": "esc",
    }
    if key in special_keys:
        return (special_keys.get(key, f"unknown:{key!r}"), True)
    return ("", False)


def getchar_unix() -> str:
    """Get a single character from the user on unix systems.

    Returns:
        str: The character entered by the user.
    """
    if termios is None:
        msg = "termios module not available"
        raise ImportError(msg)
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())  # type: ignore[attr-defined]
    try:
        while True:
            b = os.read(sys.stdin.fileno(), 3).decode()
            if len(b) == 3:
                k = ord(b[2])
                if k in {65, 66, 67, 68}:
                    k += 100
            else:
                k = ord(b)
            key_mapping = {
                127: "backspace",
                10: "return",
                32: " ",
                9: "tab",
                27: "esc",
                165: "up",
                166: "down",
                167: "right",
                168: "left",
            }
            return key_mapping.get(k, chr(k))
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)


def show(
    options: list[str],
    header: str,
    allow_keys: bool = True,
    on_update: Callable[[str, int, list[str], dict[str, Any]], tuple[list[str], int]] | None = None,
    wrap_above: bool = True,
    wrap_below: bool = True,
) -> tuple[str, int, str]:
    """Show a prompt to the user consisting of multiple options that can be selected using arrow keys.

    Args:
        options (list[str]): The list of options to display.
        header (str): The header to display above the options.
        allow_keys (bool, optional): Determines, whether keypresses should be registered and displayed (e.g. for filters). Defaults to True.
        on_update (Callable[[str, int, list[str], dict[str, Any]], tuple[list[str], int]] | None, optional): A function to be called when the user gives any input. Defaults to None.
        wrap_above (bool, optional): Determines, whether moving above the first element will wrap to the end. Defaults to True.
        wrap_below (bool, optional): Determines, whether moving below the last element will wrap to the start. Defaults to True.

    Returns:
        tuple[str, int, str]: The state, index and selected option.
    """
    state = ""
    running = True
    index = 0
    last_options = options
    original_options = options
    tags: dict[str, Any] = {}

    def print_state() -> None:
        print(header + state)
        for i, option in enumerate(options):
            pre = f"{COLOUR_YELLOW}{STYLE_BOLD} » " if i == index else "   "
            print(f"{pre}{option}{COLOUR_RESET}")

    def refresh() -> None:
        print("\r\033[K", flush=True)
        for _ in last_options:
            print("\r\033[K", flush=True)
        for _ in range(len(last_options) + 1):
            print("\033[F", end="", flush=True)

    def return_caret() -> None:
        for _ in range(len(options) + 1):
            print("\033[F", end="", flush=True)
        print(f"\033[{len(header) + len(state)}C", end="", flush=True)

    def hide_cursor() -> None:
        print("\033[?25l", end="", flush=True)

    def show_cursor() -> None:
        print("\033[?25h", end="", flush=True)

    print_state()
    if allow_keys:
        return_caret()

    try:
        while running:
            if not allow_keys:
                return_caret()
            refresh()
            print_state()
            if allow_keys:
                return_caret()
            else:
                hide_cursor()
            last_options = options

            key = getchar()
            if len(key) == 1 and allow_keys:
                state += key
            elif key == "backspace":
                state = state[:-1]
            elif key == "up":
                index -= 1
                if index < 0:
                    index = 0 if not wrap_above else len(options) - 1
            elif key == "down":
                index += 1
                if index >= len(options):
                    index = len(options) - 1 if not wrap_below else 0
            elif key == "return":
                running = False
                show_cursor()
            else:
                continue

            if on_update:
                options, index = on_update(state, index, options, tags)
            if len(options) == 0:
                options = ["---"]
            if index < 0 or index >= len(options):
                index = 0
    except:
        show_cursor()
        if not allow_keys:
            return_caret()
        refresh()
        raise

    if not allow_keys:
        return_caret()
    refresh()
    print(header + f"{STYLE_BOLD}" + options[index] + f"{COLOUR_RESET}")
    result = options[index]

    if options[index] in original_options:
        index = original_options.index(options[index])
    return state, index, result


def show_with_filter(options: list[str], header: str) -> tuple[str, int, str]:
    """Show a prompt to the user consisting of multiple options that can be selected using arrow keys, with a filter.

    Args:
        options (list[str]): The list of options to display.
        header (str): The header to display above the options.

    Returns:
        tuple[str, int, str]: The state, index and selected option.
    """
    return show(options, header, True, get_filter_rule(options))


def multiline_input() -> str:
    """Get a multiline input from the user.

    Returns:
        str: The multiline input.
    """
    result = ""
    first = True
    while True:
        line = input()
        if not line:
            break
        if not first:
            result += "\n"
        first = False
        result += line
    return result
