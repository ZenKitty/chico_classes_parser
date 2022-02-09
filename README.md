# chico_classes_parser

A command line class parser for CSU Chico by Duncan Hendrickson


## Usage

- Global Option:
    - ```-t``` Specify what semester/term you want to use for a given command
        - 0 by default, gets current semester's term
        - Format: ```./main_search.py -t -1 S CSCI-111```
            - Will result in previous semester's results

- Single Class Search:
    - ```./main_search.py S CSCI-211```
    - By default excludes lab sections, use -l to enable labs

- Multi-Class Functions
    - ```./main_search.py M -b CSCI CINS ...```
    - Use -b to find the best meeting times given a list of subjects
    - Use -w tp find the worst meeting times

- Time Function
    - Not created yet

Planned features are in ```TODO.md```