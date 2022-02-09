import sys
import textwrap
import requests
import argparse
import re

def single_class(subject, catalog_nbr, URL, include_labs):
    PARAMS = {
        'institution':'CHICO',
        'term':'2202', # Term is a numerical representation of Spring/Summer/Fall/Winter term
        'subject':subject, # 4 letter abbreviation, i.e. KINE = Kinesiology
        'catalog_nbr':catalog_nbr, # Class number from catalog
    }

    class_list = requests.get(url=URL, params=PARAMS)
    
    if class_list.status_code == 200:
        class_dict = class_list.json()
        print(class_list)
        print(f"Search Results for {subject}-{catalog_nbr}")
        if not bool(class_dict):
            print("No classes found with that Subject and Catalog Number")
        for class_found in class_dict:
            if class_found['component'] != "ACT" or include_labs:
                print(f"{class_found['component']} Section {class_found['class_section']}:")
                for time in class_found['meetings']:
                    start_hour, start_minute, start_second, excess = time['start_time'].split('.')
                    start_hour_int = int(start_hour) if int(start_hour) <= 12 else int(start_hour) % 12
                    start_M = "PM" if int(start_hour) >= 12 else "AM"
                    start_string = f"\t{start_hour_int}:{start_minute} {start_M}"

                    end_hour, end_minute, end_second, excess = time['end_time'].split('.')
                    end_hour_int = int(end_hour) if int(end_hour) <= 12 else int(end_hour) % 12
                    end_M = "PM" if int(end_hour) >= 12 else "AM"
                    end_hour, end_minute, end_second, excess = time['end_time'].split('.')
                    end_string = f"\t{end_hour_int}:{end_minute} {end_M}"
                    
                    print(f"\t{time['days']}")
                    print(start_string)
                    print(end_string)
    else:
        print(class_list.status_code)
        

def multi_class(subjects, URL, best):
    subjects = set(subjects)
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
            'term':'2202', # Term is a numerical representation of Spring/Summer/Fall/Winter term
            'subject':subject, # 4 letter abbreviation, i.e. KINE = Kinesiology
        }
        class_list = requests.get(url=URL, params=PARAMS)
        class_dict = class_list.json()
        if not bool(class_dict):
            print(f"Could not find abbreviation {subject}, skipping")
        for class_found in class_dict:
            for time in class_found['meetings']:
                start_hour = time['start_time'].split('.')[0]
                end_hour = time['end_time'].split('.')[0]
                days = re.findall(r'[A-Z][a-z]', time['days'])
                for day in days:
                    try:
                        start_hour_int = int(start_hour)
                        end_hour_int = int(end_hour)
                        times[day][start_hour_int] += 1
                        if start_hour_int != end_hour_int:
                            times[day][end_hour_int] += 1
                    except:
                        pass
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


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent('''\
        Query current CSU Chico course schedule

        Subject Abbreviations and Course Numbers available at:
        http://catalog.csuchico.edu/viewer/home
        '''))
    

    # Allow user to use Single class functions or multiclass functions
    subparsers = parser.add_subparsers(title="Valid Subcommands", help="Type of query, S = Single, M = Multi", dest="command", required=True)
    
    solo_parser = subparsers.add_parser("S")
    solo_parser.add_argument("name", nargs=1, type=str, help="Input class name and number. Format: CSCI-211")
    solo_parser.add_argument("-l", "--lab", help="Include lab sections", action="store_true")
    
    multi_parser = subparsers.add_parser("M")
    group2 = multi_parser.add_mutually_exclusive_group()
    group2.add_argument("-b", "--best", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")
    group2.add_argument("-w", "--worst", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")

    time_parse = subparsers.add_parser("T")
    time_parse.add_argument("time", help="Find how many classes start at a specific time. Format: 10:00 AM, or 2:00 PM", nargs=1, type=str, metavar="TIME")
    
    args = parser.parse_args()

    # CSU Chico class schedule search
    URL = "https://cmsweb.csuchico.edu/psc/CCHIPRD/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?"

    # Figure out which command they're using
    if args.command == "S":
        subject, catalog_nbr = args.name[0].split('-')
        single_class(subject, catalog_nbr, URL, args.lab)
    elif args.command == "M":
        if not bool(args.best) and not bool(args.worst):
            print("M command requires one of the two subcommands, -b or -w")
        else:
            multi_class((args.best if bool(args.best) else args.worst), URL, (True if bool(args.best) else False))
    elif args.command == "T":
        print("Time command implementation in progress")
        return
    else:
        print("Something went wrong", file=sys.stderr)
        return
    return




if __name__ == "__main__":
    main()