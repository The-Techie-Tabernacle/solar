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
    [sg.Text("Desired Target: "), sg.Input(size=(30, 5), key="-TARG-"), sg.Combo(values=regNatList,
                                                                         readonly=True, key="-REGNAT-")],
    [sg.Text("Desired Action: "), sg.Combo(values=actionList, readonly=True, key="-ACTION-"),
     sg.Combo(values=tagTGList, readonly=True, key="-TAGTG-")],
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
while event != "exit":
    event, values = window.read()
    # Check if the headers have been set
    if headers == "":
        headers = GetHeaders(values)
    # Checks if the window closed or if the exit button was clicked
    if event == sg.WIN_CLOSED or event == "exit":
        break
    elif event == "submit":
        # Wonderful, wonderful match case
        # TODO - Redo match case for new options
        match (values["action"]):
            case "Del Non-Endo":
                post = so.region_info(headers, "NER", values["target"])
                window['OUT'].update(post)

            case "Non-WA in Region":
                post = so.region_info(headers, "NWR", values["target"])
                window['OUT'].update(post)

            case "Nation Non-Endo":
                if window['tag'].get_text() == 'TAG':
                    post = so.calc_non_nat_tagged(headers, values["target"])
                    window['OUT'].update(post)
                else:
                    post = so.calc_non_nat(headers, values["target"])
                    window['OUT'].update(post)

            case other:
                print("Yeet")
    else:
        print("test")

# Close the window
window.close()
