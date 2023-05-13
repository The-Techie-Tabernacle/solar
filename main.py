"""
Project Solar! This is a basic data analyst script meant to allow the user to gather information on NS regions' WA -
membership rates as well as who is endorsing who etc.

Patch Notes vM1.0.2: Began refactoring the code to work with new GUI
Patch Notes vM0.2.4: Redid most of it for interaction with the GUI. . . needs work
Patch Notes vM0.2.3: Added Try/Except to check if there are no WA nations
Patch Notes vM0.2.2: Merged Malphe fork, did input validation for region/nation that are not valid
Patch Notes vM0.2: Rewrote entire thing to make use of functions to allow different options for the user -M
Patch Notes vM0.1.2: Added functionality to show non-endorsers for officers -A

Malphe Fork 1D.5M.2023Y: tweaked command line interface. Added functionality for non-endorsers with [nation] tags.
"""
import requests
from xml.etree import ElementTree as ET
from datetime import datetime as DT

# Global scope lists (Two of our three primaries use this)
residents = []
wa_nations = []

# Global scope root
information_root = None

# Global scope bool
target_type = True


def regnat_request(regnat):
    # Checks if regnat is a region or not
    global target_type

    if regnat == "Region":
        # If region, True
        target_type = True
    else:
        # Otherwise, False
        target_type = False


def target_info(headers, target: str):
    post = str
    global information_root
    information_root = None

    # Sanitize target
    target = target.replace(" ", "_").lower()

    # If it's a region, set the url to a region otherwise set to nation
    if target_type is True:
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={target}"
    else:
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={target}"

    # Grab the API call itself
    information_api = requests.get(
        url, headers=headers
    )

    # Check status and make sure we actually get in
    target_status = information_api.status_code
    if target_status != 200:
        post = f"Error: {target_status}"
    else:
        # If we get in, grab the root and set it via global
        information_root = ET.fromstring(information_api.content)

    # Return out post
    return post


def non_endo():
    post = ""
    if target_type is True:
        print("Region")
    else:
        print("Nation")
    return post
