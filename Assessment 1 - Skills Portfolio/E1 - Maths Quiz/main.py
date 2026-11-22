import ctypes
import random
import sys
import tkinter as tk
import tkinter.font as tkfont

QUESTIONS_PER_QUIZ = 10
FIRST_ATTEMPT_POINTS = 10
SECOND_ATTEMPT_POINTS = 5
MAX_SCORE = QUESTIONS_PER_QUIZ * FIRST_ATTEMPT_POINTS   

DIFFICULTY_LEVELS = {
    1: ("Easy", 1, 9),              # single-digit numbers
    2: ("Medium", 10, 99),          # double-digit numbers
    3: ("Hard", 1000, 9999),        # four-digit numbers
}

PREFERRED_FONT = "Inter"     # the font the quiz is designed for
FALLBACK_FONT = "Segoe UI"   # used when Inter is not installed
FONT = PREFERRED_FONT        # replaced at start-up with the font actually used

# Colours
BACKGROUND = "#ffffff"       # window and display area
KEY = "#f0f0f0"              # ordinary keys
KEY_HOVER = "#e2e2e2"        # an ordinary key under the mouse
ACCENT = "#0067c0"           # the blue action key (Submit, Next, Yes) and the grade
ACCENT_HOVER = "#1975cc"     # the blue key under the mouse
ACCENT_TEXT = "#ffffff"      # white text on the blue key
TEXT = "#1a1a1a"
MUTED = "#6b6b6b"            # secondary text, such as the score line
GOOD = "#107c10"             # feedback for a correct answer
BAD = "#c42b1c"              # feedback for a wrong answer
WARNING = "#9d5d00"          # feedback for invalid input
INPUT_FILL = "#ffffff"       # text box background
INPUT_BORDER = "#b0b0b0"     # text box outline when not focused

# The window icon as PNG images at 16, 32 and 64 pixels.
ICON_PNG = {
    16: "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAB+klEQVR4nKWSsUtVYRjGf+93ztX0qlREpURTDRUYRETQoA1GJjQEFgTl1NZY0XaJhrb+haDVoTVCKA2dGqJQoqBJixC9cq73XM/5zvmehrxWYDr0wrc8fO+Ph/d54D/HthNVk7NHFuYndL/TuLmaEuWeyOco8yQuQLLBbOjn4baA9sxPaCmCImmx5D0u80Sh4GwsWF5nI805Eu/iL1GggVgEnIm4CAyWgQ6gDrAjwESMUcf4LhFtak+zwADG2BZANTlOYUz+WnxzEhteQJ+MUI24lIgR5zAZvoRGxejNYd0ZfscbfLylE9WIseUmnb5Aec5wb8TISsrnZs7dazNM2aaDo8QcW1tFWcneosS3PM0eSN/WeXd90so2dOqyptOM9OprG60NKTbV1F2I93GF40UL6k1ebeQc2uM4bQG+JcytLjLU6iK68tKy54OqHj7IwNo+vo5PEmJ66SZhf5kTUs8PiQUHL1LPE5X0IQ5cnLYCKEB2+4M1gS9tR44cAb4MuK6YfnNcKMW5joi+UpiM7M9chKyGXFuJyTCg6gx8QCYiZ4wCruLARM/f1TAB+u0AEoM5c+ReBDPOYHS0CtaARDCzFfX2XZGjBq2c2c4K51cSbjQC0zShKxAGntnyTlGjcUUAjQd6XL+nOzt+/icEbRVK44okWfvttvsTZSH45eF4P/gAAAAASUVORK5CYII=",
    32: "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAFD0lEQVR4nK2WXYhdVxXHf2vvc8+dzCQz8SONFaki+PFQ0GAftAgzJZgGRIrFKIit0gctfQloTEXQk/so0oc8GuxjI5i3qg9q00n03Q+Q0OpDi1JiMm06M5l7595z9tp/H86dybTNNZk7+cNhcz7WWf+9Pv5rG3vA8qIKloBLu7Nbuowbpr34vmewaYyEDMGVb/N0GfjcxghLGfMM2cEdPEMar+6QHZEhwxspcvbxi/aWkBW7db68qMIuW3rlKZ2+fz8/W92EuXLs1CEZeBjfB1CGHCBFaBJ0Da71+XyFjlPBrgms3EebO+NLN2u83xBnC5CBAsRMG1drn602yB0fR0L9jMn4wscWmbeere6awDbEqIxEwZW1mj8oYUkoebvrOoFEB/FkNA44LXEzDKMpvU3/9ASAoq2gq5Z5KUEQZARuQABPdDG+amIWyCYCEBG2VX1TE8hQ9BuY63D0/fs5mtKtgktb9ZBhdbONxkwgDoBhetcmpiVgIncjrIz41/qQP3nbBUpt6EkJXOBOdCekTHbnkx3j4drY1oDpCYB3IgCvuTif1aYgGkrjFChByOCZaMIRx4vIwxJ5zynA6G7UeDSOHexybLvnw3ilbT+Pt/Rg2MCgIRt0BmnKIjx0vTWU+PdCl3izhkG6JT5ba53IyfHshG1hytiBDuGGc2NhnY2phGjpEi6T/S1TrWxyf2E8OGzDbJ4hqV0Fh2cKOhtOxghmKMBg6LwaxKmvXbFalcK2FAsZFfFOBC4BB65iD52zBuDqtzT3SsS33ncH2Jub2HzBR9XwQmkcWR0ymot01xpOPfayPbfzf1PNgrvFS1/RYUv8GfEJMmkj8fRjL9vz/zih8sELVgMUkszMpEozbjyRMx8e1pDbfJo7noVlR7VjSgQXyo6CYf0Rf/3MC/ZiVSmc6Y3VDlheJD7yG7v226M6XkYuH+rykX5DDbBynbwdAVUK9FCu+FU4wDfYBHJ7KYFFILX3dQP9Mbk0FhwTXB/wvSPn7ZxOKNoF207Hr08ofv2C+YuL+vT+GR5tMr989I/Wb6eEbZNFZzXvb/NGhJnNGrljnsmlUQwbfi/xw/6ID0bjecQDmw3yREiZNBspV0dcPHLejm053JmGCoUelpmAALB2gwLRIAqgwIhFoJPE+to8j9fOj8sOnx0lnpkp6AgiRoHREQSMNMlBD8tVpbC8qPHMvA2BhZmd42E8TQ1Lju1b5bkPHeSbWXy8gbWtb95xntL/L+Zez/Ijly1xm2PYJB2wpp3rC4fneebNdX5Xwk8WSi7WjhB2r9onTHoxdtDgeMr8YtM5fWiWhwYNbjbZbrfYGYH3nlJF3KgJwMkAD6wMyGZEvftLu43tXaLdyRCz9jfvrFZDZYRg/F3Ga2XAgKx24gqQRDbdWUEnoVBbmQNgSJeDJLZOdQBxfUQWnIxG3EwQjYiBGSQR93ex9Zq34Nag2l0EThCsZ0OJk9n5Twjtzmi3msuCUEaii0ESAxcDzwyS6HcC/beH/CUYPSFbWmJiv09CK0TIDNPVH2juffs4VUbOrA8YzUS6g5rXRw1PNTX/BOg3Lbl9BZoF7jvHf2/XXruGKpUAG8/qOzqjZuNZ5f5pXVs5qU/dybaqNHVX7DTMQkYgMksRjJuDmi8fOmuv6rvqCFlVKUiynRfIer3JUnvXGBcjaz/SB5qf6uc3vq8vAixX2tPRfW+k9hDau8V72mbHySjbvQjtHfA/7MrNN81eU9gAAAAASUVORK5CYII=",
    64: "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",
}


def setIcon(root):
    """Set the window icon.

    The images are returned so the caller can keep references to them;
    otherwise Tkinter discards them and the icon disappears.
    """
    images = [tk.PhotoImage(data=data) for data in ICON_PNG.values()]
    root.iconphoto(False, *images)
    return images


DWMWA_USE_IMMERSIVE_DARK_MODE = 20   
DWMWA_CAPTION_COLOR = 35             
DWMWA_TEXT_COLOR = 36                


def colourRef(hexColour):
    """Convert '#RRGGBB' into the 0x00BBGGRR number that Windows expects."""
    hexColour = hexColour.lstrip("#")
    red, green, blue = (int(hexColour[i:i + 2], 16) for i in (0, 2, 4))
    return red | (green << 8) | (blue << 16)


def styleTitleBar(root, background, text):
    """Colour the Windows title bar to match the app. Does nothing on other systems."""
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

    setAttribute(DWMWA_USE_IMMERSIVE_DARK_MODE, 0)       # always a light title bar
    setAttribute(DWMWA_CAPTION_COLOR, colourRef(background))
    setAttribute(DWMWA_TEXT_COLOR, colourRef(text))


def chooseFont(root):
    """Return Inter if it is installed on this computer, otherwise the fallback font.

    Tkinter silently substitutes another font for a missing one, so the check
    is made here, where the choice stays predictable.
    """
    installed = set(tkfont.families(root))
    return PREFERRED_FONT if PREFERRED_FONT in installed else FALLBACK_FONT


def randomInt(level):
    """Return a random whole number with the number of digits for this level."""
    _, low, high = DIFFICULTY_LEVELS[level]
    return random.randint(low, high)


def decideOperation():
    """Return '+' for an addition question or '-' for a subtraction question."""
    return random.choice(["+", "-"])


def getGrade(score):
    """Convert a score out of 100 into a letter grade."""
    if score > 90:
        return "A+"
    if score >= 80:
        return "A"
    if score >= 70:
        return "B"
    if score >= 60:
        return "C"
    if score >= 50:
        return "D"
    return "F"


def roundedRectPoints(x1, y1, x2, y2, radius):
    """Corner points for a rounded rectangle, drawn as a smooth polygon on a Canvas."""
    r = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]


def makeLabel(parent, text="", size=12, weight="normal", fg=TEXT, **options):
    """A label that sits on the background."""
    return tk.Label(parent, text=text, font=(FONT, size, weight),
                    bg=BACKGROUND, fg=fg, **options)


def keyStyle(style):
    """Return (normal colour, colour under the mouse, text colour) for a key style."""
    if style == "accent":
        return ACCENT, ACCENT_HOVER, ACCENT_TEXT
    return KEY, KEY_HOVER, TEXT


class RoundedButton(tk.Canvas):
    """A button drawn on a Canvas, so its corners can be rounded."""

    def __init__(self, parent, text, command, style="key", size=13, radius=12, height=44):
        normal, hover, textColour = keyStyle(style)
        super().__init__(parent, height=height, bg=BACKGROUND, bd=0,
                         highlightthickness=0, cursor="hand2")
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
        """Fit the rounded shape and the text to the current size."""
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
        """Run the button's command, as clicking a Tkinter button does."""
        if self.enabled and self.command:
            self.command()

    def setEnabled(self, enabled):
        """Grey the button out when it is unavailable, like a disabled calculator key."""
        self.enabled = enabled
        self.paint(self.normalColour if enabled else KEY)
        self.itemconfig(self.label, fill=self.textColour if enabled else MUTED)


class RoundedEntry(tk.Canvas):
    """A text box drawn on a Canvas, with rounded corners and an accent outline when focused."""

    def __init__(self, parent, size=20, radius=12, height=60):
        super().__init__(parent, height=height, bg=BACKGROUND, bd=0, highlightthickness=0)
        self.radius = radius
        self.insetX, self.insetY = 12, 10            # keeps the text clear of the rounded corners
        self.box = self.create_polygon(0, 0, 0, 0, smooth=True, splinesteps=24,
                                       fill=INPUT_FILL, outline=INPUT_BORDER, width=1)
        self.entry = tk.Entry(self, font=(FONT, size), bd=0, relief="flat",
                              highlightthickness=0, bg=INPUT_FILL, fg=TEXT,
                              insertbackground=TEXT, justify="right",
                              disabledbackground=INPUT_FILL, disabledforeground=TEXT)
        self.window = self.create_window(self.insetX, self.insetY, window=self.entry,
                                         anchor="nw")
        self.entry.bind("<FocusIn>", self.onFocusIn)
        self.entry.bind("<FocusOut>", self.onFocusOut)
        self.bind("<Configure>", self.redraw)

    def redraw(self, event=None):
        """Fit the rounded box and the text field to the current size."""
        width, height = self.winfo_width(), self.winfo_height()
        self.coords(self.box, *roundedRectPoints(1, 1, width - 1, height - 1, self.radius))
        self.itemconfig(self.window, width=width - 2 * self.insetX,
                        height=height - 2 * self.insetY)

    def onFocusIn(self, event):
        self.itemconfig(self.box, outline=ACCENT, width=2)

    def onFocusOut(self, event):
        self.itemconfig(self.box, outline=INPUT_BORDER, width=1)

    def focus_set(self):
        self.entry.focus_set()

    def get(self):
        return self.entry.get()

    def setText(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    def clear(self):
        self.entry.delete(0, tk.END)

    def setEnabled(self, enabled):
        self.entry.config(state="normal" if enabled else "disabled")


def makeKey(parent, text, command, style="key", size=13):
    """A rounded, calculator-style button that darkens slightly under the mouse."""
    return RoundedButton(parent, text, command, style=style, size=size)


def disableKey(button):
    """Grey a key out so it looks unavailable, like a disabled calculator key."""
    button.setEnabled(False)


class MathsQuizApp:
    def __init__(self, root):
        self.root = root
        root.title("Maths Quiz")
        root.minsize(380, 480)
        root.configure(bg=BACKGROUND)

        self.container = tk.Frame(root, padx=20, pady=20, bg=BACKGROUND)
        self.container.pack(fill="both", expand=True)

        self.level = 1
        self.score = 0
        self.questionNumber = 0
        self.attempt = 1
        self.problemText = ""
        self.correctAnswer = 0
        self.questionAnswered = False

        self.displayMenu()

        self.icons = setIcon(root)                  
        styleTitleBar(root, BACKGROUND, TEXT)

    def clearScreen(self):
        """Remove every widget from the container so a new screen can be drawn."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def displayMenu(self):
        """Show the difficulty menu (at start-up, and after 'Yes' to play again)."""
        self.clearScreen()
        makeLabel(self.container, text="Difficulty Level", size=18,
                  weight="bold").pack(fill="x", pady=(10, 0))
        makeLabel(self.container, text="Select an option", size=12,
                  fg=MUTED).pack(fill="x", pady=(4, 20))
        for level, (name, _, _) in DIFFICULTY_LEVELS.items():
            makeKey(self.container, name,
                    lambda lvl=level: self.startQuiz(lvl)).pack(fill="x", pady=4)

    def startQuiz(self, level):
        """Reset the score and counters, then ask the first question."""
        self.level = level
        self.score = 0
        self.questionNumber = 0
        self.nextQuestion()

    def nextQuestion(self):
        """Create the next problem, or show the results once all questions are done."""
        self.questionNumber += 1
        if self.questionNumber > QUESTIONS_PER_QUIZ:
            self.displayResults(self.score)
            return

        num1 = randomInt(self.level)
        num2 = randomInt(self.level)
        operation = decideOperation()
        self.problemText = f"{num1} {operation} {num2} ="
        self.correctAnswer = num1 + num2 if operation == "+" else num1 - num2
        self.attempt = 1
        self.displayProblem()

    def displayProblem(self):
        """Draw the current question and the answer box."""
        self.clearScreen()
        self.questionAnswered = False

        self.scoreLabel = makeLabel(self.container, size=10, fg=MUTED, anchor="w")
        self.scoreLabel.pack(fill="x")
        self.updateScoreLabel()

        makeLabel(self.container, text=self.problemText, size=32, weight="bold",
                  anchor="e").pack(fill="x", pady=(30, 10))

        self.answerEntry = RoundedEntry(self.container)
        self.answerEntry.pack(fill="x", pady=(0, 10))
        self.answerEntry.focus_set()
        self.answerEntry.entry.bind("<Return>", lambda event: self.submitAnswer())

        self.submitButton = makeKey(self.container, "Submit", self.submitAnswer, style="accent")
        self.submitButton.pack(fill="x", pady=(0, 10))

        self.feedbackLabel = makeLabel(self.container, size=12, height=2)
        self.feedbackLabel.pack(fill="x")

        nextText = "See Results" if self.questionNumber == QUESTIONS_PER_QUIZ else "Next Question"
        self.nextButton = makeKey(self.container, nextText, self.nextQuestion, style="accent")

    def updateScoreLabel(self):
        self.scoreLabel.config(
            text=f"Question {self.questionNumber} of {QUESTIONS_PER_QUIZ}     Score: {self.score}")

    def submitAnswer(self):
        """Read the typed answer and decide what happens next."""
        if self.questionAnswered:
            return

        text = self.answerEntry.get().strip()
        try:
            userAnswer = int(text)
        except ValueError:
            self.feedbackLabel.config(text="Please type a whole number.", fg=WARNING)
            return

        if self.isCorrect(userAnswer) or self.attempt == 2:
            self.finishQuestion()
        else:
            self.attempt = 2
            self.answerEntry.clear()
            self.answerEntry.focus_set()

    def isCorrect(self, userAnswer):
        """Check the answer, award points and show a message. Returns True if correct."""
        if userAnswer == self.correctAnswer:
            points = FIRST_ATTEMPT_POINTS if self.attempt == 1 else SECOND_ATTEMPT_POINTS
            self.score += points
            self.updateScoreLabel()
            self.feedbackLabel.config(text=f"Correct! +{points} points", fg=GOOD)
            return True

        if self.attempt == 1:
            self.feedbackLabel.config(text="Not quite. You have one more try!", fg=BAD)
        else:
            self.feedbackLabel.config(
                text=f"Incorrect. The answer was {self.correctAnswer}.", fg=BAD)
        return False

    def finishQuestion(self):
        """Lock the answer box and show the Next button."""
        self.questionAnswered = True
        self.answerEntry.setEnabled(False)
        disableKey(self.submitButton)
        self.nextButton.pack(fill="x", pady=(5, 0))

    def displayResults(self, finalScore):
        """Show the final score, the grade, and ask whether to play again."""
        self.clearScreen()
        grade = getGrade(finalScore)

        makeLabel(self.container, text="Quiz Complete", size=20,
                  weight="bold").pack(fill="x", pady=(10, 0))
        makeLabel(self.container, text=f"Final score: {finalScore} / {MAX_SCORE}",
                  size=16, fg=MUTED).pack(fill="x", pady=5)
        makeLabel(self.container, text=f"Grade: {grade}", size=28, weight="bold",
                  fg=ACCENT).pack(fill="x", pady=15)
        makeLabel(self.container, text="Would you like to play again?",
                  size=12).pack(fill="x", pady=(15, 8))

        buttons = tk.Frame(self.container, bg=BACKGROUND)
        buttons.pack(fill="x")
        makeKey(buttons, "Yes", self.displayMenu, style="accent").pack(
            side="left", fill="x", expand=True, padx=(0, 4))
        makeKey(buttons, "No", self.root.destroy).pack(
            side="left", fill="x", expand=True, padx=(4, 0))


if __name__ == "__main__":
    root = tk.Tk()
    FONT = chooseFont(root)
    MathsQuizApp(root)
    root.mainloop()