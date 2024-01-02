import argparse
import requests
from bs4 import BeautifulSoup
from urllib.request import urlretrieve

def get_report(url, output_path):
    page = requests.get(url, timeout=60000)
    soup = BeautifulSoup(page.content, "html.parser")

    # Find the report on the page
    for link in soup.find_all('a'):
        report_url = link.get('href')
        if report_url is not None:
            if ".pdf" in report_url:
                print(report_url)
                file_name = report_url[report_url.rfind('/')+1:report_url.len()]
                urlretrieve(report_url,file_name)      

def main():
    parser = argparse.ArgumentParser(description="Script to extract information table from province's url")
    parser.add_argument("--url", help="URL for extraction", default="")
    parser.add_argument("--input_path", help="File path which contains all the urls")
    parser.add_argument("--output_path", help="File path to save the extracted json", default="nchmf_data")
    args = parser.parse_args()

    if args.input_path:
        with open(args.input_path, "r") as reader:
            lines = reader.readlines()
            for line in lines:
                url = line.strip()
                print(f"URL: {url}")
                get_report(url, args.output_path)
    else:
        url = args.url
        if not url:
            url = input("Please input the url for extraction:")

        get_report(url, args.output_path)