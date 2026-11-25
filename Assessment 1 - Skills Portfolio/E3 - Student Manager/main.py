import ctypes
import os
import sys
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox, simpledialog, ttk

# The data file sits in the shared resources folder. Building the path from this
# script's own location means the app works wherever Python is started from.
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "..", "E3 - Student Manager", "studentMarks.txt")

COURSEWORK_COUNT = 3
COURSEWORK_MAX = 20                                         # each coursework mark is out of 20
EXAM_MAX = 100
TOTAL_MAX = COURSEWORK_COUNT * COURSEWORK_MAX + EXAM_MAX    # 160 marks available in total
CODE_MIN = 1000
CODE_MAX = 9999

# Column layout shared by the header and every row of the results table.
ROW_FORMAT = "{:<22}{:>8}{:>13}{:>10}{:>12}{:>8}"
HEADER = ROW_FORMAT.format("Name", "Number", "Coursework", "Exam", "Overall", "Grade")

# The fields the update sub-menu offers, in the order they are numbered.
UPDATE_OPTIONS = [
    "Name",
    "Student number",
    "Coursework 1",
    "Coursework 2",
    "Coursework 3",
    "Exam mark",
]

PREFERRED_FONT = "Google Sans"  # the font the app is designed for
FALLBACK_FONT = "Segoe UI"      # used if Google Sans cannot be loaded or installed
MONO_PREFERRED = "Consolas"     # a monospaced font keeps the results table in columns
MONO_FALLBACK = "Courier New"
FONT = PREFERRED_FONT           # replaced at start-up with the font actually used
MONO_FONT = MONO_PREFERRED      # replaced at start-up with the font actually used

FONT_DIR = os.path.join(HERE, "fonts")
FONT_FILES = ["GoogleSans-Regular.ttf", "GoogleSans-Bold.ttf"]
THEME_DIR = "sun-valley"

# The colours of the results box for each mode, matching the Sun Valley palettes.
PALETTES = {
    "light": {"background": "#fafafa", "text": "#202020", "muted": "#5c5c5c"},
    "dark": {"background": "#1c1c1c", "text": "#ffffff", "muted": "#a0a0a0"},
}

# Windows draws the title bar through the Desktop Window Manager (DWM).
DWMWA_USE_IMMERSIVE_DARK_MODE = 20   
DWMWA_CAPTION_COLOR = 35             
DWMWA_TEXT_COLOR = 36                


def colourRef(hexColour):
    """Convert '#RRGGBB' into the 0x00BBGGRR number that Windows expects."""
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
        dwmapi.DwmSetWindowAttribute(ctypes.c_void_p(frame), attribute,
                                     ctypes.byref(data), ctypes.sizeof(data))

    setAttribute(DWMWA_USE_IMMERSIVE_DARK_MODE, 1 if dark else 0)
    setAttribute(DWMWA_CAPTION_COLOR, colourRef(background))
    setAttribute(DWMWA_TEXT_COLOR, colourRef(text))


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


def pickFont(root, preferred, fallback, loaded=False):

    installed = set(tkfont.families(root))
    return preferred if loaded or preferred in installed else fallback


def loadTheme(root):
    """Load the Sun Valley theme files. Returns False if they are not next to this program."""
    tclFile = os.path.join(HERE, THEME_DIR, "sun-valley.tcl")
    if not os.path.exists(tclFile):
        return False
    root.tk.call("source", tclFile.replace("\\", "/"))
    return True


def applyPalette(root, mode):
    """Switch the theme to light or dark, then set the app font on top of it."""
    root.tk.call("set_theme", mode)

    # Every set_theme call resets the font to the theme's default, so the app font is set again here.
    style = ttk.Style(root)
    style.configure(".", font=(FONT, 10))
    style.configure("TButton", font=(FONT, 12))
    style.configure("Muted.TLabel", foreground=PALETTES[mode]["muted"])


def makeLabel(parent, text="", size=12, weight="normal", **options):
    """A label in the theme's style, using the app font."""
    return ttk.Label(parent, text=text, font=(FONT, size, weight), **options)

class Student:
    """One record from the marks file."""

    def __init__(self, code, name, courseworkMarks, examMark):
        self.code = code
        self.name = name
        self.courseworkMarks = courseworkMarks    # a list of three integers
        self.examMark = examMark

    @property
    def courseworkTotal(self):
        return sum(self.courseworkMarks)

    @property
    def totalMark(self):
        """Coursework and exam marks added together (out of 160)."""
        return self.courseworkTotal + self.examMark

    @property
    def percentage(self):
        return self.totalMark / TOTAL_MAX * 100

    @property
    def grade(self):
        return getGrade(self.percentage)


def getGrade(percentage):
    """Turn an overall percentage into a letter grade."""
    if percentage >= 70:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 50:
        return "C"
    if percentage >= 40:
        return "D"
    return "F"

def loadStudents(path):

    with open(path, encoding="utf-8") as file:
        lines = [line.strip() for line in file if line.strip()]

    students = []
    for lineNumber, line in enumerate(lines[1:], start=2):
        try:
            code, name, cw1, cw2, cw3, exam = [part.strip() for part in line.split(",")]
            students.append(Student(int(code), name,
                                    [int(cw1), int(cw2), int(cw3)], int(exam)))
        except ValueError:
            raise ValueError(f"Line {lineNumber} of the data file is not in the expected format.")
    return students


def saveStudents(path, students):
    """Write the student count and every record back to the marks file."""
    with open(path, "w", encoding="utf-8") as file:
        file.write(f"{len(students)}\n")
        for student in students:
            marks = ",".join(str(mark) for mark in student.courseworkMarks)
            file.write(f"{student.code},{student.name},{marks},{student.examMark}\n")

def findStudents(students, query):
    """Return the students matching a student number, or else a part of a name."""
    query = query.strip()
    if not query:
        return []
    byNumber = [s for s in students if str(s.code) == query]
    if byNumber:
        return byNumber
    return [s for s in students if query.lower() in s.name.lower()]


def studentsWithHighestTotal(students):
    """Every student tied for the highest total mark (usually just one)."""
    best = max(s.totalMark for s in students)
    return [s for s in students if s.totalMark == best]


def studentsWithLowestTotal(students):
    """Every student tied for the lowest total mark (usually just one)."""
    worst = min(s.totalMark for s in students)
    return [s for s in students if s.totalMark == worst]


def sortStudents(students, ascending):
    """Return a new list sorted by overall mark. The file itself is not changed."""
    return sorted(students, key=lambda s: s.totalMark, reverse=not ascending)


def averagePercentage(students):
    return sum(s.percentage for s in students) / len(students)


def checkName(name):
    """Return an error message if the name cannot be stored, otherwise None."""
    if not name.strip():
        return "The name cannot be blank."
    if "," in name:
        return "The name cannot contain a comma, because commas separate the fields in the file."
    return None


def checkCodeAvailable(code, students, ignore=None):
    """Return an error message if another student already uses this number."""
    for student in students:
        if student is not ignore and student.code == code:
            return f"Student number {code} already belongs to {student.name}."
    return None

def formatRow(student):
    coursework = f"{student.courseworkTotal}/{COURSEWORK_COUNT * COURSEWORK_MAX}"
    exam = f"{student.examMark}/{EXAM_MAX}"
    overall = f"{student.percentage:.1f}%"
    return ROW_FORMAT.format(student.name, student.code, coursework, exam, overall, student.grade)


def formatTable(students):
    rows = [HEADER, "-" * len(HEADER)]
    rows += [formatRow(student) for student in students]
    return "\n".join(rows)


def recordsReport(students):
    """The table used by menu item 1, followed by the class summary."""
    summary = (f"Number of students: {len(students)}\n"
               f"Average percentage: {averagePercentage(students):.1f}%")
    return f"{formatTable(students)}\n\n{summary}"

class StudentManagerApp:
    """The window: a menu on the left, a results box on the right, and the dark mode switch at the bottom."""

    def __init__(self, root, students, dataPath, mode="light"):
        self.root = root
        self.students = students
        self.dataPath = dataPath
        self.mode = mode
        root.title("Student Manager")

        # The switch sits in a row at the bottom, so it is always visible.
        self.header = ttk.Frame(root, padding=(20, 0, 20, 12))
        self.header.pack(side="bottom", fill="x")
        self.darkVar = tk.BooleanVar(root, value=(mode == "dark"))
        ttk.Checkbutton(self.header, text="Dark mode", style="Switch.TCheckbutton",
                        variable=self.darkVar, command=self.toggleTheme).pack(side="right")

        menuFrame = ttk.Frame(root, padding=(20, 12, 12, 12))
        menuFrame.pack(side="left", fill="y")
        makeLabel(menuFrame, text="Menu", size=14, weight="bold", anchor="w").pack(fill="x")
        makeLabel(menuFrame, text="Select:", size=12, style="Muted.TLabel",
                  anchor="w").pack(fill="x", pady=(2, 12))

        menuItems = [
            ("View all records", self.viewAll),
            ("View one record", self.viewOne),
            ("Highest total mark", self.showHighest),
            ("Lowest total mark", self.showLowest),
            ("Sort records", self.sortRecords),
            ("Add a record", self.addRecord),
            ("Delete a record", self.deleteRecord),
            ("Update a record", self.updateRecord),
            ("Quit", root.destroy),
        ]
        for label, action in menuItems:
            ttk.Button(menuFrame, text=label, width=24, command=action).pack(fill="x", pady=3)

        colours = PALETTES[mode]
        self.output = tk.Text(root, width=80, height=32, font=(MONO_FONT, 10), state="disabled",
                              bg=colours["background"], fg=colours["text"], relief="flat", bd=0,
                              highlightthickness=0, padx=16, pady=12)
        self.output.pack(side="right", fill="both", expand=True, padx=12, pady=12)
        self.styleWindow()

    def styleWindow(self):
        """Colour the results box and the title bar for the current mode."""
        colours = PALETTES[self.mode]
        self.output.config(bg=colours["background"], fg=colours["text"])
        styleTitleBar(self.root, colours["background"], colours["text"], dark=(self.mode == "dark"))

    def toggleTheme(self):
        """Switch between light and dark mode. The results on screen stay as they are."""
        self.mode = "dark" if self.darkVar.get() else "light"
        applyPalette(self.root, self.mode)
        self.styleWindow()

    def showText(self, text):
        """Replace whatever is in the output box with new text."""
        self.output.config(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert(tk.END, text)
        self.output.config(state="disabled")

    def hasStudents(self):
        if not self.students:
            messagebox.showinfo("No records", "There are no student records.", parent=self.root)
            return False
        return True

    def chooseStudent(self, action):
        """Ask for a number or name, and return the one matching Student (or None)."""
        query = simpledialog.askstring("Find student",
                                       f"Enter the student number or name to {action}:",
                                       parent=self.root)
        if query is None:
            return None

        matches = findStudents(self.students, query)
        if not matches:
            messagebox.showerror("Not found", f"No student matches '{query.strip()}'.",
                                 parent=self.root)
            return None
        if len(matches) == 1:
            return matches[0]

        # More than one name matched, so ask for the exact student number.
        listing = "\n".join(f"{s.code}  {s.name}" for s in matches)
        code = simpledialog.askinteger("Several matches",
                                       f"More than one student matches:\n\n{listing}"
                                       "\n\nEnter the student number:",
                                       parent=self.root)
        if code is None:
            return None
        for student in matches:
            if student.code == code:
                return student
        messagebox.showerror("Not found", f"{code} is not one of the matches.", parent=self.root)
        return None

    def saveChanges(self, message):
        """Write the records to the file, then confirm to the user."""
        try:
            saveStudents(self.dataPath, self.students)
        except OSError as error:
            messagebox.showerror("Save failed", f"Could not save the changes:\n{error}",
                                 parent=self.root)
            return
        messagebox.showinfo("Saved", f"{message}\n\nstudentMarks.txt has been updated.",
                            parent=self.root)

    def viewAll(self):
        if not self.hasStudents():
            return
        self.showText(recordsReport(self.students))

    def viewOne(self):
        student = self.chooseStudent("view")
        if student is not None:
            self.showText(formatTable([student]))

    def showHighest(self):
        if not self.hasStudents():
            return
        best = studentsWithHighestTotal(self.students)
        self.showText("Highest total mark:\n\n" + formatTable(best))

    def showLowest(self):
        if not self.hasStudents():
            return
        worst = studentsWithLowestTotal(self.students)
        self.showText("Lowest total mark:\n\n" + formatTable(worst))

    def sortRecords(self):
        if not self.hasStudents():
            return
        ascending = messagebox.askyesno(
            "Sort records",
            "Sort by overall mark, lowest first?\n\nYes = ascending\nNo = descending",
            parent=self.root)
        order = "ascending" if ascending else "descending"
        ordered = sortStudents(self.students, ascending)
        self.showText(f"Records sorted by overall mark ({order}):\n\n"
                      + recordsReport(ordered))

    def addRecord(self):
        code = simpledialog.askinteger("Add student", f"Student number ({CODE_MIN}-{CODE_MAX}):",
                                       minvalue=CODE_MIN, maxvalue=CODE_MAX, parent=self.root)
        if code is None:
            return
        error = checkCodeAvailable(code, self.students)
        if error:
            messagebox.showerror("Duplicate number", error, parent=self.root)
            return

        name = simpledialog.askstring("Add student", "Student name:", parent=self.root)
        if name is None:
            return
        error = checkName(name)
        if error:
            messagebox.showerror("Invalid name", error, parent=self.root)
            return
        name = name.strip()

        courseworkMarks = []
        for number in range(1, COURSEWORK_COUNT + 1):
            mark = simpledialog.askinteger("Add student",
                                           f"Coursework {number} mark (out of {COURSEWORK_MAX}):",
                                           minvalue=0, maxvalue=COURSEWORK_MAX, parent=self.root)
            if mark is None:
                return
            courseworkMarks.append(mark)

        examMark = simpledialog.askinteger("Add student", f"Exam mark (out of {EXAM_MAX}):",
                                           minvalue=0, maxvalue=EXAM_MAX, parent=self.root)
        if examMark is None:
            return

        self.students.append(Student(code, name, courseworkMarks, examMark))
        self.saveChanges(f"{name} was added.")

    def deleteRecord(self):
        student = self.chooseStudent("delete")
        if student is None:
            return
        confirmed = messagebox.askyesno(
            "Confirm delete",
            f"Delete {student.name} ({student.code})?\nThis removes the record from the file.",
            parent=self.root)
        if not confirmed:
            return
        self.students.remove(student)
        self.saveChanges(f"{student.name}'s record was deleted.")

    def updateRecord(self):
        student = self.chooseStudent("update")
        if student is None:
            return

        menu = "\n".join(f"{number}. {option}" for number, option in enumerate(UPDATE_OPTIONS, start=1))
        choice = simpledialog.askinteger(
            "Update record",
            f"What would you like to change for {student.name}?\n\n{menu}\n\nEnter a number:",
            minvalue=1, maxvalue=len(UPDATE_OPTIONS), parent=self.root)
        if choice is None:
            return

        if choice == 1:                                   # Name
            newName = simpledialog.askstring("Update name", "New name:",
                                             initialvalue=student.name, parent=self.root)
            if newName is None:
                return
            error = checkName(newName)
            if error:
                messagebox.showerror("Invalid name", error, parent=self.root)
                return
            student.name = newName.strip()

        elif choice == 2:                                 # Student number
            newCode = simpledialog.askinteger("Update number",
                                              f"New student number ({CODE_MIN}-{CODE_MAX}):",
                                              minvalue=CODE_MIN, maxvalue=CODE_MAX,
                                              parent=self.root)
            if newCode is None:
                return
            error = checkCodeAvailable(newCode, self.students, ignore=student)
            if error:
                messagebox.showerror("Duplicate number", error, parent=self.root)
                return
            student.code = newCode

        elif choice in (3, 4, 5):                         # Coursework 1, 2 or 3
            index = choice - 3
            mark = simpledialog.askinteger(
                "Update coursework",
                f"New coursework {index + 1} mark (out of {COURSEWORK_MAX}):",
                minvalue=0, maxvalue=COURSEWORK_MAX, parent=self.root)
            if mark is None:
                return
            student.courseworkMarks[index] = mark

        else:                                             # 6 = Exam mark
            mark = simpledialog.askinteger("Update exam mark",
                                           f"New exam mark (out of {EXAM_MAX}):",
                                           minvalue=0, maxvalue=EXAM_MAX, parent=self.root)
            if mark is None:
                return
            student.examMark = mark

        self.saveChanges(f"{student.name}'s record was updated.")


if __name__ == "__main__":
    fontsLoaded = loadFonts()
    root = tk.Tk()
    FONT = pickFont(root, PREFERRED_FONT, FALLBACK_FONT, fontsLoaded)
    MONO_FONT = pickFont(root, MONO_PREFERRED, MONO_FALLBACK)
    if not loadTheme(root):
        messagebox.showerror("Theme not found",
                             "The Sun Valley theme files were not found. Put the "
                             "'sun-valley' folder next to main.py and try again.")
        root.destroy()
    else:
        applyPalette(root, "light")
        try:
            studentList = loadStudents(DATA_FILE)
        except (OSError, ValueError) as error:
            messagebox.showerror("Could not load data", str(error))
            root.destroy()
        else:
            StudentManagerApp(root, studentList, DATA_FILE)
            root.mainloop()