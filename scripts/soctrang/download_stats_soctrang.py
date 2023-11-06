"""Script to extract table from Tra Vinh url"""
import argparse
import json
import requests
from bs4 import BeautifulSoup
import time

processed_urls = []

def data_type_vietnamese(id):
    if id == 1:
        return "Nhiệt độ"
    if id == 2:
        return "Độ mặn"
    if id == 3:
        return "pH"
    if id == 4:
        return "Độ Kiềm"
    if id == 5:
        return "Độ trong"
    if id == 6:
        return "Dissolved Oxygen (DO)"
    if id == 7:
        return "Độ mặn so với năm trước"
    return "unknown"
   
def data_type_english(id):
    if id == 1:
        return "temperature"
    if id == 2:
        return "salinity"
    if id == 3:
        return "pH"
    if id == 4:
        return "alkalinity"
    if id == 5:
        return "transparency"
    if id == 6:
        return "oxygen"
    if id == 7:
        return "salinity comparison to previous year"
    return "unknown"
   
def data_unit(id):
    if id == 1:
        return "celcius"
    if id == 2:
        return "0/00"
    if id == 3:
        return "none"
    if id == 4:
        return "mg/l"
    if id == 5:
        return "cm"
    if id == 6:
        return "mg/l"
    if id == 7:
        return "+-"
    return "unknown"

def get_date(url):
    ds = url[url.find("Ngay-")+5:len(url)-6]
    separator_count = ds.count('-')
    if separator_count == 3:
        ds = ds[ds.find("-")+1:len(ds)].replace("-","/")
    if separator_count == 2:
        ds = ds.replace("-","/")
    if separator_count == 4:
        ds = ds[ds.find("-")+1:len(ds)]
        ds = ds[ds.find("-")+1:len(ds)].replace("-","/")
    return ds

def to_us_date(vn_date):
    year = vn_date[vn_date.rfind("/")+1:len(vn_date)]
    month = vn_date[vn_date.find("/")+1:vn_date.rfind("/")]
    day = vn_date[0:vn_date.find("/")]
    if len(month) < 2:
        month = "0" + month
    if len(day) < 2:
        day = "0" + day
    return year + "_" + month + "_" + day

def extract_table_url(url, output_path):
    global processed_urls
    if url not in processed_urls:
        print(f"Processing: {url}")
        processed_urls.append(url)
        vn_date = get_date(url)
        
        page = requests.get(url, timeout=60000)
        soup = BeautifulSoup(page.content, "html.parser")

        # Find the table on the page. Adjust the class_attribute if the table class is different.
        tables = soup.findAll("table")
        table = tables[2]

        if table is None:
            print("Cannot find a table in this website")
        else:
            # Create an empty list to store rows
            rows = []

            # Find all table rows
            for row in table.findAll("tr"):
                row_data = []
                for table_cell in row.findAll(["td", "th"]):  # Capture header (th) and data (td) cells
                    row_data.append(table_cell.get_text(strip=True))  # .get_text() extracts the text from the tags
                rows.append(row_data)
            
            # Print the extracted data
            result = {
                "date_created" : vn_date,
                "datetime_format" : "vietnamese",
                "data" : []
            }
            
            for row in rows[4:]:
                # sometime there is an extra empty column at the begining of the table               
                print(", ".join(row))
                if len(row) < 10:
                    print("-- SKIP ROW")
                else:
                    dic = {}
                    dic["location"] = row[2]
                    dic["time"] = row[1].replace("h",":")
                    for i in range(1,8):
                        dic[data_type_vietnamese(i)] = {
                            "value" : row[i+2].replace(",","."),
                            "unit"  : data_unit(i),
                            "name"  : data_type_english(i)
                        }
                    result["data"].append(dic)
                
        # save result to file
        output_full_path = output_path + "-" + to_us_date(vn_date) + ".json"
        print(f"Saving to {output_full_path}.")
        with open(output_full_path, "w", encoding="utf-8") as writer:
            json.dump(result, writer, ensure_ascii=False, indent=4)
    else:
        print(f"Already processed url: {url}")


def main():
    parser = argparse.ArgumentParser(description="Script to extract information table from province's url")
    parser.add_argument("--url", help="URL for extraction", default="")
    parser.add_argument("--input_path", help="File path which contains all the urls")
    parser.add_argument("--output_path", help="File path to save the extracted json", default="soctrang")
    args = parser.parse_args()

    if args.input_path:
        server = "https://sotuphap.soctrang.gov.vn"
        with open(args.input_path, "r") as reader:
            lines = reader.readlines()
            for line in lines:
                url = server + line
                url = url.strip()
                print(f"URL: {url}")
                extract_table_url(url, args.output_path)
    else:
        url = args.url
        if not url:
            url = input("Please input the url for extraction:")

        #extract the server address
        server = url[0:url.find("/mDefault")]
        print(f"Server: {server}")

        extract_table_url(url, args.output_path)


if __name__ == "__main__":
    main()
