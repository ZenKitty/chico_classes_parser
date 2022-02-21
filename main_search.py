#!/usr/local/bin/python3
import sys
import textwrap
import requests
import argparse
import re
import json
from datetime import date


    #    
    #   This is a command line program designed to be used for CSU Chico's class search functionality 
    #   
    #    
    #   Developed by Duncan Hendrickson, GitHub repo available at: https://github.com/ZenKitty/chico_classes_parser 
    #    


def single_class(subject, catalog_nbr, URL, include_lab, term, verbose, raw) -> None:
    PARAMS = {
        'institution':'CHICO',
        'term':term, # Term is a numerical representation of Spring/Summer/Fall/Winter term
        'subject':subject, # 4 letter abbreviation, i.e. KINE = Kinesiology
        'catalog_nbr':catalog_nbr, # Class number from catalog
    }

    class_list = requests.get(url=URL, params=PARAMS)
    
    if class_list.status_code == 200:
        class_dict = class_list.json()
        if raw:
            print(json.dumps(class_dict, indent=4))
            return
        print(f"Search Results for {subject}-{catalog_nbr}")
        if not bool(class_dict):
            print("No classes found with that Subject and Catalog Number")
        for class_found in class_dict:
            if class_found['component'] == "DIS" or class_found['component'] == "LEC" or (class_found['component'] == "ACT" and include_lab):
                print(f"{class_found['component']} Section {class_found['class_section']}:", end="")
                if verbose: 
                    prof = class_found['instructors'][0]['name']
                    print(f"\t{prof}") 
                else: 
                    print("")
                for time in class_found['meetings']:
                    start_hour, start_minute, excess = time['start_time'].split('.', 2)
                    start_hour_int = int(start_hour) if int(start_hour) <= 12 else int(start_hour) % 12
                    start_M = "PM" if int(start_hour) >= 12 else "AM"
                    start_string = f"\t{start_hour_int}:{start_minute} {start_M}"

                    end_hour, end_minute, excess = time['end_time'].split('.', 2)
                    end_hour_int = int(end_hour) if int(end_hour) <= 12 else int(end_hour) % 12
                    end_M = "PM" if int(end_hour) >= 12 else "AM"
                    end_string = f"\t{end_hour_int}:{end_minute} {end_M}"
                    
                    print(f"\t{time['days']}", end="")
                    if verbose:
                        print(f"\t{class_found['instruction_mode_descr']}")
                    else:
                        print("")
                    print(start_string)
                    print(end_string)
        return
    else:
        print(f"Search failed with a code of: {class_list.status_code}")
        return
        

def multi_class(subjects, URL, best, term) -> None:
    subjects = set(subjects) # removes duplicates
    WEEKDAYS = {0: "Mo", 1: "Tu", 2: "We", 3: "Th", 4: "Fr"}
    times = {
        "Mo":{8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17:0},
        "Tu":{8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17:0},
        "We":{8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17:0},
        "Th":{8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17:0},
        "Fr":{8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17:0},
        }
    for subject in subjects:
        print(f"Processing {subject}...")
        PARAMS = {
            'institution':'CHICO',
            'term':term, # Term is a numerical representation of Spring/Summer/Fall/Winter term
            'subject':subject, # 4 letter abbreviation, i.e. KINE = Kinesiology
        }
        class_list = requests.get(url=URL, params=PARAMS)
        if class_list.status_code == 200:
            class_dict = class_list.json()
            if not bool(class_dict):
                print(f"Could not find abbreviation {subject}, skipping")
            for class_found in class_dict:
                for time in class_found['meetings']:
                    start_hour = time['start_time'].split('.')[0]
                    end_hour = time['end_time'].split('.')[0]
                    days = re.findall(r'[A-Z][a-z]', time['days']) # Date format is always 'MoWeFr' format
                    for day in days:
                        try:
                            start_hour_int = int(start_hour)
                            end_hour_int = int(end_hour)
                            for i in range(start_hour_int, end_hour_int + 1):
                                times[day][i] += 1
                        except:
                            pass
        else:
            print(class_list.status_code)
    for i, day in enumerate(WEEKDAYS):
        desired_time = 0
        if best:
            desired_time = min(times[WEEKDAYS[i]], key=times[WEEKDAYS[i]].get)
        else:
            desired_time = max(times[WEEKDAYS[i]], key=times[WEEKDAYS[i]].get)
        time_txt =" AM" if desired_time < 12 else " PM"
        desired_time = desired_time % 12 if desired_time > 12 else desired_time
        phrase = "Best" if best else "Worst"
        print(f"{phrase} time for an hour long event on {WEEKDAYS[i]}: {desired_time}{time_txt}")

    return

# Have to input a range that fully encapsulates the class time, just shooting for a 3 hour window
    # for labs and such
def time_to_times(hour: str, minute: str):
    hour_int = int(hour)
    if hour_int < 8:
        hour_int += 12
    if int(minute) == 30:
        hour_int += .5
    return (str(hour_int), str(hour_int+3))


def class_time(subject, URL, term, given_time):
    hour, minute = given_time.split(":")
    time_tuple = time_to_times(hour, minute)
    time_string = f"{time_tuple[0]},{time_tuple[1]}"
    PARAMS = {
        'institution':'CHICO',
        'term':term, # Term is a numerical representation of Spring/Summer/Fall/Winter term
        'subject':subject, # 4 letter abbreviation, i.e. KINE = Kinesiology
        'time_range': time_string,
    }
    class_list = requests.get(url=URL, params=PARAMS)
    if class_list.status_code == 200:
        class_dict = class_list.json()
        if not bool(class_dict):
            print(f"No classes found at {given_time}")
            return
        print(f"Classes starting at {given_time}")
        for class_found in class_dict:
            for time in class_found['meetings']:
                start_hour = time['start_time'].split('.')[0].lstrip('0')
                start_minute = time['start_time'].split('.')[1]
                if start_hour == hour and start_minute == minute:
                    print(f"{class_found['subject']}-{class_found['catalog_nbr']}\t{class_found['component']} Section {class_found['class_section']}\t{time['days']}")
        return
    else:
        print(f"Search failed with a code of: {class_list.status_code}")
        return


# Gets the numerical value for the given term requested, relative to current semester
def get_term(mod) -> str:
    today_term = date.today()
    add_sem = 0
    if mod % 2 == 1:
        mod -= 1
        if today_term.month < 6:
            add_sem = 6
        else:
            add_sem = 4
    add_year = abs(int(mod/2))
    coeff = 1 if mod > 0 else -1
    term = ((today_term.year + add_year) % 2022)*10*coeff + 2222 + add_sem
    return str(term)



def main() -> int:
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\
        Query current CSU Chico course schedule

        Subject Abbreviations and Course Numbers available at:
        http://catalog.csuchico.edu/viewer/home
        '''))
    

    # Allow user to use Single class functions or multiclass functions
    subparsers = parser.add_subparsers(title="Valid Subcommands", help="Type of query, S = Single, M = Multi, T not yet implemented", dest="command", required=True)
    
    solo_parser = subparsers.add_parser("S")
    solo_parser.add_argument("name", nargs=1, type=str, help="Input class name and number. Format: CSCI-211")
    solo_parser.add_argument("-l", "--lab", help="Include lab sections", action="store_true")
    solo_parser.add_argument("-v", "--verbose", help="Include information like Instructor and Instruction Mode (online or in-person, etc.)", action="store_true")
    solo_parser.add_argument("-r", "--raw", help="Print raw JSON data instead of parsed output.", action="store_true")
    
    multi_parser = subparsers.add_parser("M")
    group2 = multi_parser.add_mutually_exclusive_group()
    group2.add_argument("-b", "--best", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")
    group2.add_argument("-w", "--worst", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")

    time_parse = subparsers.add_parser("T")
    time_parse.add_argument("time", help="Find how many classes start at a specific time. Format: 10:00, or 2:30", nargs=2, type=str, metavar=("SUBJECT", "TIME"))
    
    parser.add_argument("-t", "--term", help="Specify a term relative to current term. Each semester is worth 1. Only fall and spring available currently. Format: '1', '+2', or '-4', etc. ", nargs=1, type=str, default='0')
    try:
        args = parser.parse_args()
    except:
        print("Unknown argument parser error. If you believe this to be an error please contact", file=sys.stderr)

    # CSU Chico class schedule search
    URL = "https://cmsweb.csuchico.edu/psc/CCHIPRD/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?"

    term = ''
    try:
        mod_term = int(args.term[0])
        term = get_term(mod_term)
    except:
        print("Failed to read term argument, please try again.", file=sys.stderr)
        return 1
    # Figure out which command they're using
    if args.command == "S":
        try:
            subject, catalog_nbr = re.split("-|_", args.name[0], 1)
            subject = subject.upper()
            single_class(subject, catalog_nbr, URL, args.lab, term, args.verbose, bool(args.raw))
        except ValueError:
            print(f"Failed to parse {args.name[0]}, failing...", file=sys.stderr)
            return 1
    elif args.command == "M":
        if not bool(args.best) and not bool(args.worst):
            print("M command requires one of the two subcommands, -b or -w", file=sys.stderr)
            return 1
        else:
            multi_class((args.best if bool(args.best) else args.worst), URL, bool(args.best), term)
    elif args.command == "T":
        class_time(args.time[0], URL, term, args.time[1])
    else:
        print("Something went wrong", file=sys.stderr)
        return 1
    return 0




if __name__ == "__main__":
    main()