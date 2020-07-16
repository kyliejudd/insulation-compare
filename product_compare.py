import json
import csv
import re
from tabulate import tabulate

# we maintain a seperate reference file for info on pink batts. we can cross reference model numbers to obtain more info
data_batts = []
with open('pink_batts.csv') as csv_file:
    for row in csv.DictReader(csv_file, skipinitialspace=True):
        data_batts.append(row)

# regex magic to try and find square metres in product descriptions. 
unit_pattern = re.compile(r"[+-]? *((?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*(square meters|square metres|square meter|square metre|square m|square mt|sqmt|sq mt|sq.mt|sq. mt|sqm|sq m|sq.m|sq. m|meters2|metres2|meter2|metre2|mt2|m2|m²)", re.IGNORECASE)


attributes = [
              'type',
              'displayName',
              'price',
              'Model Number',
              'Colour',
              'Material',
              'Coverage Area (sq. Mtr.)',
              'R Value',
              'cost per sqm',
              'productUrl'
              ]

# try and find the total area per bale value of a pink batts product by model number
def find_details(modelnum):
    for line in data_batts:
        if line['code'] == modelnum:
            return float(line['tapbn'])

# try and find the r value of a pink batts product by model number
def find_r(modelnum):
    for line in data_batts:
        if line['code'] == modelnum:
            return line['rvalue']


def create_table(product_file):
    processed_items = []
    # loop through the data we have scraped and try and fill in missing data
    with open(product_file) as json_file:
        data = json.load(json_file)
        for line in data:
            line['type'] = product_file.split('.')[0]
            sqm = 0
            # not sure if a typo, sometimes the sq mtr is listed as sp. Mtr
            if 'Coverage Area (sp. Mtr.)' in line:
                line['Coverage Area (sq. Mtr.)'] = line['Coverage Area (sp. Mtr.)']
                del line['Coverage Area (sp. Mtr.)']
            # find the sq mtr coverage
            if 'Coverage Area (sq. Mtr.)' in line:
                sqm = float(line['Coverage Area (sq. Mtr.)'])
            # if missing and a pink batts product refer to additional data
            elif 'Pink' in line['displayName']:
                sqm = find_details(line['Model Number'])
            # last resort to get square metres, maybe its in the displayname
            else:
                str = re.findall(unit_pattern, line['displayName'])
                if str:
                    sqm = float(tuple(str[0])[0])
            # once we know the metres square we can use this to calculate price per m2
            if sqm:
                float_price = float(line['price'])
                line['Coverage Area (sq. Mtr.)'] = sqm
                line['cost per sqm'] = round(float_price / sqm, 2)
            # try and find R values from pink batt additional data
            if 'Pink' in line['displayName'] and 'R Value' not in line:
                r = find_r(line['Model Number'])
                line['R Value'] = r
            # try and extract value out of displayname
            if 'R Value' not in line:
                r = re.findall('R[0-9]..', line['displayName'])
                if r:
                    line['R Value'] = r[0]
            if 'productUrl' in line:
                line['productUrl'] = 'https://www.bunnings.co.nz' + line['productUrl']
            # build a new dictionary based on attributes we want.
            item = {}
            for a in attributes:
                if a in line:
                    item[a] = line[a]
                else:
                    item[a] = 'not found'

            processed_items.append(item)
    header = attributes
    rows = [x.values() for x in processed_items]
    print(tabulate(rows, header))
    print('\n')

for file in ['wall.json', 'ceiling.json', 'underfloor.json']:
    create_table(file)