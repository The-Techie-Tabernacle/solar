# SOLAR
## About
Solar is a small tool developed by Ghazi-Rahman Ammar, Volstrostia, and Malphe II.

Solar can get a list of:
- WA Nations not endorsing the Delegate and Officers of a target region.
- WA Nations not endorsing the target nation.
- Non WA nations in a target region.
- Nations that have not logged in for a certain number of days

## Installation

### Pre-built executable
Solar releases include a Windows executable that can run without a local python installation.<br>
To use it, download the latest release, unzip the compressed folder, and run the included exe file.

### From Source
Solar also can be run from source by running `python3 gui.py`
Solar is developed for use with Python 3.10 and above. Older versions have not been tested.

## Usage
Solar has three functions, two target modes, and two output modes. 

To use Solar, first place your nation name in the first box. Do not include the pretitle - e.g., instead of "The Republic of Mynation", just put "mynation"

Next, enter a target region or nation name, and select a function and target mode. There are three functions:
- Non-Endo
 -- In Nation mode, show a list of everyone not endorsing the target nation
 -- In Region mode, show a list of everyone not endorsing the delegate and ROs in the target region
- Non-WA
 -- In Nation mode, show if a nation is or is not a WA member
 -- In Region mode, show a list of people not in the WA in the target region
- DeathWatch
 -- In Nation mode, show how long it has been since the target nation logged in
 -- In Region mode, show a breakdown of nations who have not logged in by number of days in the target region

Finally, select output format. There are two output formats.
- TAG: Create a list of nations in [nation]MyNation[/nation] [nation]MyOtherNation[/nation] format
- TG: Create a list of nations in MyNation, MyOtherNation format, broken up into groups of eight or fewer.
Additionally, some functions, such as DeathWatch in region mode, may create a graph of results.

Resulting reports will be saved with a report- or graph- prefix, followed by the date and target name.

## Support
Contact me on discord @ theonetruepi with any issues
