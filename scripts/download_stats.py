"""Script to extract table from Tra Vinh url"""
import argparse
import json
import requests
from bs4 import BeautifulSoup

processed_urls = []
server = ""

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

            # Print the extracted data
            result = {"data": []}
            for row in rows[2:]:
                if row[0]:
                    dic = {}
                    print(", ".join(row))
                    dic["location"] = row[1]
                    dic["salinity"] = {"value": row[2], "unit": "%"}
                    dic["ph"] = {"value": row[2], "unit": "ph"}
                    dic["alkalinity"] = {"value": row[3], "unit": "mg/l"}
                    dic["oxygen"] = {"value": row[4], "unit": "mg/l"}
                    dic["temperature"] = {"value": row[5], "unit": "celsius"}
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
            for link in soup.find_all('a'):
                other_day_url = link.get('href')
                if other_day_url is not None:
                    if "ket-qua-quan-trac-moi-truong-nuoc-ngay" in other_day_url:
                        extract_table_url(server+other_day_url,output_path)
    else:
        print(f"Already processed url: {url}")


def main():
    parser = argparse.ArgumentParser(description="Script to extract information table from province's url")
    parser.add_argument("--url", help="URL for extraction", default="")
    parser.add_argument("--output_path", help="File path to save the extracted json", default="travinh")
    args = parser.parse_args()

    url = args.url
    if not url:
        url = input("Please input the url for extraction:")

    #extract the server address
    global server
    server = url[0:url.find("/mDefault")]
    print(f"Server: {server}")

    extract_table_url(url, args.output_path)


if __name__ == "__main__":
    main()
