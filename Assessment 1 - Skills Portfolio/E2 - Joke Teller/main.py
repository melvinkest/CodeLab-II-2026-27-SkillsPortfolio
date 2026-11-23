import ctypes
import os
import random
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

HERE = os.path.dirname(os.path.abspath(__file__))
JOKES_FILE = os.path.join(HERE, "..", "E2 - Joke Teller", "randomJokes.txt")

PREFERRED_FONT = "Inter"     # the font the app is designed for
FALLBACK_FONT = "Segoe UI"   # used when Inter is not installed
FONT = PREFERRED_FONT        # replaced at start-up with the font actually used

# Colors
BACKGROUND = "#ffffff"       # window background
KEY = "#f0f0f0"              # ordinary keys
KEY_HOVER = "#e2e2e2"        # an ordinary key under the mouse
ACCENT = "#0067c0"           # the blue action buttons and the punchline
ACCENT_HOVER = "#1975cc"     # the blue button under the mouse
ACCENT_TEXT = "#ffffff"      # white text on the blue buttons
TEXT = "#1a1a1a"
MUTED = "#6b6b6b"            # text on a disabled button

DWMWA_USE_IMMERSIVE_LIGHT_MODE = 20   
DWMWA_CAPTION_COLOR = 35             
DWMWA_TEXT_COLOR = 36                

def colourRef(hexColour):
    hexColour = hexColour.lstrip("#")
    red, green, blue = (int(hexColour[i:i + 2], 16) for i in (0, 2, 4))
    return red | (green << 8) | (blue << 16)


def styleTitleBar(root, background, text):
    if sys.platform != "win32":
        return
    root.update()                        
    user32 = ctypes.windll.user32
    dwmapi = ctypes.windll.dwmapi
    user32.GetParent.restype = ctypes.c_void_p
    user32.GetParent.argtypes = [ctypes.c_void_p]
    frame = user32.GetParent(root.winfo_id())

    def setAttribute(attribute, value):
        data = ctypes.c_int(value)
        dwmapi.DwmSetWindowAttribute(ctypes.c_void_p(frame), attribute,
                                     ctypes.byref(data), ctypes.sizeof(data))

    setAttribute(DWMWA_USE_IMMERSIVE_LIGHT_MODE, 0)       
    setAttribute(DWMWA_CAPTION_COLOR, colourRef(background))
    setAttribute(DWMWA_TEXT_COLOR, colourRef(text))


def chooseFont(root):
    installed = set(tkfont.families(root))
    return PREFERRED_FONT if PREFERRED_FONT in installed else FALLBACK_FONT


def loadJokes(path):
    jokes = []
    with open(path, encoding="utf-8") as file:
        for line in file:
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


def roundedRectPoints(x1, y1, x2, y2, radius):
    """Corner points for a rounded rectangle, drawn as a smooth polygon on a Canvas."""
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


def makeLabel(parent, text="", size=12, weight="normal", fg=TEXT, **options):
    return tk.Label(parent, text=text, font=(FONT, size, weight),
                    bg=BACKGROUND, fg=fg, **options)


def keyStyle(style):
    if style == "accent":
        return ACCENT, ACCENT_HOVER, ACCENT_TEXT
    return KEY, KEY_HOVER, TEXT


class RoundedButton(tk.Canvas):
    """A button drawn on a Canvas, so its corners can be rounded."""

    def __init__(self, parent, text, command, style="key", size=13, radius=12,
                 height=44, **options):
        normal, hover, textColour = keyStyle(style)
        super().__init__(parent, height=height, bg=BACKGROUND, bd=0,
                         highlightthickness=0, cursor="hand2", **options)
        self.buttonText = text
        self.command = command
        self.radius = radius
        self.normalColour, self.hoverColour, self.textColour = normal, hover, textColour
        self.fillColour = normal
        self.enabled = True
        self.shape = self.create_polygon(0, 0, 0, 0, smooth=True, splinesteps=24,
                                         fill=normal, outline=normal)
        self.label = self.create_text(0, 0, text=text, fill=textColour, font=(FONT, size))
        self.bind("<Configure>", self.redraw)
        self.bind("<Enter>", self.onEnter)
        self.bind("<Leave>", self.onLeave)
        self.bind("<Button-1>", self.onClick)

    def redraw(self, event=None):
        width, height = self.winfo_width(), self.winfo_height()
        self.coords(self.shape, *roundedRectPoints(1, 1, width - 1, height - 1, self.radius))
        self.coords(self.label, width / 2, height / 2)

    def paint(self, colour):
        self.fillColour = colour
        self.itemconfig(self.shape, fill=colour, outline=colour)

    def onEnter(self, event):
        if self.enabled:
            self.paint(self.hoverColour)

    def onLeave(self, event):
        if self.enabled:
            self.paint(self.normalColour)

    def onClick(self, event):
        self.invoke()

    def invoke(self):
        if self.enabled and self.command:
            self.command()

    def setEnabled(self, enabled):
        self.enabled = enabled
        self.paint(self.normalColour if enabled else KEY)
        self.itemconfig(self.label, fill=self.textColour if enabled else MUTED)


def makeKey(parent, text, command, style="key", size=13, **options):
    """A rounded button that darkens slightly under the mouse."""
    return RoundedButton(parent, text, command, style=style, size=size, **options)


class JokeTellerApp:

    def __init__(self, root, jokes):
        self.root = root
        self.jokes = jokes
        self.currentJoke = None      
        self.punchlineShown = False

        root.title("Alexa tell me a Joke")
        root.configure(bg=BACKGROUND)

        self.setupLabel = makeLabel(root, text="Press the button to hear a joke!", size=15,
                                    wraplength=420, justify="center")
        self.setupLabel.pack(padx=20, pady=(25, 10))

        self.punchlineLabel = makeLabel(root, text="", size=15, weight="bold", fg=ACCENT,
                                        wraplength=420, justify="center")
        self.punchlineLabel.pack(padx=20, pady=(0, 20))

        buttons = tk.Frame(root, bg=BACKGROUND)
        buttons.pack(pady=(0, 20))

        self.tellButton = makeKey(buttons, "Alexa tell me a Joke", self.showNewJoke,
                                  style="accent", width=200)
        self.punchlineButton = makeKey(buttons, "Show Punchline", self.showPunchline,
                                       style="accent", width=200)
        self.nextButton = makeKey(buttons, "Next Joke", self.showNewJoke,
                                  style="accent", width=200)
        self.quitButton = makeKey(buttons, "Quit", root.destroy, width=200)

        self.tellButton.grid(row=0, column=0, padx=6, pady=6)
        self.punchlineButton.grid(row=0, column=1, padx=6, pady=6)
        self.nextButton.grid(row=1, column=0, padx=6, pady=6)
        self.quitButton.grid(row=1, column=1, padx=6, pady=6)

        self.updateButtons()
        styleTitleBar(root, BACKGROUND, TEXT)

    def showNewJoke(self):
        self.currentJoke = pickJoke(self.jokes, previous=self.currentJoke)
        self.setupLabel.config(text=self.currentJoke[0])
        self.punchlineLabel.config(text="")
        self.punchlineShown = False
        self.updateButtons()

    def showPunchline(self):
        self.punchlineLabel.config(text=self.currentJoke[1])
        self.punchlineShown = True
        self.updateButtons()

    def updateButtons(self):
        hasJoke = self.currentJoke is not None
        self.tellButton.setEnabled(not hasJoke)
        self.punchlineButton.setEnabled(hasJoke and not self.punchlineShown)
        self.nextButton.setEnabled(hasJoke)


if __name__ == "__main__":
    root = tk.Tk()
    FONT = chooseFont(root)
    try:
        jokes = loadJokes(JOKES_FILE)
        if not jokes:
            raise ValueError("No jokes were found in randomJokes.txt.")
    except (OSError, ValueError) as error:
        messagebox.showerror("Could not load jokes", str(error))
        root.destroy()
    else:
        JokeTellerApp(root, jokes)
        root.mainloop()