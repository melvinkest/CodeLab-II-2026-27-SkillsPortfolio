import ctypes
import os
import random
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(HERE, "..", "E2 - Joke Teller", "randomJokes.txt")

PREFERRED_FONT = "Google Sans"  # the font the app is designed for
FALLBACK_FONT = "Segoe UI"      # used if Google Sans cannot be loaded or installed
FONT = PREFERRED_FONT        # replaced at start-up with the font actually used

THEME_DIR = "sun-valley"

FONT_DIR = os.path.join(HERE, "fonts")
FONT_FILES = ["GoogleSans-Regular.ttf", "GoogleSans-Bold.ttf"]

# Colours for each mode.
PALETTES = {
    "light": {"background": "#fafafa", "text": "#202020", "accent": "#2f60d8"},
    "dark": {"background": "#1c1c1c", "text": "#ffffff", "accent": "#60cdff"},
}

ROLE_STYLES = {"text": "TLabel", "accent": "Accent.TLabel"}

# Windows draws the title bar through the Desktop Window Manager (DWM).
DWMWA_USE_IMMERSIVE_DARK_MODE = 20   
DWMWA_CAPTION_COLOR = 35             
DWMWA_TEXT_COLOR = 36                


def colourRef(hexColour):
    hexColour = hexColour.lstrip("#")
    red, green, blue = (int(hexColour[i:i + 2], 16) for i in (0, 2, 4))
    return red | (green << 8) | (blue << 16)


def styleTitleBar(root, background, text, dark):
    """Colour the Windows title bar to match the mode. Does nothing on other systems."""
    if sys.platform != "win32":
        return
    root.update()                        # make sure the window exists before asking for it
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi
    user32.GetParent.restype = ctypes.c_void_p
    user32.GetParent.argtypes = [ctypes.c_void_p]
    frame = user32.GetParent(root.winfo_id())

    def setAttribute(attribute, value):
        data = ctypes.c_int(value)
        # Older Windows versions don't know every attribute and return an error code.
        dwmapi.DwmSetWindowAttribute(ctypes.c_void_p(frame), attribute,
                                     ctypes.byref(data), ctypes.sizeof(data))

    setAttribute(DWMWA_USE_IMMERSIVE_DARK_MODE, 1 if dark else 0)
    setAttribute(DWMWA_CAPTION_COLOR, colourRef(background))
    setAttribute(DWMWA_TEXT_COLOR, colourRef(text))


def loadFonts():
    if sys.platform != "win32":
        return False
    FR_PRIVATE = 0x10                    # the font is available only to this program
    loaded = True
    for name in FONT_FILES:
        path = os.path.abspath(os.path.join(FONT_DIR, name))
        if not os.path.exists(path) or ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0) == 0:
            loaded = False
    return loaded


def chooseFont(root, fontsLoaded):
    installed = set(tkfont.families(root))
    return PREFERRED_FONT if fontsLoaded or PREFERRED_FONT in installed else FALLBACK_FONT


def loadTheme(root):
    """Load the Sun Valley theme files. Returns False if they are not next to this program."""
    tclFile = os.path.join(HERE, THEME_DIR, "sun-valley.tcl")
    if not os.path.exists(tclFile):
        return False
    root.tk.call("source", tclFile.replace("\\", "/"))
    return True


def applyPalette(root, mode):
    """Switch the theme to light or dark, then set the app's font and text colours."""
    root.tk.call("set_theme", mode)

    # Every set_theme call resets the font to the theme's default, so the app font is set again here.
    style = ttk.Style(root)
    style.configure(".", font=(FONT, 10))
    style.configure("TButton", font=(FONT, 12))
    style.configure("Accent.TButton", font=(FONT, 12))

    colours = PALETTES[mode]
    style.configure(ROLE_STYLES["accent"], foreground=colours["accent"])


def makeLabel(parent, text="", size=12, weight="normal", role="text", **options):
    """A label in the theme's style, using the app font and the colour for this role."""
    return ttk.Label(parent, text=text, font=(FONT, size, weight),
                     style=ROLE_STYLES[role], **options)


def setEnabled(button, enabled):
    """Grey a button out when it is not available."""
    button.config(state="normal" if enabled else "disabled")


def loadJokes(path):
    jokes = []
    # UTF-8 is specified so characters such as the ellipsis in the file read correctly.
    with open(path, encoding="utf-8") as file:
        for line in file:
            # partition splits on the FIRST '?' only, so a '?' in the punchline is kept.
            setup, mark, punchline = line.strip().partition("?")
            if mark and setup and punchline.strip():
                jokes.append((setup + "?", punchline.strip()))
    return jokes


def pickJoke(jokes, previous=None):
    """Choose a random joke, avoiding an immediate repeat of the previous one."""
    if len(jokes) == 1:
        return jokes[0]
    joke = random.choice(jokes)
    while joke == previous:
        joke = random.choice(jokes)
    return joke


class JokeTellerApp:
    """The window: the joke, its punchline, four buttons, and the dark mode switch at the bottom."""

    def __init__(self, root, jokes, mode="light"):
        self.root = root
        self.jokes = jokes
        self.currentJoke = None      # the (setup, punchline) pair on screen, or None
        self.punchlineShown = False
        self.mode = mode

        root.title("Alexa")

        # The switch sits in a row at the bottom, so it is always visible.
        self.header = ttk.Frame(root, padding=(20, 0, 20, 12))
        self.header.pack(side="bottom", fill="x")
        self.darkVar = tk.BooleanVar(root, value=(mode == "dark"))
        ttk.Checkbutton(self.header, text="Dark mode", style="Switch.TCheckbutton",
                        variable=self.darkVar, command=self.toggleTheme).pack(side="right")

        self.container = ttk.Frame(root, padding=20)
        self.container.pack(fill="both", expand=True)

        self.titleLabel = makeLabel(self.container, text="Alexa", size=22, weight="bold",
                                    anchor="w", justify="left")
        self.titleLabel.pack(fill="x", pady=(10, 0))

        self.setupLabel = makeLabel(self.container, text="Press the button to hear a joke!",
                                    size=15, wraplength=420, anchor="w", justify="left")
        self.setupLabel.pack(fill="x", pady=(8, 10))

        self.punchlineLabel = makeLabel(self.container, text="", size=15, weight="bold",
                                        role="accent", wraplength=420, anchor="w", justify="left")
        self.punchlineLabel.pack(fill="x", pady=(0, 20))

        buttons = ttk.Frame(self.container)
        buttons.pack()

        self.tellButton = ttk.Button(buttons, text="Tell me a joke", style="Accent.TButton",
                                     width=22, command=self.showNewJoke)
        self.punchlineButton = ttk.Button(buttons, text="Show Punchline", style="Accent.TButton",
                                          width=22, command=self.showPunchline)
        self.nextButton = ttk.Button(buttons, text="Next Joke", style="Accent.TButton",
                                     width=22, command=self.showNewJoke)
        self.quitButton = ttk.Button(buttons, text="Quit", width=22, command=root.destroy)

        # A 2 x 2 grid of buttons, all the same width.
        self.tellButton.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.punchlineButton.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        self.nextButton.grid(row=1, column=0, padx=6, pady=6, sticky="ew")
        self.quitButton.grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        buttons.columnconfigure(0, uniform="buttons")
        buttons.columnconfigure(1, uniform="buttons")

        self.updateButtons()
        self.styleWindow()

    def styleWindow(self):
        """Colour the title bar to match the current mode."""
        colours = PALETTES[self.mode]
        styleTitleBar(self.root, colours["background"], colours["text"], dark=(self.mode == "dark"))

    def toggleTheme(self):
        """Switch between light and dark mode. The joke on screen stays as it is."""
        self.mode = "dark" if self.darkVar.get() else "light"
        applyPalette(self.root, self.mode)
        self.styleWindow()

    def showNewJoke(self):
        """Pick a joke, show its setup and hide any old punchline."""
        self.currentJoke = pickJoke(self.jokes, previous=self.currentJoke)
        self.setupLabel.config(text=self.currentJoke[0])
        self.punchlineLabel.config(text="")
        self.punchlineShown = False
        self.updateButtons()

    def showPunchline(self):
        """Reveal the punchline of the joke that is on screen."""
        self.punchlineLabel.config(text=self.currentJoke[1])
        self.punchlineShown = True
        self.updateButtons()

    def updateButtons(self):
        """Enable only the buttons that make sense in the current state."""
        hasJoke = self.currentJoke is not None
        setEnabled(self.tellButton, not hasJoke)
        setEnabled(self.punchlineButton, hasJoke and not self.punchlineShown)
        setEnabled(self.nextButton, hasJoke)


if __name__ == "__main__":
    fontsLoaded = loadFonts()
    root = tk.Tk()
    FONT = chooseFont(root, fontsLoaded)
    try:
        jokes = loadJokes(JOKES_FILE)
        if not jokes:
            raise ValueError("No jokes were found in randomJokes.txt.")
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load jokes", str(error))
        root.destroy()
    else:
        if not loadTheme(root):
            messagebox.showerror("Theme not found",
                                 "The Sun Valley theme files were not found. Put the "
                                 "'sun-valley' folder next to main.py and try again.")
            root.destroy()
        else:
            applyPalette(root, "light")
            JokeTellerApp(root, jokes)
            root.mainloop()
