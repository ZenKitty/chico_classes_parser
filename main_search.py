import json
import requests
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query current CSU Chico course schedule")
    # parser.add_argument("command", type=str, nargs=1, help="""Desired command for the Parser""")
    parser.add_argument("-c", "--class", nargs=1, type=int, help="Search for a specific class. Format: CSCI-211")
    parser.add_argument("-l", "--lab", help="Include lab sections", action="store_true")
    args = parser.parse_args()

    URL = "https://cmsweb.csuchico.edu/psc/CCHIPRD/EMPLOYEE/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?"

    PARAMS = {
        'institution':'CHICO',
        'term':'2202',
        'date_from':'',
        'date_thru':'',
        'subject':'CSCI',
        'subject_like':'',
        'catalog_nbr':'211',
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
        for counter, class_found in enumerate(class_dict):
            if class_found['component'] != "ACT" or args.lab:
                print("Section {}:".format(class_found['class_section']))
                for time in class_found['meetings']:
                    start_hour, start_minute, start_second, excess = time['start_time'].split('.')
                    end_hour, end_minute, end_second, excess = time['end_time'].split('.')
                    print("\t{}:{}".format(int(start_hour)%12, start_minute))
                    print("\t{}:{}".format(int(end_hour)%12, end_minute))
    else:
        print(class_list.status_code)
        

