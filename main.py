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

############ I'M BANISHING YOU TO THE SHADOW REALM ########## # Global scope lists (Two of our three primaries use this) AND THEY SHOULDN'T
############ I'M BANISHING YOU TO THE SHADOW REALM ########## #residents = []
############ I'M BANISHING YOU TO THE SHADOW REALM ########## #wa_nations = []
############ I'M BANISHING YOU TO THE SHADOW REALM ########## 
############ I'M BANISHING YOU TO THE SHADOW REALM ########## # Global scope root
############ I'M BANISHING YOU TO THE SHADOW REALM ########## #information_root = None
############ I'M BANISHING YOU TO THE SHADOW REALM ########## 
############ I'M BANISHING YOU TO THE SHADOW REALM ########## # Global scope bool
############ I'M BANISHING YOU TO THE SHADOW REALM ########## #target_type = True

# Leaving this here as a note to future developers, so you all see what I had to deal with.
#def regnat_request(regnat):
#    # Checks if regnat is a region or not
#    global target_type
#
#    if regnat == "Region":
#        # If region, True
#        target_type = True
#    else:
#        # Otherwise, False
#        target_type = False

class ErrorRequest():
    def __init__(self, source, message, location="any"):
        self.source = source #Parent function
        self.message = message
        self.location = location

    def makePost(self, override=False):
        if override or self.location == "post" or self.location == "any":
            print(f"Error in {self.source}: {self.message}")
            return f"Error in {self.source}: {self.message}"

    def fatal(self):
        raise RuntimeError(f"Fatal error in {self.source}: {self.message}. Solar cannot recover and will now shut down. Please file a bug report.")

def target_info(headers, regnat, target):
#    post = str
#    information_root = None

    # Target is already sanitized from user input
#    target = target.replace(" ", "_").lower()

    # If it's a region, set the url to a region otherwise set to nation
    if regnat == "region":
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={target}&q=wanations+nations+officers+delegate"
    elif regnat == "nation":
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={target}&q=region+endorsements"
    else:
        raise RuntimeError(f"Illegal option selected for regnat: {regnat}") # How did we get here?

    # Grab the API call itself
    information_api = requests.get(
        url, headers=headers
    )

    # Check status and make sure we actually get in
    target_status = information_api.status_code

    if target_status != 200:
        errorRequest = ErrorRequest("target_info",f"Illegal status code received for {regnat} {target}: {target_status}\nCheck that {target} exists and is spelled correctly.")
        return errorRequest

    else:
        return ET.fromstring(information_api.text) # Return the actual XML and allow calling function to parse


# R : ( numNations, numWA, (delegate, nonEndos), [(officer, nonEndos)])
# N : ( numNations, numWA, (target, nonEndos))
def non_endo(headers, regnat, target):
    if not headers:
        return "Could not complete HTTP request: Headers not specified"

    raw_data = target_info(headers, regnat, target)
    if type(raw_data) == ErrorRequest:
        return raw_data # Return the error request and do not attempt to parse it
    
    if regnat == "region":
        regionData = raw_data #.find("REGION")
        if type(raw_data) == ErrorRequest:
            return raw_data

        delegate = regionData.find("DELEGATE").text

        officers = []
        officersAll = regionData.find("OFFICERS")
        for officer in officersAll.findall("OFFICER"):
            officers.append(officer.find("NATION").text)

        nations = regionData.find("NATIONS").text
        numNations = len(nations)
        wanations = regionData.find("UNNATIONS").text
        numWA = len(wanations)
        delegateInfo = None

        #string.split fails if char not found - this prevents 0 or 1 nation regions from causing a crash. 

        if ":" in nations:
            nations = nations.split(":") 
        else:
            nations = [nations]

        if "," in wanations:
            wanations = wanations.split(",") 
        else:
            wanations = [wanations]

        if delegate:
            delnonendorsers = []
            delendorsers = target_info(headers, "nation", delegate)
            if type(delendorsers) == ErrorRequest:
                return delendorers

            delendorsers = delendorsers.find("ENDORSEMENTS").text
            if delendorsers:
                if "," in delendorsers:
                    delendorsers = delendorsers.split(",")
                else:
                    delendorsers = [delendorsers]

                for nation in wanations:
                    if nation not in delendorsers:
                        delnonendorsers.append(nation)

            delegateInfo = (delegate, delnonendorsers)

        else:
            delegateInfo = (None, [])

        officerInfo = []

        for officer in officers:
            if delegate and officer != delegate: # Skip the del, we do that in a second anyway
                officernonendorsers = []
                endoData = target_info(headers, "nation", officer)
                if type(endoData) == ErrorRequest:
                    return endoData
                endorsers = endoData.find("ENDORSEMENTS").text

                if endoData:
                    if "," in endoData:
                        endorsers = endorsers.split(",")
                    else:
                        endorsers = [endorsers]

                for nation in wanations:
                    if nation not in endorsers:
                        officernonendorsers.append(nation)

                officerInfo.append((officer, officernonendorsers))
        return (numNations, numWA, delegateInfo, officerInfo)

    elif regnat == "nation":
        nationData = target_info(headers, regnat, target)
        if type(nationData) == ErrorRequest:
            return nationData
        endorsers = nationData.find("ENDORSEMENTS").text
        regionname = nationData.find("REGION").text.lower().replace(" ","_")

        regionData = target_info(headers, "region", regionname)
        if type(regionData) == ErrorRequest:
            return regionData

        nations = regionData.find("NATIONS").text
        numNations = len(nations)
        wanations = regionData.find("UNNATIONS").text
        numWA = len(wanations)

        if ":" in nations:
            nations = nations.split(":") 
        else:
            nations = [nations]

        if "," in wanations:
            wanations = wanations.split(",") 
        else:
            wanations = [wanations]

        if endorsers:
            if "," in endorsers:
                endorsers = endorsers.split(",")
            else:
                endorsers = [endorsers]
        else:
            endorsers = []

        nonendorsers = []
        for nation in wanations:
            if nation not in endorsers:
                nonendorsers.append(nation)

        return (numNations, numWA, (target, nonendorsers))

    else:
        raise RuntimeError(f"Illegal option selected for regnat: {regnat}") # How did we get here?

def non_wa():
    pass

def deathwatch():
    pass

def write_nationlist(f,nationlist,formatting):
    if formatting == "tag":
        for nation in nationlist:
            f.write(f"[nation]{nation}[/nation] ")
        f.write("\n")

    elif formatting == "tg":
        for i in range(0,len(nationlist),8):
            for nation in nationlist[i:i+8]:
                f.write(f"{nation}, ")
            f.write("\n")

    f.write("\n")

def getRoundedIdiot(a,b):
    # 5 / 10
    # 50000 / 10
    # 5000
    # 50.00

    return int((a * 10000) / b) / 100.0

# Parameters: mode, assorted settings
# Does: passes assorted settings to correct helper function as determined by mode. Opens file containing reporting information. 
# Returns: status message
def perform_analysis(headers,mode,regnat,target,formatting):
    reportName = f"report-{DT.now().date().isoformat()}-{target}.txt"
    
    nations_raw = []

    match mode:
        case "non-endo":
            raw_data = non_endo(headers, regnat, target)
            numNations = raw_data[0]
            numWA = raw_data[1]
            delInfo = raw_data[2]

            with open(reportName, "a") as f:
                f.write(f"Report for {regnat} {target.title()}\n")
                f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                f.write("Mode: non-endorsers\n")
                f.write("\n")
                f.write(f"Number of total nations: {numNations}\n")
                f.write(f"Number of nations in WA: {numWA} ({getRoundedIdiot(numWA,numNations)})%\n")

                if regnat == "region":
                    officerInfo = raw_data[3]
                    if delInfo and delInfo[0]:
                        f.write("\n")

                        if delInfo[1] != [None]:
                            f.write(f"Nonendorsers for delegate {delInfo[0]}: {len(delInfo[1])} ({getRoundedIdiot(len(delInfo[1]),numWA)}%)\n")
                            write_nationlist(f,delInfo[1],formatting)
                        else:
                            f.write(f"Delegate {delInfo[0]} has all possible endorsements")

                    f.write("\n")

                    for officer in officerInfo:
                        if officer:
                            officerName = officer[0]
                            officerNonE = officer[1]
                            
                            if officer:
                                if officerNonE != [None]:
                                    f.write(f"Nonendorsers for officer {officerName}: {len(officerNonE)} ({getRoundedIdiot(len(officerNonE),numWA)}%)\n")
                                    write_nationlist(f,officerNonE,formatting)
                                    f.write("\n")
                                else:
                                    f.write(f"Officer {officerName} has all possible endorsements")

                elif regnat == "nation":
                    if delInfo and delInfo[0]:
                        f.write("\n")

                        if delInfo[1] != [None]:
                            f.write(f"Nonendorsers for target {delInfo[0]}: {len(delInfo[1])} ({getRoundedIdiot(len(delInfo[1]),numWA)}%)\n")
                            write_nationlist(f,delInfo[1],formatting)
                        else:
                            f.write(f"Target {delInfo[0]} has all possible endorsements")

                f.write("\nEND OF REPORT\n\n\n")

        case "non-wa":
            raw_data = non_wa(headers, regnat, target)

        case "deathwatch":
            raw_data = deathwatch(headers, regnat, target)
            
    # Abort and alert user in the event of an error
    if type(raw_data) == ErrorRequest:
        return raw_data.makePost() # One of the subfunctions wishes to raise an error request - pass it along as needed

    

    # TODO: Parse nations_raw according to formatting
    # TODO: Generate report using parsed nationlist

    return f"Your results are available in the file {reportName}"
