import ctypes
import os
import random
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, ttk

HERE = os.path.dirname(os.path.abspath(__file__))

QUESTIONS_PER_QUIZ = 10
FIRST_ATTEMPT_POINTS = 10
SECOND_ATTEMPT_POINTS = 5
MAX_SCORE = QUESTIONS_PER_QUIZ * FIRST_ATTEMPT_POINTS

# level number -> (name, smallest value, largest value)
DIFFICULTY_LEVELS = {
    1: ("Easy", 1, 9),
    2: ("Medium", 10, 99),
    3: ("Hard", 1000, 9999),
    4: ("Extreme", 10000, 99999),           
}

# Seconds allowed for each question (both attempts share the same time).
TIME_LIMITS = {1: 10, 2: 15, 3: 20, 4: 30}  # seconds

# The second number in × and the divisor in ÷ are whole numbers in this range.
MULTIPLIER_RANGE = (2, 12)

PREFERRED_FONT = "Google Sans"  # the font the quiz is designed for
FALLBACK_FONT = "Segoe UI"      # used if Google Sans cannot be loaded or installed
FONT = PREFERRED_FONT        # replaced at start-up with the font actually used

# The Sun Valley theme: its folder name. The mode (light or dark) can be switched in the app.
THEME_DIR = "sun-valley"

# Colours for each mode.
PALETTES = {
    "light": {"background": "#fafafa", "text": "#202020", "muted": "#5c5c5c",
              "accent": "#2f60d8", "good": "#107c10", "bad": "#c42b1c", "warning": "#9d5d00"},
    "dark": {"background": "#1c1c1c", "text": "#ffffff", "muted": "#a0a0a0",
             "accent": "#60cdff", "good": "#6ccb5f", "bad": "#ff99a4", "warning": "#ffc857"},
}

# Text colours are ttk styles, so switching mode recolours every label at once.
ROLE_STYLES = {
    "text": "TLabel",
    "muted": "Muted.TLabel",
    "accent": "Accent.TLabel",
    "good": "Good.TLabel",
    "bad": "Bad.TLabel",
    "warning": "Warning.TLabel",
}

# The window icon as PNG images at 16, 32 and 64 pixels.
ICON_PNG = {
    16: "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAC+ElEQVR4nE2TT2jcVRzEP9/3e/tLdtOlMdH0YCyhRI0pVMVrEaT1pBBQt4qW2JYiHgVFDE26DVJaEA+CBykGBeu/5CBKTxYvntqTtkhtkSZtUkUa08Zskt3s7703HhLRgTnOzGFmDABkCDDTcP3GsPnyEVLcR4oPAOCyeTP7gZimfpm8/yqSYQAm93/xIxM3T5jLL5i5N53xWObozRy9zngc59+Ss4vDx29MYCbqJwxkVptWNlMjDR27/mWpet+LYXURR4qtAmsVyQR0lkzlkilZlvmuewmrt7/49eTgwdo0zgCGxq4cL23bMdlu3G5nRmmtnezBHR08MVDBGfw03+TqHxtUclMURV7ty9uNP8evnd590obeufIQ6DI47whutSXbv7vKh6M7KecOgHYQb3y+wLmfl6l2OiXzCaW2o7XHKbRftyzvUGihFC3FgsNP9lLOHZPf3OLtr+bJvXFobw+kgFI0FS0sy8sh2GteCvtVNEWKFgWVEox/PUc5z7h4vcHo3j4AVpqBFAMkQcK2NE97xdCfJCNF/sXCXwWNZuSZR3s49dIAi42C9767ibeIIkjJFGRKod+TApJA/xmUzKh2iA9eHaScO55//xKXbzbornhiLABhgGLEKxW3XOa6UwzCMAOCoOSMsz/+zuJKm0tzd+kue0IotnaHzHmUigVHiOcxMxREiihFlAJGZK0VCCFR9iKEACluUkGAofS9S0ofxdZKS4BSIVNkY6NNf0+JsecGOXVwiErOZroCioUExI3GulM6YwC7jp4b99t63y3W7rQNlczMYhJP7eljtRm4cG2J3DskCazwXT15WF8amz3z7GmjNp0xcyDtOvrt2ax8z8uxuYykCNhqK5gz6Or0kpA5l2Wd2wnrdz+bmxoZpTadOWZqiXrdZj8eeaVYuzMB9rfzeWbOue0Vb9WyN8w55/MMsRzWlo7NTY2MUq87Zg4k22rOkMBMA0emHzbLD4P2KcWdAObcvJk7TwifzH76wm+bdzYA/QPFipqcL1JO3QAAAABJRU5ErkJggg==",
    32: "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",
    64: "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",
}


def setIcon(root):
    """Set the window icon."""
    images = [tk.PhotoImage(data=data) for data in ICON_PNG.values()]
    root.iconphoto(False, *images)
    return images


# Windows draws the title bar through the Desktop Window Manager (DWM).
DWMWA_USE_IMMERSIVE_DARK_MODE = 20   # dark title bar 
DWMWA_CAPTION_COLOR = 35             # title bar colour 
DWMWA_TEXT_COLOR = 36                # title text colour


def colourRef(hexColour):
    hexColour = hexColour.lstrip("#")
    red, green, blue = (int(hexColour[i:i + 2], 16) for i in (0, 2, 4))
    return red | (green << 8) | (blue << 16)


def styleTitleBar(root, background, text, dark):
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


FONT_DIR = os.path.join(HERE, "fonts")
FONT_FILES = ["GoogleSans-Regular.ttf", "GoogleSans-Bold.ttf"]

# A question must fit the window's width; its text is made smaller when it would not.
QUESTION_MAX_WIDTH = 340     # pixels available for a question
QUESTION_SIZE = 32           # the largest size for a question, in points
QUESTION_MIN_SIZE = 18       # the smallest size for a question, in points


def loadFonts():
    if sys.platform != "win32":
        return False
    FR_PRIVATE = 0x10                    
    loaded = True
    for name in FONT_FILES:
        path = os.path.abspath(os.path.join(FONT_DIR, name))
        if not os.path.exists(path) or ctypes.windll.gdi32.AddFontResourceExW(path, FR_PRIVATE, 0) == 0:
            loaded = False
    return loaded


def chooseFont(root, fontsLoaded):
    installed = set(tkfont.families(root))
    return PREFERRED_FONT if fontsLoaded or PREFERRED_FONT in installed else FALLBACK_FONT


def fitQuestionSize(root, text):
    for size in range(QUESTION_SIZE, QUESTION_MIN_SIZE - 1, -2):
        measured = tkfont.Font(root=root, family=FONT, size=size, weight="bold").measure(text)
        if measured <= QUESTION_MAX_WIDTH:
            return size
    return QUESTION_MIN_SIZE


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

    style = ttk.Style(root)
    style.configure(".", font=(FONT, 10))
    style.configure("TButton", font=(FONT, 12))
    style.configure("Accent.TButton", font=(FONT, 12))

    colours = PALETTES[mode]
    for role, styleName in ROLE_STYLES.items():
        if role != "text":
            style.configure(styleName, foreground=colours[role])


def randomInt(level):
    """Return a random whole number with the number of digits for this level."""
    _, low, high = DIFFICULTY_LEVELS[level]
    return random.randint(low, high)


def operationsFor(level):
    """Easy uses addition and subtraction; Medium and above also use multiplication and division."""
    return ["+", "-"] if level == 1 else ["+", "-", "×", "÷"]


def makeQuestion(level):
    """Return (first number, operation, second number, correct answer) for one question."""
    operation = random.choice(operationsFor(level))
    if operation == "×":
        first, second = randomInt(level), random.randint(*MULTIPLIER_RANGE)
        return first, operation, second, first * second
    if operation == "÷":
        # Choose the whole-number answer so that the dividend, which is shown, stays within
        # the level's digits. Then the division always comes out exact.
        divisor = random.randint(*MULTIPLIER_RANGE)
        _, low, high = DIFFICULTY_LEVELS[level]
        answer = random.randint(-(-low // divisor), high // divisor)     # -(-x // d) is ceil(x / d)
        return answer * divisor, operation, divisor, answer
    first, second = randomInt(level), randomInt(level)
    answer = first + second if operation == "+" else first - second
    return first, operation, second, answer


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


def makeLabel(parent, text="", size=12, weight="normal", role="text", **options):
    return ttk.Label(parent, text=text, font=(FONT, size, weight),
                     style=ROLE_STYLES[role], **options)


class MathsQuizApp:
    def __init__(self, root, mode="light"):
        self.root = root
        root.title("Quiz")
        root.minsize(380, 480)
        self.mode = mode
        self.timerId = None

        self.header = ttk.Frame(root, padding=(20, 0, 20, 12))
        self.header.pack(side="bottom", fill="x")
        self.darkVar = tk.BooleanVar(root, value=(mode == "dark"))
        ttk.Checkbutton(self.header, text="Dark mode", style="Switch.TCheckbutton",
                        variable=self.darkVar, command=self.toggleTheme).pack(side="right")

        self.container = ttk.Frame(root, padding=20)
        self.container.pack(fill="both", expand=True)

        self.level = 1
        self.score = 0
        self.questionNumber = 0
        self.attempt = 1
        self.problemText = ""
        self.correctAnswer = 0
        self.questionAnswered = False
        self.timeLimit = TIME_LIMITS[1]
        self.timeLeft = self.timeLimit

        self.displayMenu()

        self.icons = setIcon(root)                   
        colours = PALETTES[mode]
        styleTitleBar(root, colours["background"], colours["text"], dark=(mode == "dark"))

    def toggleTheme(self):
        """Switch between light and dark mode. The current screen and any timer carry on."""
        self.mode = "dark" if self.darkVar.get() else "light"
        applyPalette(self.root, self.mode)
        colours = PALETTES[self.mode]
        styleTitleBar(self.root, colours["background"], colours["text"], dark=(self.mode == "dark"))

    def clearScreen(self):
        """Remove every widget from the container so a new screen can be drawn."""
        for widget in self.container.winfo_children():
            widget.destroy()

    def cancelTimer(self):
        """Stop the countdown for the current question, if one is running."""
        if self.timerId is not None:
            self.root.after_cancel(self.timerId)
            self.timerId = None

    def displayMenu(self):
        """Show the difficulty menu (at start-up, and after 'Yes' to play again)."""
        self.cancelTimer()
        self.clearScreen()
        makeLabel(self.container, text="Difficulty Level", size=18,
                  weight="bold").pack(fill="x", pady=(10, 0))
        makeLabel(self.container, text="Select an option", size=12,
                  role="muted").pack(fill="x", pady=(4, 20))
        for level, (name, _, _) in DIFFICULTY_LEVELS.items():
            ttk.Button(self.container, text=name,
                       command=lambda lvl=level: self.startQuiz(lvl)).pack(fill="x", pady=4)

    def startQuiz(self, level):
        """Reset the score and counters, then ask the first question."""
        self.level = level
        self.timeLimit = TIME_LIMITS[level]
        self.score = 0
        self.questionNumber = 0
        self.nextQuestion()

    def nextQuestion(self):
        """Create the next problem, or show the results once all questions are done."""
        self.questionNumber += 1
        if self.questionNumber > QUESTIONS_PER_QUIZ:
            self.displayResults(self.score)
            return

        first, operation, second, answer = makeQuestion(self.level)
        self.problemText = f"{first} {operation} {second} ="
        self.correctAnswer = answer
        self.attempt = 1
        self.displayProblem()

    def displayProblem(self):
        """Draw the current question, its timer and the answer box."""
        self.clearScreen()
        self.questionAnswered = False

        row = ttk.Frame(self.container)
        row.pack(fill="x")
        self.scoreLabel = makeLabel(row, size=10, role="muted")
        self.scoreLabel.pack(side="left")
        self.timerLabel = makeLabel(row, size=10, role="muted")
        self.timerLabel.pack(side="right")
        self.updateScoreLabel()

        self.timeLeft = self.timeLimit
        self.timerBar = ttk.Progressbar(self.container, maximum=self.timeLimit, value=self.timeLeft)
        self.timerBar.pack(fill="x", pady=(6, 0))
        self.updateTimer()
        self.startTimer()

        questionSize = fitQuestionSize(self.root, self.problemText)
        makeLabel(self.container, text=self.problemText, size=questionSize, weight="bold",
                  anchor="e").pack(fill="x", pady=(24, 10))

        self.answerEntry = ttk.Entry(self.container, font=(FONT, 20), justify="right")
        self.answerEntry.pack(fill="x", pady=(0, 10), ipady=6)
        self.answerEntry.focus_set()
        self.answerEntry.bind("<Return>", lambda event: self.submitAnswer())

        self.submitButton = ttk.Button(self.container, text="Submit", style="Accent.TButton",
                                       command=self.submitAnswer)
        self.submitButton.pack(fill="x", pady=(0, 10))

        # The padding keeps room for the feedback message, so the layout does not jump.
        self.feedbackLabel = makeLabel(self.container, size=12, padding=(0, 12))
        self.feedbackLabel.pack(fill="x")

        nextText = "See Results" if self.questionNumber == QUESTIONS_PER_QUIZ else "Next Question"
        self.nextButton = ttk.Button(self.container, text=nextText, style="Accent.TButton",
                                     command=self.nextQuestion)

        # Packed last, so it sits at the bottom; the Next button is packed above it later.
        self.forfeitButton = ttk.Button(self.container, text="Forfeit quiz", command=self.forfeit)
        self.forfeitButton.pack(fill="x", pady=(10, 0))

    def updateScoreLabel(self):
        self.scoreLabel.config(
            text=f"Question {self.questionNumber} of {QUESTIONS_PER_QUIZ}     Score: {self.score}")

    def updateTimer(self):
        """Show the seconds left; the message turns red in the last five seconds."""
        role = "bad" if self.timeLeft <= 5 else "muted"
        self.timerLabel.config(text=f"Time left: {self.timeLeft}s", style=ROLE_STYLES[role])
        self.timerBar.config(value=self.timeLeft)

    def startTimer(self):
        """Start the countdown: one tick every second."""
        self.cancelTimer()
        self.timerId = self.root.after(1000, self.tick)

    def tick(self):
        self.timerId = None
        self.timeLeft -= 1
        self.updateTimer()
        if self.timeLeft <= 0:
            self.timeUp()
        else:
            self.timerId = self.root.after(1000, self.tick)

    def timeUp(self):
        """The time for this question has run out: show the answer and lock the question."""
        self.setFeedback(f"Time's up! The answer was {self.correctAnswer}.", "bad")
        self.finishQuestion()

    def setFeedback(self, text, role):
        self.feedbackLabel.config(text=text, style=ROLE_STYLES[role])

    def submitAnswer(self):
        """Read the typed answer and decide what happens next."""
        if self.questionAnswered:
            return

        text = self.answerEntry.get().strip()
        try:
            userAnswer = int(text)
        except ValueError:
            self.setFeedback("Please type a whole number.", "warning")
            return

        if self.isCorrect(userAnswer) or self.attempt == 2:
            self.finishQuestion()
        else:
            self.attempt = 2
            self.answerEntry.delete(0, tk.END)
            self.answerEntry.focus_set()

    def isCorrect(self, userAnswer):
        """Check the answer, award points and show a message. Returns True if correct."""
        if userAnswer == self.correctAnswer:
            points = FIRST_ATTEMPT_POINTS if self.attempt == 1 else SECOND_ATTEMPT_POINTS
            self.score += points
            self.updateScoreLabel()
            self.setFeedback(f"Correct! +{points} points", "good")
            return True

        if self.attempt == 1:
            self.setFeedback("Not quite. You have one more try!", "bad")
        else:
            self.setFeedback(f"Incorrect. The answer was {self.correctAnswer}.", "bad")
        return False

    def finishQuestion(self):
        """Stop the timer, lock the answer box and show the Next button."""
        self.cancelTimer()
        self.questionAnswered = True
        self.answerEntry.config(state="disabled")
        self.submitButton.config(state="disabled")
        self.nextButton.pack(fill="x", pady=(5, 0), before=self.forfeitButton)

    def forfeit(self):
        """Give up the quiz, keeping the points scored so far."""
        if messagebox.askyesno("Forfeit quiz", "Give up this quiz? Your score so far will be kept."):
            self.displayResults(self.score, forfeited=True)

    def displayResults(self, finalScore, forfeited=False):
        """Show the final score, the grade, and ask whether to play again."""
        self.cancelTimer()
        self.clearScreen()
        grade = getGrade(finalScore)

        makeLabel(self.container, text="Quiz Forfeited" if forfeited else "Quiz Complete",
                  size=20, weight="bold").pack(fill="x", pady=(10, 0))
        makeLabel(self.container, text=f"Final score: {finalScore} / {MAX_SCORE}",
                  size=16, role="muted").pack(fill="x", pady=5)
        makeLabel(self.container, text=f"Grade: {grade}", size=28, weight="bold",
                  role="accent").pack(fill="x", pady=15)
        makeLabel(self.container, text="Would you like to play again?",
                  size=12).pack(fill="x", pady=(15, 8))

        buttons = ttk.Frame(self.container)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Yes", style="Accent.TButton", command=self.displayMenu).pack(
            side="left", fill="x", expand=True, padx=(0, 4))
        ttk.Button(buttons, text="No", command=self.root.destroy).pack(
            side="left", fill="x", expand=True, padx=(4, 0))


if __name__ == "__main__":
    fontsLoaded = loadFonts()
    root = tk.Tk()
    FONT = chooseFont(root, fontsLoaded)
    if not loadTheme(root):
        messagebox.showerror("Theme not found",
                             "The Sun Valley theme files were not found. Put the "
                             "'sun-valley' folder next to main.py and try again.")
        root.destroy()
    else:
        applyPalette(root, "light")
        MathsQuizApp(root)
        root.mainloop()
