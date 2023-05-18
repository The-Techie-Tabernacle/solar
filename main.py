"""
Project Solar! This is a basic data analyst script meant to allow the user to gather information on NS regions' WA -
membership rates as well as who is endorsing who etc.

Patch Notes vM1.0.5: started work on graphing
Patch Notes vM1.0.5: Another review, I didn't go through properly last time
Patch Notes vM1.0.4: Reviewed 1.0.3, altered variable names, overall tried to refit to convention (and fixed typos)
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

# from os import path
import gzip

# Graphing!
import plotting as pt


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
        error_request = ErrorRequest(
            "target_info",
            f"Illegal status code received for {regnat} {target}: {target_status}\nCheck that {target} "
            f"exists and is spelled correctly.",
        )
        return error_request

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
        wanations = region_data.find("UNNATIONS").text

        # string.split fails if char not found - this prevents 0 or 1 nation regions from causing a crash.
        if ":" in nations:
            nations = nations.split(":")
        else:
            nations = [nations]

        num_nations = len(nations)

        if wanations is not None:
            if "," in wanations:
                wanations = wanations.split(",")
            else:
                wanations = [wanations]

            del_non_endos = []

            if delegate != 0:
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
                        if nation not in del_endos and nation != delegate:
                            del_non_endos.append(nation)

                delegate_info = (delegate, del_non_endos)

            else:
                delegate_info = (None, [])

            officer_info = []

            # Populate x-axis over in plotting module
            del_off = [delegate]
            for i in officers:
                if i != delegate:
                    del_off.append(i)
            pt.PopulateXAxis(del_off)

            num_wa = len(wanations)

            # Y-axis list for # of non-endorsements
            plot_non_endos = [getRoundedIdiot(len(del_non_endos), num_wa)]

            for officer in officers:
                if (
                    delegate and officer != delegate
                ):  # Skip the del, we do that in a second anyway
                    officer_non_endo = []
                    endo_data = target_info(headers, "nation", officer)
                    if type(endo_data) == ErrorRequest:
                        return endo_data
                    wa = endo_data.find("UNSTATUS").text
                    endo_data = endo_data.find("ENDORSEMENTS").text

                    if wa != "Non-member":
                        if endo_data:
                            if "," in endo_data:
                                endo_data = endo_data.split(",")
                            else:
                                endo_data = [endo_data]

                        for nation in wanations:
                            if nation not in endo_data and nation != officer:
                                officer_non_endo.append(nation)

                    plot_non_endos.append(
                        getRoundedIdiot(len(officer_non_endo), num_wa)
                    )

                    officer_info.append((officer, officer_non_endo))

            # Finish Y-Axis plotting
            pt.PopulateYAxis(plot_non_endos)

            # Graph it baby
            pt.GraphTheGraph(target)

            return num_nations, num_wa, delegate_info, officer_info
        else:
            return num_nations, 0, None, None

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
        wanations = region_data.find("UNNATIONS").text

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

        non_endos = []
        for nation in wanations:
            if nation not in endorsers:
                non_endos.append(nation)

        num_nations = len(nations)
        num_wa = len(wanations)

        return num_nations, num_wa, (target, non_endos)

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


def getRoundedIdiot(a: int, b: int):
    # a = smaller number (out of b)
    # b = larger total number
    c = a * 100 / b
    return round(c, 2)


def non_wa(headers, regnat, target):
    raw_data = target_info(headers, regnat, target)

    if regnat == "region":
        nations = raw_data.find("NATIONS").text
        wanations = raw_data.find("UNNATIONS").text
        not_in_wa = []

        if ":" in nations:
            nations = nations.split(":")
        else:
            nations = [nations]

        num_nations = len(nations)

        if wanations is not None:
            if "," in wanations:
                wanations = wanations.split(",")
            else:
                wanations = [wanations]

            for nation in nations:
                if nation not in wanations:
                    not_in_wa.append(nation)

            num_wa = len(wanations)

            return num_nations, num_wa, not_in_wa
        else:
            return num_nations, 0, not_in_wa

    elif regnat == "nation":
        endo_status = raw_data.find("UNSTATUS").text
        if endo_status.lower() == "non-member":
            return False
        else:
            return True


def download_file(headers, url):
    local_filename = url.split("/")[-1]
    with requests.get(url, stream=True, headers=headers) as r:
        with open(local_filename, "wb") as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename


def parseNations(headers, region):
    r = requests.get(
        f"https://www.nationstates.net/cgi-bin/api.cgi?region={region}&q=nations",
        headers=headers,
    )  # Fetch current regionlist - helps speed at the cost of an API req
    nations = ET.fromstring(r.text).findtext("NATIONS").split(":")

    with gzip.open("nations.xml.gz", mode="r") as f:
        raw_nations = f.read()

    nations_xml = ET.fromstring(raw_nations)

    results = {}

    for nation in nations_xml.findall("NATION"):
        if nation.find("REGION").text.lower().replace(" ", "_") == region:
            last_login = nation.find("LASTACTIVITY").text
            if "days" in last_login.lower():
                num_days = str(int(last_login.split(" days")[0]))

                if num_days not in results:
                    results[num_days] = []

                results[num_days].append(nation.find("NAME").text)

    return results


def deathwatch(headers, regnat, target):
    # Deathwatch code adapted from https://github.com/rootabeta/DeathWatch
    if regnat == "region":
        download_file(
            headers, "https://www.nationstates.net/pages/nations.xml.gz"
        )  # Download nations datadump
        times = parseNations(headers, target)
        return times
    else:
        nation = target_info(headers, regnat, target)
        results = {}
        last_login = nation.find("LASTACTIVITY").text
        if "days" in last_login.lower():
            num_days = str(int(last_login.split(" days")[0]))

            if num_days not in results:
                results[num_days] = []

            results[num_days].append(nation.find("NAME").text)

        return results  # Same data type moment


# Parameters: mode, assorted settings
# Does: passes assorted settings to correct helper function as determined by mode.
# Opens file containing reporting information.
# Returns: status message
def perform_analysis(headers, mode, regnat, target, formatting):
    report_name = f"report-{DT.now().date().isoformat()}-{target}.txt"

    nations_raw = []

    match mode:
        case "non-endo":
            raw_data = non_endo(headers, regnat, target)
            if type(raw_data) == ErrorRequest:
                return raw_data
            else:
                num_nations = raw_data[0]
                num_wa = raw_data[1]
                del_info = raw_data[2]

            with open(report_name, "a") as f:
                f.write(f"Report for {regnat} {target.title()}\n")
                f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                f.write("Mode: non-endorsers\n")
                f.write("\n")
                f.write(f"Number of total nations: {num_nations}\n")
                f.write(
                    f"Number of nations in WA: {num_wa} ({getRoundedIdiot(num_wa,num_nations)})%\n"
                )

                if regnat == "region":
                    officer_info = raw_data[3]
                    if del_info and del_info[0]:
                        f.write("\n")

                        if del_info[1] is not None:
                            f.write(
                                f"Nonendorsers for delegate {del_info[0]}: {len(del_info[1])} "
                                f"({getRoundedIdiot(len(del_info[1]),num_wa)}%)\n"
                            )
                            write_nationlist(f, del_info[1], formatting)
                        else:
                            f.write(
                                f"Delegate {del_info[0]} has all possible endorsements"
                            )
                    else:
                        f.write(
                            f"\nThere is no delegate for {target.title().replace('_', ' ')}"
                        )

                    f.write("\n")

                    if officer_info is not None:
                        for officer in officer_info:
                            if officer:
                                officer_name = officer[0]
                                officer_non_e = officer[1]

                                if officer:
                                    if len(officer_non_e) > 0:
                                        if officer_non_e != [None]:
                                            f.write(
                                                f"Nonendorsers for officer {officer_name}: {len(officer_non_e)} "
                                                f"({getRoundedIdiot(len(officer_non_e),num_wa)}%)\n"
                                            )
                                            write_nationlist(
                                                f, officer_non_e, formatting
                                            )
                                            f.write("\n")
                                        else:
                                            f.write(
                                                f"Officer {officer_name} has all possible endorsements\n"
                                            )
                                    else:
                                        f.write(
                                            f"Officer {officer_name} is not in the world assembly\n"
                                        )
                    else:
                        f.write(
                            f"\nNo WA regional officers in {target.title().replace('_', ' ')}\n"
                        )

                elif regnat == "nation":
                    if del_info and del_info[0]:
                        f.write("\n")

                        if del_info[1] != [None]:
                            f.write(
                                f"Nonendorsers for target {del_info[0]}: {len(del_info[1])} "
                                f"({getRoundedIdiot(len(del_info[1]),num_wa)}%)\n"
                            )
                            write_nationlist(f, del_info[1], formatting)
                        else:
                            f.write(
                                f"Target {del_info[0]} has all possible endorsements"
                            )

                f.write("\nEND OF REPORT\n\n\n")

        case "non-wa":
            raw_data = non_wa(headers, regnat, target)
            if type(raw_data) != ErrorRequest:
                with open(report_name, "a") as f:
                    f.write(f"Report for {regnat} {target.title()}\n")
                    f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                    f.write("Mode: Non-WA\n")
                    if regnat == "region":
                        num_nations = raw_data[0]
                        num_wa = raw_data[1]
                        not_wa = raw_data[2]
                        f.write("\n")
                        f.write(f"Number of total nations: {num_nations}\n")
                        f.write(
                            f"Number of nations in WA: {num_wa} ({getRoundedIdiot(num_wa,num_nations)})%\n"
                        )
                        f.write(f"Nations not in the WA in {target}:\n")
                        if len(not_wa) > 0:
                            write_nationlist(f, not_wa, formatting)
                        else:
                            f.write(
                                f"There are no WA nations in {target.title().replace('_', ' ')}\n"
                            )

                    else:
                        if raw_data:
                            f.write(f"{target.title()} is in the World Assembly\n")
                        else:
                            f.write(f"{target.title()} is not in the World Assembly\n")

                    f.write("\nEND OF REPORT\n\n\n")
            else:
                return raw_data

        case "deathwatch":
            raw_data = deathwatch(headers, regnat, target)
            if type(raw_data) != ErrorRequest:
                with open(report_name, "a") as f:
                    f.write(f"Report for {regnat} {target.title()}\n")
                    f.write(f"Date generated: {DT.now().date().isoformat()}\n")
                    f.write("Mode: DeathWatch\n")
                    for key in sorted(raw_data.keys(), key=lambda x: int(x)):
                        f.write(
                            f"Nations that have not logged in for {key} days: ({len(raw_data[key])})\n"
                        )
                        write_nationlist(f, raw_data[key], formatting)

                    f.write("\nEND OF REPORT\n\n\n")
            else:
                return raw_data

    # Abort and alert user in the event of an error
    if type(raw_data) == ErrorRequest:
        return (
            raw_data.makePost()
        )  # One of the subfunctions wishes to raise an error request - pass it along as needed

    return f"Your results are available in the file {report_name}"
