# ===== Console Value things =====

# X;Ym

class Base:
    # Resets console styling to default, required if you want normal console messages to be normal after using CandyConsole
    ENDCC = '\033[0m'


class TextStyles:
    # Text Styles
    BOLD = ';1'
    NORMAL = ';2'
    ITALICS = ';3'
    UNDERLINE = ';4'
    BACKGROUND = ';7'
    STRIKETHROUGH = ';9'
    UNDERLINE_THICK = ';21'

    # A literal box around the text. This also warps messages to add a space around the message, for clarity.
    BOX = ';51'


class BackgroundColour:
    # Text BG Block 1
    BLACK = ';40'
    LIGHT_RED = ';41'
    GREEN = ';42'
    YELLOW = ';43'
    BLUE = ';44'
    PURPLE = ';45'
    TURQUOISE = ';46'
    LIGHT_GREY = ';47'

    # Text BG Block 2
    DARK_GREY = ';100'
    RED = ';101'
    BRIGHT_GREEN = ';102'
    BRIGHT_YELLOW = ';103'
    BRIGHT_BLUE = ';104'
    LIGHT_PURPLE = ';105'
    CYAN = ';106'
    WHITE = ';107'


class TextColour:
    # Text Colour Block 1
    BLACK = ';30'
    LIGHT_RED = ';31'
    GREEN = ';32'
    YELLOW = ';33'
    BLUE = ';34'
    PURPLE = ';35'
    TURQUOISE = ';36'
    LIGHT_GREY = ';37'

    # Text Colour Block 2
    DARK_GREY = ';90'
    RED = ';91'
    BRIGHT_GREEN = ';92'
    BRIGHT_YELLOW = ';93'
    BRIGHT_BLUE = ';94'
    LIGHT_PURPLE = ';95'
    CYAN = ';96'
    WHITE = ';97'


# ===== Print Functions =====

# This function accepts a single option
def colour_print(message, colortype):
    print(f"\033[0{colortype}{message}{Base.ENDCC}")


# This function may be easier to use quickly, but is more limiting
def candy_print_simple(message, colour="", background="", bold=False, italics=False, underline=False):
    candy = "\033[0"
    if bold:
        candy += TextStyles.BOLD
    if italics:
        candy += TextStyles.ITALICS
    if underline:
        candy += TextStyles.UNDERLINE

    if colour:
        candy += colour
    if background:
        candy += background

    candy += "m"
    print(f"{candy}{message}{Base.ENDCC}")


# This function may need an options array input, but is more powerful
def candy_print(message, options=[]):
    candy = "\033[0"
    for option in options:
        candy += option

    candy += "m"
    print(f"{candy}{message}{Base.ENDCC}")


def print_codes():
    # Example 1
    candy_print_simple("This is Example 1")
    # Example 2
    candy_print_simple("This is Example 2", colour=TextColour.CYAN)
    # Example 3
    candy_print_simple("This is Example 3", colour=TextColour.RED, background=BackgroundColour.BLACK, bold=True,
                       underline=True)

    # Example 4
    candy_options = [TextColour.GREEN, BackgroundColour.BLACK, TextStyles.UNDERLINE_THICK, TextStyles.BOLD,
                     TextStyles.BOX]
    candy_print("This is Example 4", candy_options)
    # Example 5
    candy_print("This is Example 5", [TextColour.BLACK, BackgroundColour.WHITE])

    candy_print_simple("My message", colour=TextColour.RED)
    candy_print("My message", [TextColour.RED])

    input()
    for i in range(0, 120):
        print(f"\033[0;{i}m TEST CODE 0,{i}{Base.ENDCC}")


def candy_colour(message, options=[]):
    candy = "\033[0"
    for option in options:
        candy += option

    candy += "m"
    return f"{candy}{message}{Base.ENDCC}"


def split_message(message, split_length=50, split_char=' '):
    lines = []
    v = message
    while len(v) > split_length:
        # split the line at a new line character if there is one
        if '\n' in v[:split_length]:
            split = v[:split_length].index('\n')
            lines.append(v[:split])
            v = v[split+1:]
            continue
        else:
            # get index of the last space in the first 80 characters
            split = v[:split_length].rfind(split_char)
        
            # split the verse at the space
            lines.append(v[:split])
            v = v[split+1:]  
    
    # v = v.strip().replace('\n', ' ')

    lines.append(v)
    return lines


if __name__ == '__main__':
    print_codes()

