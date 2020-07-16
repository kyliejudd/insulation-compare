import requests
import time
import json
from bs4 import BeautifulSoup

bunnings_site = 'https://www.bunnings.co.nz'
bunnings_uri = [
    '/our-range/building-hardware/insulation/underfloor-insulation',
    '/our-range/building-hardware/insulation/wall-insulation',
    '/our-range/building-hardware/insulation/ceiling-insulation'
]

class Insulation:
    """an attempt to create insulation object"""
    def __init__(self, insulation_type):
        self.insulation_type = insulation_type

    def get_product_url(self):
        #returns the url of the product you are looking for
        if self.insulation_type == 'underfloor':
            product_url = bunnings_site + bunnings_uri[0]
            return product_url
        elif self.insulation_type == 'wall':
            product_url = bunnings_site + bunnings_uri[1]
            return product_url
        elif self.insulation_type == 'ceiling':
            product_url = bunnings_site + bunnings_uri[2]
            return product_url
        else:
            exit(127)

    def get_products(self):
        # returns list of items found on page
        product_list = []
        site = self.get_product_url()
        html = requests.get(site)
        soup = BeautifulSoup(html.content, 'html.parser')
        results = soup.find_all('div', class_='js-product-tile-container')
        for result in results:
            contents = result['data-options']
            jdump = json.loads(contents)
            add_to_list = jdump['data']
            product_list = product_list + add_to_list
        print(len(product_list))
        return product_list

    def get_product_details(self):
        # drilling into the specification section of each product found in get_products()
        products = self.get_products()
        appended_products = []
        for product in products:
            time.sleep(0.5)  # little break to stop smashing the site.
            product_url = bunnings_site + product['productUrl']
            product_page = requests.get(product_url)
            product_soup = BeautifulSoup(product_page.content, 'html.parser')
            product_details = product_soup.find('div', class_="product-detail__table js-pdp-accordion-specification")[
                'data-options']
            product_details_json = json.loads(product_details)
            product_details_json = product_details_json['availableSpecifications']
            for detail in product_details_json:
                key = (detail['Key'])
                value = (detail['Value'])
                product[key] = value
            appended_products.append(product)
        return appended_products



def create_product_list(insulation_type):
    products = Insulation(insulation_type)
    product_details = products.get_product_details()
    with open('{}.json'.format(insulation_type), 'w') as f:
        json.dump(product_details, f)


for product in ['wall', 'ceiling', 'underfloor']:
    create_product_list(product)
