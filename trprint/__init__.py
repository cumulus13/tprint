#!/usr/bin/env python3

# File: tprint/__init__.py
# Author: Hadi Cahyadi <cumulus13@gmail.com>
# Date: 2026-09-30
# Description: 
# License: MIT

import sys
import os
from datetime import datetime
import traceback

class Check:
    """Auto-detect terminal color support across all major OS."""

    def __new__(cls, force = None):
        """Return detected color mode immediately (not an instance)."""
        return cls.detect_color_support(force)

    # --- Environment checks ---
    @staticmethod
    def _check_env_truecolor() -> bool:
        colorterm = str(os.getenv("COLORTERM") or "").lower()
        if "truecolor" in colorterm or "24bit" in colorterm:
            return True
        if os.getenv("WT_SESSION"):  # Windows Terminal
            return True
        return False

    # --- curses terminfo (Unix-like only) ---
    @staticmethod
    def _curses_colors() -> int:
        try:
            import curses
            curses.setupterm()
            n = curses.tigetnum("colors")
            if isinstance(n, int):
                return n
        except Exception:
            pass
        return -1

    # --- Windows ANSI Enable ---
    @staticmethod
    def enable_windows_ansi() -> bool:
        if sys.platform != "win32":
            return False

        import ctypes

        try:
            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            if handle in (0, -1):
                return False

            mode = ctypes.c_uint()
            if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                return False

            ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
            if new_mode != mode.value:
                if not kernel32.SetConsoleMode(handle, new_mode):
                    return False
            return True
        except Exception:
            return False

    # --- Core detection logic ---
    @classmethod
    def detect_color_support(cls, force = None) -> str:
        if force in (
            ColorSupport.TRUECOLOR,
            ColorSupport.COLOR_256,
            ColorSupport.BASIC,
            ColorSupport.NONE,
        ):
            return force

        if not sys.stdout.isatty():
            return ColorSupport.NONE

        if cls._check_env_truecolor():
            return ColorSupport.TRUECOLOR

        term = str(os.getenv("TERM") or "").lower()
        if "256color" in term:
            return ColorSupport.COLOR_256
        if "color" in term:
            return ColorSupport.BASIC

        colors = cls._curses_colors()
        if colors >= 16777216:
            return ColorSupport.TRUECOLOR
        if colors >= 256:
            return ColorSupport.COLOR_256
        if colors >= 8:
            return ColorSupport.BASIC

        if sys.platform == "win32":
            if cls.enable_windows_ansi():
                if cls._check_env_truecolor() or sys.getwindowsversion().major >= 10:
                    return ColorSupport.TRUECOLOR
                return ColorSupport.BASIC
            return ColorSupport.NONE

        return ColorSupport.BASIC

class ColorSupport:
    TRUECOLOR = "truecolor"
    COLOR_256 = "256color"
    BASIC = "basic"
    NONE = "none"

class Colors:
    """Handler untuk color schemes dengan berbagai format output."""

    def __init__(
        self,
        color_type='ansi',
        show_background=False,

        emergency_color: str = '',        
        alert_color: str = '',        
        critical_color: str = '',        
        error_color: str = '',        
        warning_color: str = '',        
        fatal_color: str = '',        
        notice_color: str = '',        
        debug_color: str = '',        
        info_color: str = '',
        success_color: str = '',
        primary_color: str = '',
        danger_color: str = '',
        ):

        self.color_type = color_type
        self.show_background = show_background

        self.emergency_color = emergency_color
        self.alert_color = alert_color
        self.critical_color = critical_color
        self.error_color = error_color
        self.warning_color = warning_color
        self.fatal_color = fatal_color
        self.notice_color = notice_color
        self.debug_color = debug_color
        self.info_color = info_color
        self.success_color = success_color
        self.primary_color = primary_color
        self.danger_color = danger_color

    def rich_color(self, show_background=False):
        """Restore color scheme in rich library format."""
        if show_background:
            COLORS = {
                'debug': self.debug_color or "#000000 on #FFAA00",
                'info': self.info_color or "#000000 on #00FF00",
                'success': self.info_color or "#00FF00 on #2D2D2D",
                'warning': self.warning_color or "black on #FFFF00",
                'error': self.error_color or "white on red",
                'critical': self.critical_color or "bright_white on #0000FF",
                'fatal': self.fatal_color or "#FFAA00 on #FF557F",
                'emergency': self.emergency_color or "bright_white on #AA00FF",
                'alert': self.alert_color or "bright_white on #005500",
                'notice': self.notice_color or "black on #00FFFF",
                'primary': self.primary_color or "white on #000000",
                'danger': self.danger_color or "#00FFFF on #FF00FF",
                'reset': '',
            }
        else:
            COLORS = {
                'debug': self.debug_color or "#FFAA00",
                'info': self.info_color or "#00FF00",
                'success': self.success_color or "#00FF00",
                'warning': self.warning_color or "#FFFF00",
                'error': self.error_color or "red",
                'critical': self.critical_color or "#0000FF",
                'fatal': self.fatal_color or "#FF557F",
                'emergency': self.emergency_color or "#AA00FF",
                'alert': self.alert_color or "#005500",
                'notice': self.notice_color or "#00FFFF",
                'primary': self.primary_color or "#000000",
                'danger': self.danger_color or "#FF00FF",
                'reset': '',
            }
        return COLORS

    def check(self):
        """Detection and Return Color Scheme according to the Terminal Support."""
        COLORS = {}
        mode = Check()
        
        if mode == ColorSupport.TRUECOLOR:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[38;2;0;0;0;48;2;255;170;0m",        # #000000 on #FFAA00
                        'info': self.info_color or "\x1b[38;2;0;0;0;48;2;0;255;0m",           # #000000 on #00FF00
                        'success': self.success_color or "\x1b[38;2;0;0;0;48;2;0;255;0m",           # #000000 on #00FF00
                        'warning': self.warning_color or "\x1b[38;2;0;0;0;48;2;255;255;0m",      # black on #FFFF00
                        # 'error': "\x1b[38;2;255;255;255;48;2;255;0;0m",    # white on red (RGB 24-bit) (Bugs)
                        'error': self.error_color or "\x1b[97;41m",                            # white on red
                        'critical': self.critical_color or "\x1b[38;2;255;255;255;48;2;0;0;255m", # bright_white on #0000FF
                        'fatal': self.fatal_color or "\x1b[38;2;0;0;255;48;2;255;85;127m",     # blue on #FF557F
                        'emergency': self.warning_color or "\x1b[38;2;255;255;255;48;2;170;0;255m", # bright_white on #AA00FF
                        'alert': self.alert_color or "\x1b[38;2;255;255;255;48;2;0;85;0m",     # bright_white on #005500
                        'notice': self.notice_color or "\x1b[38;2;0;0;0;48;2;0;255;255m",       # black on #00FFFF
                        'primary': self.primary_color or "\x1b[38;2;255;255;255;48;2;0;0;0m",  # bright_white on #000000
                        'danger': self.danger_color or "\x1b[38;2;255;255;255;48;2;255;0;255m", # bright_white on #FF00FF
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[38;2;255;170;0m",        # #FFAA00
                        'info': self.info_color or "\x1b[38;2;0;255;0m",           # #00FF00
                        'success': self.success_color or "\x1b[38;2;0;255;0m",           # #00FF00
                        'warning': self.warning_color or "\x1b[38;2;255;255;0m",      # #FFFF00
                        'error': self.error_color or "\x1b[38;2;255;0;0m",          # red
                        'critical': self.critical_color or "\x1b[38;2;0;0;255m",       # #0000FF
                        'fatal': self.fatal_color or "\x1b[38;2;255;85;127m",       # #FF557F
                        'emergency': self.emergency_color or "\x1b[38;2;170;0;255m",    # #AA00FF
                        'alert': self.alert_color or "\x1b[38;2;0;85;0m",           # #005500
                        'notice': self.notice_color or "\x1b[38;2;0;255;255m",       # #00FFFF
                        'primary': self.primary_color or "\x1b[38;2;0;0;0m",        # #000000
                        'danger': self.danger_color or "\x1b[38;2;255;0;255m",      # #FF00FF
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.COLOR_256:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[30;48;5;214m",      # black on orange
                        'info': self.info_color or "\x1b[30;48;5;46m",        # black on bright green
                        'success': self.success_color or "\x1b[30;48;5;46m",        # black on bright green
                        'warning': self.warning_color or "\x1b[30;48;5;226m",    # black on yellow
                        'error': self.error_color or "\x1b[97;41m",            # white on red
                        'critical': self.critical_color or "\x1b[97;44m",         # white on blue
                        'fatal': self.fatal_color or "\x1b[21;48;5;204m",      # blue on pink
                        'emergency': self.emergency_color or "\x1b[97;48;5;129m",  # white on purple
                        'alert': self.alert_color or "\x1b[97;48;5;22m",       # white on dark green
                        'notice': self.notice_color or "\x1b[30;48;5;51m",      # black on cyan
                        'primary': self.primary_color or "\x1b[30;48;5;0m",    # black on black
                        'danger': self.danger_color or "\x1b[30;48;5;196m",     # black on red
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[38;5;214m",      # orange
                        'info': self.info_color or "\x1b[38;5;46m",        # bright green
                        'success': self.success_color or "\x1b[38;5;46m",        # bright green
                        'warning': self.warning_color or "\x1b[38;5;226m",    # yellow
                        'error': self.error_color or "\x1b[91m",            # red
                        'critical': self.critical_color or "\x1b[38;5;21m",    # blue
                        'fatal': self.fatal_color or "\x1b[38;5;204m",      # pink
                        'emergency': self.emergency_color or "\x1b[38;5;129m",  # purple
                        'alert': self.alert_color or "\x1b[38;5;22m",       # dark green
                        'notice': self.notice_color or "\x1b[38;5;51m",      # cyan
                        'primary': self.primary_color or "\x1b[38;5;0m",    # black
                        'danger': self.danger_color or "\x1b[91m",            # red
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.BASIC:
            if self.color_type == 'ansi':
                if self.show_background:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[30;43m",      # black on yellow
                        'info': self.info_color or "\x1b[30;42m",       # black on green
                        'success': self.success_color or "\x1b[30;42m",       # black on green
                        'warning': self.warning_color or "\x1b[30;43m",    # black on yellow
                        'error': self.error_color or "\x1b[97;41m",      # white on red
                        'critical': self.critical_color or "\x1b[97;44m",   # white on blue
                        'fatal': self.fatal_color or "\x1b[97;45m",      # white on magenta
                        'emergency': self.emergency_color or "\x1b[97;45m",  # white on magenta
                        'alert': self.alert_color or "\x1b[97;42m",      # white on green
                        'notice': self.notice_color or "\x1b[30;46m",     # black on cyan
                        'primary': self.primary_color or "\x1b[30;48;5;0m",    # black on black
                        'danger': self.danger_color or "\x1b[30;48;5;196m",     # black on red
                        'reset': "\x1b[0m"
                    })
                else:
                    COLORS = SafeDict({
                        'debug': self.debug_color or "\x1b[33m",      # yellow
                        'info': self.info_color or "\x1b[32m",       # green
                        'success': self.success_color or "\x1b[32m",       # green
                        'warning': self.warning_color or "\x1b[33m",    # yellow
                        'error': self.error_color or "\x1b[31m",      # red
                        'critical': self.critical_color or "\x1b[34m",   # blue
                        'fatal': self.fatal_color or "\x1b[35m",      # magenta
                        'emergency': self.emergency_color or "\x1b[35m",  # magenta
                        'alert': self.alert_color or "\x1b[32m",      # green
                        'notice': self.notice_color or "\x1b[36m",     # cyan
                        'primary': self.primary_color or "\x1b[30m",    # black 
                        'danger': self.danger_color or "\x1b[31m",
                        'reset': "\x1b[0m"
                    })
            elif self.color_type == 'rich':
                # For Basic Mode, keep using the rich_color format
                COLORS = self.rich_color(self.show_background)
                
        elif mode == ColorSupport.NONE:
            COLORS = SafeDict({
                'debug': '',
                'info': '',
                'success': '',
                'warning': '',
                'error': '',
                'critical': '',
                'fatal': '',
                'emergency': '',
                'alert': '',
                'notice': '',
                'primary': '',
                'danger': '',
                'reset': ''
            })
        
        return COLORS

def print_traceback(
    exc_info,
    padding_left=0,
    show_datetime=True,
    show_emoji=False,
    emoji="❌ ",
    console=None,
    custom_message=None,
    status=None,
):
    try:
        from rich.text import Text
        from rich.cells import cell_len

        if not console:
            from rich.console import Console
            console = Console()

    except Exception:
        return print_traceback_ansi(
            exc_info,
            padding_left=padding_left,
            show_datetime=show_datetime,
            show_emoji=show_emoji,
            emoji=emoji,
            status=status,
        )

    exc_type, exc_value, tb_details = exc_info

    if padding_left is None:
        padding_left = 0

    terminal_width = os.get_terminal_size()[0]

    # Keep the original value because your code changes
    # padding_left to 4 later.
    original_padding_left = padding_left

    icon = emoji.strip() + ' ' if show_emoji else ' '
    timestamp = ''

    # Timestamp
    if show_datetime:
        timestamp = datetime.now().strftime(
            "[bold #FF00FF]%Y[/]-"
            "[bold #0055FF]%m[/]-"
            "[bold #FF55FF]%d[/] "
            "[bold #FFFF00]%H[/]:"
            "[bold #FF5500]%M[/]:"
            "[bold #AAAAFF]%S[/]."
            "[bold #00FF00]%f[/]"
        )

        icon = emoji + ' ' if show_emoji else ' '

    # Format traceback parts with colors
    type_text = Text(
        str(exc_type),
        style="white on red",
    )

    # Include custom message in value if provided
    if custom_message:
        value_text = Text(
            f"{custom_message}: {str(exc_value)}",
            style="black on #FFFF00",
        )
    else:
        value_text = Text(
            str(exc_value),
            style="black on #FFFF00",
        )

    if isinstance(tb_details, str):
        tb_string = tb_details
    else:
        tb_string = "".join(traceback.format_tb(tb_details))

    tb_text = Text(
        "\n".join(
            [
                padding_left * ' ' if padding_left
                else 2 * ' ' + i
                for i in tb_string.split("\n")
            ]
        ),
        style="#00FFFF",
    )

    # =========================================================
    # STATUS MODE
    # =========================================================
    if status is not None:
        status_text = Text()

        # -----------------------------------------------------
        # First line
        #
        # EXACTLY corresponds to:
        #
        # console.print(
        #     f"{icon}{padding_left * ' '}"
        #     f"[bold]{timestamp}[/bold] - ",
        #     end=''
        # )
        #
        # console.print(type_text, end='')
        # console.print(" : ", end='')
        # console.print(value_text)
        # -----------------------------------------------------

        if show_datetime:
            status_text.append(
                Text.from_markup(
                    f"{icon}"
                    f"{padding_left * ' '}"
                    f"[bold]{timestamp}[/bold] - "
                )
            )
        else:
            status_text.append(
                Text(
                    f"{icon}{padding_left * ' '}"
                )
            )

        status_text.append(type_text)
        status_text.append(" : ")
        status_text.append(value_text)
        status_text.append("\n")

        # -----------------------------------------------------
        # Traceback body
        #
        # EXACTLY corresponds to:
        #
        # console.print(Text(padding_left * ' ') + tb_text)
        # -----------------------------------------------------

        status_text.append(
            Text(padding_left * ' ') + tb_text
        )
        status_text.append("\n")

        # -----------------------------------------------------
        # Second timestamp/header
        #
        # Your original code:
        #
        # if not padding_left:
        #     padding_left = 4
        #     console.print(
        #         f" [bold]{timestamp}[/bold] - ",
        #         end=''
        #     ) if timestamp else None
        #
        # console.print(type_text, ":", value_text)
        #
        # IMPORTANT:
        # The timestamp must start where the FIRST timestamp
        # starts AFTER the emoji.
        #
        # If icon == "❌ ", reserve exactly its terminal width.
        # -----------------------------------------------------

        if not padding_left:
            padding_left = 4

            if timestamp:
                # Reserve the visual width of "❌ "
                # without actually displaying it.
                status_text.append(
                    " " * cell_len(icon)
                )

                status_text.append(
                    Text.from_markup(
                        f"[bold]{timestamp}[/bold] - "
                    )
                )

        status_text.append(type_text)
        status_text.append(" : ")
        status_text.append(value_text)

        # -----------------------------------------------------
        # DO NOT add the separator to status.update().
        #
        # Your original separator condition is unreachable here
        # after padding_left becomes 4, and the separator should
        # not become part of the live status content.
        # -----------------------------------------------------

        status.update(status_text)

        return status_text

    # =========================================================
    # NORMAL RICH OUTPUT
    # YOUR ORIGINAL OUTPUT PATH
    # =========================================================

    # Timestamp
    if show_datetime:
        console.print(
            f"{icon}{padding_left * ' '}[bold]{timestamp}[/bold] - ",
            end=''
        )

    # Format traceback parts with colors
    console.print(
        Text(icon) + Text(padding_left * ' ') + type_text
        if not show_datetime else type_text,
        end=''
    )

    console.print(" : ", end='')
    console.print(value_text)
    console.print(
        Text(padding_left * ' ') + tb_text
    )

    if not padding_left:
        padding_left = 4
        console.print(
            f" [bold]{timestamp}[/bold] - ",
            end=''
        ) if timestamp else None

    console.print(type_text, ":", value_text)

    # Separator line
    if not padding_left:
        padding_left = 4
        console.print("-" * terminal_width)


# --- ANSI colored traceback printer ---
def print_traceback_ansi(
    exc_info,
    padding_left: int = 0,
    show_datetime: bool = True,
    show_emoji: bool = False,
    emoji: str = "❌ ",
    show_background: bool = False,
    status=None,
):
    """
    Print traceback using ANSI colors from CustomFormatter.COLORS
    (or fallback).

    If status is supplied, update the Rich status instead of
    writing the ANSI traceback directly to stdout.
    """

    colors = Colors(
        color_type='ansi',
        show_background=show_background,
    ).check()

    exc_type, exc_value, tb_details = exc_info

    if padding_left is None:
        padding_left = 0

    reset = colors.get("reset", "")
    type_color = colors.get("error", "") or colors.get("emergency", "")
    value_color = colors.get("warning", "") or colors.get("error", "")
    tb_color = colors.get("notice", "") or ""

    # Timestamp
    timestamp = ""

    if show_datetime:
        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]

    icon = (emoji + " ") if show_emoji else ""

    # Build the same ANSI output in the original order.
    output = []

    output.append(
        f"{icon}{timestamp if timestamp else ''}"
    )

    output.append(
        f"{type_color}"
        f"{exc_type.__name__ if hasattr(exc_type, '__name__') else str(exc_type)}"
        f"{reset} : "
        f"{value_color}{str(exc_value)}{reset}"
    )

    if isinstance(tb_details, str):
        tb_lines = tb_details.splitlines()
    else:
        tb_lines = traceback.format_tb(tb_details)
        tb_lines = sum(
            (t.splitlines() for t in tb_lines),
            [],
        )

    for line in tb_lines:
        if line is None:
            continue

        for sub in str(line).splitlines():
            output.append(
                f"{tb_color}"
                f"{' ' * max(4, padding_left)}"
                f"{sub}"
                f"{reset}"
            )

    # Status path
    if status is not None:
        try:
            from rich.text import Text

            status.update(
                Text.from_ansi("\n".join(output))
            )

            return
        except Exception:
            pass

    # Original stdout path
    for line in output:
        sys.stdout.write(line + "\n")


def print_exception(e: Exception | None = None, *args, **kwargs):
    """
    Convenience function to print current exception.

    status:
        rich.console.Status
    """

    status = kwargs.pop('status', None)

    if not e:
        return print_traceback(
            sys.exc_info(),
            *args,
            status=status,
            **kwargs,
        )

    # If e is a string (custom message), get the current exception
    if isinstance(e, str):
        exc_info = sys.exc_info()
        custom_message = e
        remaining_args = args
    else:
        exc_info = sys.exc_info()
        custom_message = None
        remaining_args = args[2:] if len(args) > 2 else ()

    return print_traceback(
        exc_info,
        *remaining_args,
        custom_message=custom_message,
        status=status,
        **kwargs,
    )

def tprint(*args, **kwargs):
    return print_exception(*args, **kwargs)


    