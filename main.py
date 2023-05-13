"""
Project Solar! This is a basic data analyst script meant to allow the user to gather information on NS regions' WA -
membership rates as well as who is endorsing who etc.

Patch Notes vA1.0.3: Continue refactoring, backend modification, etc. 
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
import shutil
#from os import path
import gzip

class ErrorRequest:
    def __init__(self, source, message, location="any"):
        self.source = source  # Parent function
        self.message = message
        self.location = location

    def makePost(self, override=False):
        if override or self.location == "post" or self.location == "any":
            print(f"Error in {self.source}: {self.message}")
            return f"Error in {self.source}: {self.message}"

    def fatal(self):
        raise RuntimeError(
            f"Fatal error in {self.source}: {self.message}. Solar cannot recover and will now shut down. "
            f"Please file a bug report."
        )


def target_info(headers, regnat, target):
    # If it's a region, set the url to a region otherwise set to nation
    if regnat == "region":
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?region={target}&q=wanations+nations+officers+delegate"
    elif regnat == "nation":
        url = f"https://www.nationstates.net/cgi-bin/api.cgi?nation={target}&q=region+endorsements+wa+lastactivity"
    else:
        raise RuntimeError(
            f"Illegal option selected for regnat: {regnat}"
        )  # How did we get here?

    # Grab the API call itself
    information_api = requests.get(url, headers=headers)

    # Check status and make sure we actually get in
    target_status = information_api.status_code

    if target_status != 200:
        errorRequest = ErrorRequest(
            "target_info",
            f"Illegal status code received for {regnat} {target}: {target_status}\nCheck that {target} exists and is spelled correctly.",
        )
        return errorRequest

    else:
        return ET.fromstring(
            information_api.text
        )  # Return the actual XML and allow calling function to parse


def non_endo(headers, regnat, target):
    if not headers:
        return "Could not complete HTTP request: Headers not specified"

    raw_data = target_info(headers, regnat, target)
    if type(raw_data) == ErrorRequest:
        return raw_data  # Return the error request and do not attempt to parse it

    if regnat == "region":
        region_data = raw_data  # .find("REGION")
        if type(raw_data) == ErrorRequest:
            return raw_data

        delegate = region_data.find("DELEGATE").text

        officers = []
        officers_all = region_data.find("OFFICERS")
        for officer in officers_all.findall("OFFICER"):
            officers.append(officer.find("NATION").text)

        nations = region_data.find("NATIONS").text
        num_nations = len(nations)
        wanations = region_data.find("UNNATIONS").text
        num_wa = len(wanations)

        # string.split fails if char not found - this prevents 0 or 1 nation regions from causing a crash.
        if ":" in nations:
            nations = nations.split(":")
        else:
            nations = [nations]

        if "," in wanations:
            wanations = wanations.split(",")
        else:
            wanations = [wanations]

        if delegate:
            del_non_endos = []
            del_endos = target_info(headers, "nation", delegate)
            if type(del_endos) == ErrorRequest:
                return del_endos

            del_endos = del_endos.find("ENDORSEMENTS").text
            if del_endos:
                if "," in del_endos:
                    del_endos = del_endos.split(",")
                else:
                    del_endos = [del_endos]

                for nation in wanations:
                    if nation not in del_endos:
                        del_non_endos.append(nation)

            delegate_info = (delegate, del_non_endos)

        else:
            delegate_info = (None, [])

        officer_info = []

        for officer in officers:
            if (
                delegate and officer != delegate
            ):  # Skip the del, we do that in a second anyway
                officer_non_endo = []
                endo_data = target_info(headers, "nation", officer)
                if type(endo_data) == ErrorRequest:
                    return endo_data
                endorsers = endo_data.find("ENDORSEMENTS").text

                if endo_data:
                    if "," in endo_data:
                        endorsers = endorsers.split(",")
                    else:
                        endorsers = [endorsers]

                for nation in wanations:
                    if nation not in endorsers:
                        officer_non_endo.append(nation)

                officer_info.append((officer, officer_non_endo))
        return num_nations, num_wa, delegate_info, officer_info

    elif regnat == "nation":
        nation_data = target_info(headers, regnat, target)
        if type(nation_data) == ErrorRequest:
            return nation_data
        endorsers = nation_data.find("ENDORSEMENTS").text
        regionname = nation_data.find("REGION").text.lower().replace(" ", "_")

        region_data = target_info(headers, "region", regionname)
        if type(region_data) == ErrorRequest:
            return region_data

        nations = region_data.find("NATIONS").text
        num_nations = len(nations)
        wanations = region_data.find("UNNATIONS").text
        num_wa = len(wanations)

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

        return num_nations, num_wa, (target, nonendorsers)

    else:
        raise RuntimeError(
            f"Illegal option selected for regnat: {regnat}"
        )  # How did we get here?



def write_nationlist(f, nationlist, formatting):
    if formatting == "tag":
        for nation in nationlist:
            f.write(f"[nation]{nation}[/nation] ")
        f.write("\n")

    elif formatting == "tg":
        for i in range(0, len(nationlist), 8):
            for nation in nationlist[i : i + 8]:
                f.write(f"{nation}, ")
            f.write("\n")

    f.write("\n")


def getRoundedIdiot(a, b):
    # 5 / 10
    # 50000 / 10
    # 5000
    # 50.00

    return int((a * 10000) / b) / 100.0

def non_wa(headers, regnat, target):
    raw_data = target_info(headers, regnat, target)

    if regnat == "region":
        nations = raw_data.find("NATIONS").text
        wanations = raw_data.find("UNNATIONS").text

        if ":" in nations:
            nations = nations.split(":")
        else:
            nations = [nations]

        if "," in wanations:
            wanations = wanations.split(",")
        else:
            wanations = [wanations]
        
        notinwa = []
        for nation in nations:
            if nation not in wanations:
                notinwa.append(nation)

        return (len(nations), len(wanations), notinwa)

    elif regnat == "nation":
        endostatus = raw_data.find("UNSTATUS").text
        if endostatus.lower() == "non-member":
            return False
        else:
            return True


# https://www.nationstates.net/pages/regions.xml.gz 
# https://www.nationstates.net/pages/nations.xml.gz 

def download_file(headers, url):
    #print(f"Downloading {url}")
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True, headers=headers) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    
    return local_filename

def parseNations(headers, region):
    r = requests.get(f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=nations", headers=headers) # Fetch current regionlist - helps speed at the cost of an API req
    nations = ET.fromstring(r.text).findtext("NATIONS").split(":")

    with gzip.open("nations.xml.gz",mode="r") as f:
        rawnations = f.read()

    nationsxml = ET.fromstring(rawnations)

    results = {}

    for nation in nationsxml.findall("NATION"):
        if nation.find("REGION").text.lower().replace(" ","_") == region:
            lastlogin = nation.find("LASTACTIVITY").text
            if "days" in lastlogin.lower():
                numDays = str(int(lastlogin.split(" days")[0]))

                if numDays not in results:
                    results[numDays] = []

                results[numDays].append(nation.find("NAME").text)

    return results


def deathwatch(headers, regnat, target):
    # Deathwatch code adapted from https://github.com/rootabeta/DeathWatch
    if regnat == "region":
        download_file(headers, "https://www.nationstates.net/pages/nations.xml.gz") #Download nations datadump
        times = parseNations(headers, target)
        return times
    else:
        nationData = target_info(headers, regnat, target)
        results = {}
        lastlogin = nation.find("LASTACTIVITY").text
        if "days" in lastlogin.lower():
            numDays = str(int(lastlogin.split(" days")[0]))

            if numDays not in results:
                results[numDays] = []

            results[numDays].append(nation.find("NAME").text)

        return results # Same data type moment

# Parameters: mode, assorted settings
# Does: passes assorted settings to correct helper function as determined by mode.
# Opens file containing reporting information.
# Returns: status message
def perform_analysis(headers, mode, regnat, target, formatting):
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
                f.write(
                    f"Number of nations in WA: {numWA} ({getRoundedIdiot(numWA,numNations)})%\n"
                )

                if regnat == "region":
                    officerInfo = raw_data[3]
                    if delInfo and delInfo[0]:
                        f.write("\n")

                        if delInfo[1] != [None]:
                            f.write(
                                f"Nonendorsers for delegate {delInfo[0]}: {len(delInfo[1])} ({getRoundedIdiot(len(delInfo[1]),numWA)}%)\n"
                            )
                            write_nationlist(f, delInfo[1], formatting)
                        else:
                            f.write(
                                f"Delegate {delInfo[0]} has all possible endorsements"
                            )

                    f.write("\n")

                    for officer in officerInfo:
                        if officer:
                            officerName = officer[0]
                            officerNonE = officer[1]

                            if officer:
                                if officerNonE != [None]:
                                    f.write(
                                        f"Nonendorsers for officer {officerName}: {len(officerNonE)} ({getRoundedIdiot(len(officerNonE),numWA)}%)\n"
                                    )
                                    write_nationlist(f, officerNonE, formatting)
                                    f.write("\n")
                                else:
                                    f.write(
                                        f"Officer {officerName} has all possible endorsements"
                                    )

                elif regnat == "nation":
                    if delInfo and delInfo[0]:
                        f.write("\n")

                        if delInfo[1] != [None]:
                            f.write(
                                f"Nonendorsers for target {delInfo[0]}: {len(delInfo[1])} ({getRoundedIdiot(len(delInfo[1]),numWA)}%)\n"
                            )
                            write_nationlist(f, delInfo[1], formatting)
                        else:
                            f.write(
                                f"Target {delInfo[0]} has all possible endorsements"
                            )

                f.write("END OF REPORT\n\n\n")

        case "non-wa":
            raw_data = non_wa(headers, regnat, target)

            with open(reportName, "a") as f:
                f.write(f"Report for {regnat} {target.title()}\n")
                f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                f.write("Mode: Non-WA\n")
                if regnat == "region":
                    numNations = raw_data[0]
                    numWA = raw_data[1]
                    notWA = raw_data[2]
                    f.write("\n")
                    f.write(f"Number of total nations: {numNations}\n")
                    f.write(
                        f"Number of nations in WA: {numWA} ({getRoundedIdiot(numWA,numNations)})%\n"
                    )
                    f.write(f"Nations not in the WA in {target}:\n")
                    write_nationlist(f,notWA,formatting)

                else:
                    if raw_data:
                        f.write(f"{target.title()} is in the World Assembly\n")
                    else:
                        f.write(f"{target.title()} is not in the World Assembly\n")

                f.write("\nEND OF REPORT\n\n\n")

        case "deathwatch":
            raw_data = deathwatch(headers, regnat, target)

            with open(reportName, "a") as f:
                f.write(f"Report for {regnat} {target.title()}\n")
                f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                f.write("Mode: DeathWatch\n")
                for key in sorted(raw_data.keys(), key=lambda x: int(x)):
                    f.write(f"Nations have not logged in for {key} days: ({len(raw_data[key])})\n")
                    write_nationlist(f,raw_data[key],formatting)
    #                f.write("\n")
                
                f.write("\nEND OF REPORT\n\n\n")

    # Abort and alert user in the event of an error
    if type(raw_data) == ErrorRequest:
        return (
            raw_data.makePost()
        )  # One of the subfunctions wishes to raise an error request - pass it along as needed

    # TODO: Parse nations_raw according to formatting
    # TODO: Generate report using parsed nationlist

    return f"Your results are available in the file {reportName}"
