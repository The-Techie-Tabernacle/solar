"""
The GUI file for Project Solar! Originally Solar was a console only script however this is being changed as to make the
script more user-friendly!
"""
import PySimpleGUI as sg

# import solar as so
import main as so

# Import the class
from main import ErrorRequest as ER

# Setting the color scheme
sg.theme("DarkBlack")

# Create a list for our wonderful dropdown menus
actionList = ["Non-Endo", "Non-WA", "Deathwatch"]
regNatList = ["Region", "Nation"]
tagTGList = ["TAG", "TG"]

# Create the layout
layout = [
    [sg.Text("Welcome to Solar!", key="-OUT-")],
    [sg.Text("Main Nation:     "), sg.Input(size=(40, 5), key="user-agent")],
    [
        sg.Text("Desired Target: "),
        sg.Input(size=(30, 5), key="-TARG-"),
        sg.Combo(
            values=regNatList, default_value="Region", readonly=True, key="-REGNAT-"
        ),
    ],
    [
        sg.Text("Desired Action: "),
        sg.Combo(
            values=actionList, default_value="Non-Endo", readonly=True, key="-ACTION-"
        ),
        sg.Combo(values=tagTGList, default_value="TAG", readonly=True, key="-TAGTG-"),
    ],
    [
        sg.Button("Exit", size=(3, 1), key="-EXIT-"),
        sg.Button("Submit", size=(5, 1), key="-SUBMIT-", bind_return_key=True),
    ],
]

# Create the window!
window = sg.Window("Solar", layout)

# Starting event
event = "-START-"
headers = ""


# Setting user entry
def GetHeaders(values):
    # Headers with main nation from entry
    headers = {
        "User-Agent": (
            "Project Solar requesting region and nation information, developed by"
            f" nation=Hesskin_Empire and in use by {values['user-agent']}"
        )
    }
    return headers


# Loop to open and hold open the gui
while event != "-EXIT-":
    event, values = window.read()
    # Check if the headers have been set
    if headers == "":
        headers = GetHeaders(values)
    # Checks if the window closed or if the exit button was clicked
    if event in [sg.WIN_CLOSED, "-EXIT-"]:
        break
    elif event == "-SUBMIT-":
        window["-OUT-"].update("Performing analysis, please wait...")

        # Checking the user agent
        popup = sg.PopupYesNo(
            f"Is your main nation {values['user-agent']}?",
            title="Confirm Nation",
            grab_anywhere=True,
            keep_on_top=True,
        )

        # Checking the answer!
        if popup == "No":
            window["-OUT-"].update("Please re-enter your main nation.")
            event = "-START-"
        else:
            post = (  # make the default ask to file a bug report
                "Error: could not complete request. Please file a bug report."
            )
            mode = values["-ACTION-"].lower()
            target = values["-TARG-"].lower().replace(" ", "_")  # NSification
            regnat = values["-REGNAT-"].lower()
            formatting = values["-TAGTG-"].lower()

            post = so.perform_analysis(headers, mode, regnat, target, formatting)
            if type(post) == ER:
                post = post.makePost()

            window["-OUT-"].update(post)


# Close the window
window.close()
