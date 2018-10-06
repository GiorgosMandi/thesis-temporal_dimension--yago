import pandas as pd

import requests
import pickle
import time
import re
from bs4 import BeautifulSoup
from bs4 import element


try:
    with open("Kapodistria_scheme/Wiki_Object", 'rb') as wo:
        page = pickle.load(wo)
except FileNotFoundError:
    print("Request")
    page = requests.get("https://el.wikipedia.org/wiki/%CE%94%CE%B9%CE%BF%CE%B9%CE%BA%CE%B7%CF%84%CE%B9%CE%BA%CE%AE_%CE%B4%CE%B9%CE%B1%CE%AF%CF%81%CE%B5%CF%83%CE%B7_%CF%84%CE%B7%CF%82_%CE%95%CE%BB%CE%BB%CE%AC%CE%B4%CE%B1%CF%82_1997")
    if page.status_code == 200:
        with open("Kapodistria_scheme/Wiki_Object", 'wb') as wo:
            pickle.dump(page, wo)

region_counties = {}
counties_municipalities = {}

#gets the table from the html page
soup = BeautifulSoup(page.content, 'html.parser')
html = list(soup.children)[2]
main_table = html.find('table')
sub_tables = main_table.find_all('table')
data = sub_tables[0].find_all('td')

# NOTE: special treatment for Attica Region
r_key = data[0].get_text()
r_counties = []
for index, county in enumerate(data[2:]):
    if index%2 == 0:
        r_counties.append(county.get_text())
        c_key = county.get_text()
    else:
        print(county.get_text(),"\n")
        url = county.find('a',  href=True)
        munic_page = requests.get('https://el.wikipedia.org/'+url['href'])
        sub_soup = BeautifulSoup(munic_page.content, 'html.parser')
        sub_html = list(sub_soup.children)[2]
        municipalities_list = sub_html.find_all('ul')[1]
        municipalities_li = municipalities_list.find_all('li')
        municipalities = []
        for municipality in municipalities_li:
            municipality_str = municipality.get_text()
            municipality_str = re.sub('\d|-- | --|\.', '', municipality_str)
            municipalities.append(municipality_str)

        counties_municipalities[c_key] = pd.Series(municipalities)
region_counties[r_key] = pd.Series(r_counties)



for table in sub_tables[1:]:
    data = table.find_all('td')
    r_key = data[0].get_text()
    r_counties = []
    for index, county in enumerate(data[1:]):
        if index%2 == 0:
            r_counties.append(county.get_text())
            c_key = county.get_text()
        else:
            print(county.get_text(),"\n")
            url = county.find('a',  href=True)
            munic_page = requests.get('https://el.wikipedia.org/'+url['href'])
            sub_soup = BeautifulSoup(munic_page.content, 'html.parser')
            sub_html = list(sub_soup.children)[2]
            municipalities_list = sub_html.find_all('ul')[1]
            municipalities_li = municipalities_list.find_all('li')
            municipalities = []
            for municipality in municipalities_li:
                municipality_str = municipality.get_text()
                municipality_str = re.sub('\d|-- | --', '', municipality_str)
                municipalities.append(municipality_str)

            counties_municipalities[c_key] = pd.Series(municipalities)

    region_counties[r_key] = pd.Series(r_counties)


RC = pd.DataFrame(region_counties)
RC.to_csv("Kapodistria_scheme/Region_Counties.csv", sep='\t', columns=RC.columns)

CM = pd.DataFrame(counties_municipalities)
CM.to_csv("Kapodistria_scheme/Counties_Municipalities.csv", sep='\t', columns=CM.columns)
