import json
import requests
import argparse


def main():
    parser = argparse.ArgumentParser(description="Query current CSU Chico course schedule")

    subparsers = parser.add_subparsers(title="Valid Subcommands", help="Type of query, S = Single, M = Multi", dest="command", required=True)
    
    solo_parser = subparsers.add_parser("S")
    solo_parser.add_argument("name", nargs=1, type=str, help="Input class name. Format: CSCI-211")
    solo_parser.add_argument("-l", "--lab", help="Include lab sections", action="store_true")
    
    multi_parser = subparsers.add_parser("M")
    group2 = multi_parser.add_mutually_exclusive_group()
    group2.add_argument("-b", "--best", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")
    group2.add_argument("-w", "--worst", help="Find the best time for an event, given a list of Subject Abbreviations", nargs="+", metavar="SUBJECT")
    
    args = parser.parse_args()

    if args.command == "S":
        subject, catalog_nbr = args.name[0].split('-')
    elif args.command == "M":
        print("Multi-Class implementation still in progress")
        return
    else:
        print("Something went wrong")
        return

    URL = "https://cmsweb.csuchico.edu/psc/CCHIPRD/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?"

    PARAMS = {
        'institution':'CHICO',
        'term':'2202',
        'date_from':'',
        'date_thru':'',
        'subject':subject,
        'subject_like':'',
        'catalog_nbr':catalog_nbr,
        'time_range':'',
        'days':'',
        'campus':'',
        'location':'',
        'x_acad_career':'',
        'acad_group':'',
        'rqmnt_designtn':'',
        'instruction_mode':'',
        'keyword':'',
        'class_nbr':'',
        'acad_org':'',
        'enrl_stat':'',
        'crse_attr':'',
        'crse_attr_value':'',
        'instructor_name':'',
        'session_code':'',
        'units':'',
        'operationName':'',
        'variables':'',
        'query':''
    }
    class_list = requests.get(url=URL, params=PARAMS)
    if class_list.status_code == 200:
        class_dict = class_list.json()
        print(class_list)
        print(f"Search Results for {subject}-{catalog_nbr}")
        for counter, class_found in enumerate(class_dict):
            if class_found['component'] != "ACT" or args.lab:
                print("Section {}:".format(class_found['class_section']))
                for time in class_found['meetings']:
                    start_hour, start_minute, start_second, excess = time['start_time'].split('.')
                    start_hour_int = int(start_hour) if int(start_hour) <= 12 else int(start_hour) % 12
                    start_M = "PM" if int(start_hour) >= 12 else "AM"
                    start_string = f"\t{start_hour_int}:{start_minute} {start_M}"

                    end_hour, end_minute, end_second, excess = time['end_time'].split('.')
                    end_hour_int = int(end_hour) if int(end_hour) <= 12 else int(end_hour) % 12
                    end_M = "PM" if int(end_hour) >= 12 else "AM"
                    end_string = f"\t{end_hour_int}:{start_minute} {start_M}"
                    end_hour, end_minute, end_second, excess = time['end_time'].split('.')
                    
                    print(start_string)
                    print(end_string)
    else:
        print(class_list.status_code)
        

if __name__ == "__main__":
    main()