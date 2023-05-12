"""
The GUI file for Project Solar! Originally Solar was a console only script however this is being changed as to make the
script more user-friendly!

Patch Notes vMG-1.0.1: Revamping front end for 1.1 release
Patch Notes vAX-0.1.2: Hotfixes for existing work
Patch Notes vMG-0.1.1: Seems to mostly be working, I think most of the issues rn are in the solar module not gui
Patch Notes vMG-0.1: Actually created the file, current calls from solar itself so still does console printing
"""
import PySimpleGUI as sg
import solar as so

# Setting the color scheme
sg.theme("NeutralBlue")

# Create a list for our wonderful dropdown menus
actionList = ["Non-Endo", "Non-WA", "Deathwatch"]
regNatList = ["Region", "Nation"]
tagTGList = ["TAG", "TG"]

# Create the layout
layout = [
    [sg.Text("Welcome to Solar!", key="-OUT-")],
    [sg.Text("Main Nation:     "), sg.Input(size=(40, 5), key="user-agent")],
    [sg.Text("Desired Target: "), sg.Input(size=(30, 5), key="-TARG-"), sg.Combo(values=regNatList, default_value="Region",
                                                                                 readonly=True, key="-REGNAT-")],
    [sg.Text("Desired Action: "), sg.Combo(values=actionList, default_value="Non-Endo" , readonly=True, key="-ACTION-"),
     sg.Combo(values=tagTGList, default_value="TAG", readonly=True, key="-TAGTG-")],
    [sg.Button("Exit", size=(3, 1), key="-EXIT-"), sg.Button("Submit", size=(5, 1), key="-SUBMIT-")]
]

# Create the window!
window = sg.Window("Solar", layout)

# Starting event
event = "start"
headers = ""


# Setting user entry
def GetHeaders(values):
    # Headers with main nation from entry
    headers = {
        "User-Agent": f"Project Solar requesting region and nation information, developed by nation=Hesskin_Empire "
                      f"and in use by {values['user-agent']}"
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
        # Wonderful, wonderful match case
        match (values["-ACTION-"]):
            case "Non-Endo":
                if values["-REGNAT-"] == "Region":
                    post = "Region"  # Once backend functions are fixed it will call for post here
                else:
                    post = "Nation"
                window['-OUT-'].update(post)

            case "Non-WA":
                if values["-REGNAT-"] == "Region":
                    post = "Region"  # Once backend functions are fixed it will call for post here
                else:
                    post = "Nation"
                window['-OUT-'].update(post)

            case "Deathwatch":
                if values["-REGNAT-"] == "Region":
                    post = "Region"  # Once backend functions are fixed it will call for post here
                else:
                    post = "Nation"
                window['-OUT-'].update(post)


# Close the window
window.close()
