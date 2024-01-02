Store Python scripts to process data gathered from different sources.

### Mekong River Commission (MRC)

**Type**: Purchased

**URL**: https://portal.mrcmekong.org/time-series

**File format**:

1. Metadata: .txt
2. Location: .kml
3. Data points: .csv

**Scripts**:

1. File name: process_data.py
2. Input: directory path containing the meta-data & data files.
3. Output: directory where JSON output files are stored.
4. Description:
   - Go over all the meta-data files in the directory. For each meta-data file:
	   - read the relevant meta-data fields from the file
	   - read the data points from the corresponding .csv file if the meta-data satisfy certain criteria (e.g., the latest collection time is within 3 years)
	   - create the JSON file based the data points and some certain meta-data.
   - Output the statistics on all files based on values read from all meta-data files.

### Soc Trang

**Type**: Free (publicly available on the web)

**URL** (example): https://sotuphap.soctrang.gov.vn/snnptnt/1282/30591/53960/371205/Thong-tin-phuc-vu-San-xuat-Nong-nghiep/THONG-BAO-KET-QUA-QUAN-TRAC-MOI-TRUONG-Tuan-33--Ngay-7-8-8-2023-.aspx

**Script 1**: Gathering relevant URLs


1. File name: *gather\_urls\_soctrang.py*
2. Input: an exampple URL where one day of data is presented. Ideally should use the latest day that data was released (should be linked at the bottom of any example day)
3. Output: a text file with all URLs on Soc Trang's server of all the reports.
4. Description:
	- Use Selenium package to simulate webpage navigation using Webdriver (such as Chromium).
	- Find all links in the page with particular name in the URL (e.g., "BAO-KET-QUA-QUAN-TRAC-MOI-TRUONG"
	- Find a particular link on page (with particular name) that lead to a new page, then simulate click on that link to go to a new page and repeat the process.

**Script 2**: Extracting the data from each page URL gathered by **Script 1**, then store the extracted data in a new JSON file.

1. File name: *download\_starts\_soctrang.py*
2. Input: Text file with each line representing a file located on the Soc Trang's server.
3. Output: JSON file of sensory data (stored in a table) in the HTML file.


### Tra Vinh

Very similar to Soc Trang. Basically containing two files that: (1) gathering the URLs; (2) extracting data table and convert it to JSON.

Differences: (1) servers; (2) HTML file structure; (3) table structure.

**URL** (example): https://travinh.gov.vn/mDefault.aspx?sid=1444&pageid=6591&catid=71012&id=693472&catname=ket-qua-quan-trac-moi-truong-nuoc&title=ket-qua-quan-trac-moi-truong-nuoc-ngay-15-8-2023-tren-dia-ban-tinh-tra-vinh


### National Centre for Hydro-Mêtorological Forecasting (NCHMF)

(Tổng Cục Khí Tượng Thủy Văn - Trung Tâm Dự Báo Khí Tượng Thủy Văn Quốc Gia)

