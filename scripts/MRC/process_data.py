import argparse
import os
import json

parameters = {
    "Total" : {"count" : 0, "within 3 years": 0, "3-5 years" : 0, "5-10 years": 0, "older than 10 years" : 0}
}

def set_age(parameter,end_year):
    global parameters
    parameters["Total"]["count"] += 1
    parameters[parameter]["count"] += 1

    if 2023 - end_year <= 3:
        parameters[parameter]["within 3 years"] += 1
        parameters["Total"]["within 3 years"] += 1
    else: 
        if 2023 - end_year <= 5:
            parameters[parameter]["3-5 years"] += 1
            parameters["Total"]["3-5 years"] += 1
        else:
            if 2023 - end_year <= 10:
                parameters[parameter]["5-10 years"] += 1
                parameters["Total"]["5-10 years"] += 1
            else:
                parameters[parameter]["older than 10 years"] += 1
                parameters["Total"]["older than 10 years"] += 1


def extract_metadata(file_path):
    global parameters
    value_parameter = ""
    location = ""
    start_date = ""
    end_date = ""
    start_year = 0
    end_year = 0
    with open(file_path, "r") as reader:
        lines = reader.readlines()
        for line in lines:
            if "Value parameter:" in line:
                value_parameter = line[line.find(":")+2:len(line)-1]

            if "Location identifier" in line:
                location = line[line.find("VN_"):len(line)-1]
            if "Export options" in line:
                start_date = line[line.find("from ")+5:line.find("T",line.find("from "))]
                start_year = int(start_date[0:4])
                end_date = line[line.find("to ")+3:line.find("T",line.find("to "))]
                end_year = int(end_date[0:4])
    
    if value_parameter not in parameters.keys():
        parameters[value_parameter] = {"count" : 0, "within 3 years": 0, "3-5 years" : 0, "5-10 years": 0, "older than 10 years" : 0}

    # print(f"Location: {location} | Start date: {start_date} | End date: {end_date} | Parameter: {value_parameter}")
    set_age(value_parameter,end_year)
    if 2023 - end_year <= 3:
        return True

def csv_file_to_json(file_path, file_name, output_dir):
    result = {
        "Parameter" : file_name[0:file_name.find('.')],
        "Location"  : file_name[file_name.find('[')+1:file_name.find(']')],
        "Station Code" : file_name[file_name.find('_')+1:file_name.find("_[")],
        "Unit" : "",
        "Data" : []
    }
    with open(file_path, "r") as reader:
        lines = reader.readlines()
        result["Unit"] = lines[1].split(",")[6]
        for i in range(1,len(lines)):
            values = lines[i].split(",")
            result["Data"].append({"Time" : values[4], "Value" : values[5]})

    # save result to file
    output_full_path = os.path.join(output_dir,file_name + ".json")
    with open(output_full_path, "w", encoding="utf-8") as writer:
        json.dump(result, writer, ensure_ascii=False, indent=4)



def main():
    parser = argparse.ArgumentParser(description="Script to extract information from meta-data files of data sets bought from MRC")
    parser.add_argument("--input_path", help="Directory path which contains data files", default="Data")
    parser.add_argument("--output_path", help="File path to save the extracted meta-data", default="json")
    args = parser.parse_args()

    global parameters
    global csv_files
    if args.input_path:
        dir_path = args.input_path
        print(f"Input directory: {dir_path}")
        print(f"Ouput directory: {args.output_path}")
        for file_path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, file_path)):
                if "metadata" in file_path:
                    # print(file_path)
                    if extract_metadata(os.path.join(dir_path, file_path)) == True:
                        csv_file_to_json(os.path.join(dir_path, file_path[0:file_path.find("__metadata")]+".csv")
                                         ,file_path[0:file_path.find("__metadata")],args.output_path)

        for para in parameters.keys():
            print(f"\n{para} : {parameters[para]}")

    else:
        print("There is no input directory entered")

if __name__ == "__main__":
    main()