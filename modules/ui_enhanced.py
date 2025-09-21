"""
Enhanced UI utilities for beautiful console interface
"""

import os
import shutil
from typing import List, Tuple


class Colors:
    """ANSI color codes for terminal styling"""
    # Regular colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDERLINE = "\033[4m"
    
    # Text colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def get_terminal_width():
    """Get terminal width or default to 80"""
    try:
        return shutil.get_terminal_size().columns
    except:
        return 80


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def print_header(title: str, subtitle: str = "", width: int = None):
    """Print a beautiful header with title and optional subtitle"""
    if width is None:
        width = min(get_terminal_width(), 100)
    
    # Create top border
    border = "╔" + "═" * (width - 2) + "╗"
    
    print(f"\n{Colors.BRIGHT_CYAN}{border}{Colors.RESET}")
    
    # Title line
    title_line = f"║{title.center(width - 2)}║"
    print(f"{Colors.BRIGHT_CYAN}║{Colors.BRIGHT_WHITE}{Colors.BOLD}{title.center(width - 2)}{Colors.RESET}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
    
    # Subtitle if provided
    if subtitle:
        print(f"{Colors.BRIGHT_CYAN}║{Colors.BRIGHT_BLACK}{subtitle.center(width - 2)}{Colors.RESET}{Colors.BRIGHT_CYAN}║{Colors.RESET}")
    
    # Bottom border
    bottom_border = "╚" + "═" * (width - 2) + "╝"
    print(f"{Colors.BRIGHT_CYAN}{bottom_border}{Colors.RESET}")


def print_section(title: str, width: int = None):
    """Print a section header"""
    if width is None:
        width = min(get_terminal_width(), 80)
    
    print(f"\n{Colors.BRIGHT_YELLOW}{'─' * width}{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}▶ {Colors.BRIGHT_WHITE}{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.BRIGHT_YELLOW}{'─' * width}{Colors.RESET}")


def print_box(content: List[str], title: str = "", box_type: str = "info"):
    """Print content in a beautiful box"""
    if not content:
        return
        
    width = min(get_terminal_width(), 80)
    content_width = width - 4
    
    # Choose colors based on box type
    if box_type == "warning":
        border_color = Colors.BRIGHT_YELLOW
        title_color = Colors.BRIGHT_YELLOW
        content_color = Colors.YELLOW
    elif box_type == "error":
        border_color = Colors.BRIGHT_RED
        title_color = Colors.BRIGHT_RED
        content_color = Colors.RED
    elif box_type == "success":
        border_color = Colors.BRIGHT_GREEN
        title_color = Colors.BRIGHT_GREEN
        content_color = Colors.GREEN
    elif box_type == "danger":
        border_color = Colors.BRIGHT_RED
        title_color = Colors.BRIGHT_RED + Colors.BOLD
        content_color = Colors.BRIGHT_RED
    else:  # info
        border_color = Colors.BRIGHT_CYAN
        title_color = Colors.BRIGHT_CYAN
        content_color = Colors.CYAN
    
    # Top border
    print(f"\n{border_color}┌{'─' * (width - 2)}┐{Colors.RESET}")
    
    # Title if provided
    if title:
        title_line = f"│ {title_color}{Colors.BOLD}{title}{Colors.RESET} "
        padding = width - len(title) - 4
        print(f"{border_color}{title_line}{' ' * padding}│{Colors.RESET}")
        print(f"{border_color}├{'─' * (width - 2)}┤{Colors.RESET}")
    
    # Content
    for line in content:
        # Word wrap if needed
        if len(line) > content_width:
            words = line.split(' ')
            current_line = ""
            for word in words:
                if len(current_line + word) <= content_width:
                    current_line += word + " "
                else:
                    if current_line:
                        print(f"{border_color}│ {content_color}{current_line.ljust(content_width - 2)}{Colors.RESET}{border_color} │{Colors.RESET}")
                    current_line = word + " "
            if current_line:
                print(f"{border_color}│ {content_color}{current_line.ljust(content_width - 2)}{Colors.RESET}{border_color} │{Colors.RESET}")
        else:
            print(f"{border_color}│ {content_color}{line.ljust(content_width - 2)}{Colors.RESET}{border_color} │{Colors.RESET}")
    
    # Bottom border
    print(f"{border_color}└{'─' * (width - 2)}┘{Colors.RESET}")


def print_menu_option(number: int, icon: str, text: str, description: str = "", color: str = Colors.BRIGHT_WHITE):
    """Print a formatted menu option"""
    option_text = f"{Colors.BRIGHT_BLUE}{number}.{Colors.RESET} {icon} {color}{Colors.BOLD}{text}{Colors.RESET}"
    if description:
        option_text += f" {Colors.DIM}({description}){Colors.RESET}"
    print(f"  {option_text}")


def print_list_items(items: List[str], title: str, icon: str, color: str = Colors.BRIGHT_WHITE):
    """Print a formatted list with items"""
    count_color = Colors.BRIGHT_YELLOW if len(items) > 0 else Colors.BRIGHT_BLACK
    print(f"\n{icon} {Colors.BOLD}{title} {count_color}({len(items)}){Colors.RESET}:")
    
    if not items:
        print(f"  {Colors.DIM}(пусто){Colors.RESET}")
    else:
        for i, item in enumerate(items, 1):
            item_display = item if item.strip() else f"{Colors.DIM}(пустая строка){Colors.RESET}"
            print(f"  {Colors.BRIGHT_BLACK}{i:2}.{Colors.RESET} {color}{item_display}{Colors.RESET}")


def print_status(message: str, status_type: str = "info"):
    """Print a status message with appropriate colors"""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️",
        "danger": "🚨"
    }
    
    colors = {
        "success": Colors.BRIGHT_GREEN,
        "error": Colors.BRIGHT_RED,
        "warning": Colors.BRIGHT_YELLOW,
        "info": Colors.BRIGHT_BLUE,
        "danger": Colors.BRIGHT_RED + Colors.BOLD
    }
    
    icon = icons.get(status_type, "•")
    color = colors.get(status_type, Colors.WHITE)
    
    print(f"{icon} {color}{message}{Colors.RESET}")


def get_input_with_prompt(prompt: str, input_type: str = "default"):
    """Get user input with a nicely formatted prompt"""
    if input_type == "choice":
        prompt_color = Colors.BRIGHT_CYAN
    elif input_type == "username":
        prompt_color = Colors.BRIGHT_YELLOW
    elif input_type == "danger":
        prompt_color = Colors.BRIGHT_RED
    else:
        prompt_color = Colors.BRIGHT_WHITE
    
    return input(f"\n{prompt_color}➤ {prompt}{Colors.RESET} ").strip()


def print_separator(char: str = "═", color: str = Colors.BRIGHT_BLACK):
    """Print a separator line"""
    width = min(get_terminal_width(), 80)
    print(f"{color}{char * width}{Colors.RESET}")


def print_progress_bar(current: int, total: int, width: int = 50):
    """Print a progress bar"""
    if total == 0:
        percentage = 100
    else:
        percentage = min(100, (current * 100) // total)
    
    filled = (percentage * width) // 100
    empty = width - filled
    
    bar = "█" * filled + "░" * empty
    print(f"\r{Colors.BRIGHT_CYAN}[{bar}] {percentage:3}% ({current}/{total}){Colors.RESET}", end="", flush=True)