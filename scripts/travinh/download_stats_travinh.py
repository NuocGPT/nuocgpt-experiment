"""Script to extract table from Tra Vinh url"""
import argparse
import json
import requests
from bs4 import BeautifulSoup

# mapping function for Vietnamese sensoring data name
def data_type_english_name(vietnamese_name):
    if "mặn" in vietnamese_name or "Mặn" in vietnamese_name:
        return "salinity"
    if "pH" in vietnamese_name or "ph" in vietnamese_name:
        return "pH"
    if "Kiềm" in vietnamese_name or "kiềm" in vietnamese_name:
        return "alkalinity"
    if "Oxy" in vietnamese_name or "oxy" in vietnamese_name:
        return "oxygen"
    if "Nhiệt" in vietnamese_name or "nhiệt" in vietnamese_name:
        return "temperature"
    if "NH4" in vietnamese_name or "nh4" in vietnamese_name:
        return "NH4/NH3"
    return "unknown"

def data_unit(vietnamese_name):
    if "mặn" in vietnamese_name or "Mặn" in vietnamese_name:
        return "0/00"
    if "pH" in vietnamese_name or "ph" in vietnamese_name:
        return "none"
    if "Kiềm" in vietnamese_name or "kiềm" in vietnamese_name:
        return "mg/l"
    if "Oxy" in vietnamese_name or "oxy" in vietnamese_name:
        return "mg/l"
    if "Nhiệt" in vietnamese_name or "nhiệt" in vietnamese_name:
        return "celcius"
    if "NH4" in vietnamese_name or "nh4" in vietnamese_name:
        return "mg/l"
    return "unknown"


processed_urls = []
server = "https://travinh.gov.vn"

def extract_table_url(url, output_path):
    global processed_urls
    if url not in processed_urls:
        print(f"Processing: {url}")
        processed_urls.append(url)

        page = requests.get(url, timeout=60000)
        soup = BeautifulSoup(page.content, "html.parser")

        # Find the table on the page. Adjust the class_ attribute if the table class is different.
        table = soup.find("table")

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
                print(row_data)
                
            # Print the extracted data
            result = {"data": []}
            for row in rows[2:]:
                # sometime there is an extra empty column at the begining of the table
                i = 1
                if not row[0]:
                    i = 2
                    
                if row[i]:
                    print(", ".join(row))
                    dic = {}
                    dic["location"] = row[i]

                    for column_header in rows[1]:
                        i = i + 1
                        dic[column_header] = {"value": row[i].replace(",","."), "unit": data_unit(column_header), "name" : data_type_english_name(column_header)}
                
                    result["data"].append(dic)

            # date created
            date_string = soup.find("div", class_="DateCreate").contents[0].replace("Ngày ", "")
            result["date_created"] = date_string
            result["datetime_format"] = "vietnamese"

            output_full_path = output_path + "-" + date_string.replace("/","_") + ".json"

            # save to file
            # print(result)
            print(f"Saving to {output_full_path}.")
            with open(output_full_path, "w", encoding="utf-8") as writer:
                json.dump(result, writer, ensure_ascii=False, indent=4)

            # grab the links to other pages with results of other days
            #for link in soup.find_all('a'):
            #    other_day_url = link.get('href')
            #    if other_day_url is not None:
            #        if "ket-qua-quan-trac-moi-truong-nuoc-ngay" in other_day_url:
            #            extract_table_url(server+other_day_url,output_path)
    else:
        print(f"Already processed url: {url}")


def main():
    parser = argparse.ArgumentParser(description="Script to extract information table from province's url")
    parser.add_argument("--url", help="URL for extraction", default="")
    parser.add_argument("--input_path", help="File path which contains all the urls")
    parser.add_argument("--output_path", help="File path to save the extracted json", default="travinh")
    args = parser.parse_args()

    if args.input_path:
        server = "https://travinh.gov.vn"
        with open(args.input_path, "r") as reader:
            lines = reader.readlines()
            for line in lines:
                url = server + line
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
