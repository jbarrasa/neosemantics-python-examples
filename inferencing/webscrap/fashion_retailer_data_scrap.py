import requests
from bs4 import BeautifulSoup
import csv
import os

HOME_URL = "https://www.next.co.uk/"
data_dir_name = 'data'


def parse_item(url, brandName):
    r = requests.get(url)

    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('section', attrs={'class': 'ProductDetail'})

    product = {}
    if table is not None:
        article = table.findAll('article')[0]
        product['url'] = url
        product['itemId'] = article['id']
        product['itemName'] = article['data-itemname']
        product['brandName'] = brandName
        # the following two  are not always available so there'll be 'NOT_IN_USE'
        product['itemDepartmemnt'] = article['data-department']
        product['itemCategory'] = article['data-category']
        productComposition = table.findAll('div', attrs={'id': 'Composition'})
        if productComposition:
            product['itemComposition'] = productComposition[0].text

        # not always available
        productPairings = []
        styleWithSection = table.find('ul', attrs={'class': 'sw-slider__items-list'})
        if styleWithSection is not None:
            for row in styleWithSection.findAll('li', attrs={'class': 'sw-slider__items-list-item'}):
                productPairings.append(row.a['href'])
            product['itemPairing'] = productPairings

    return product


f = open(os.path.join(data_dir_name, 'next_products.csv'), 'w')
w = csv.DictWriter(f, fieldnames=['url', 'itemId', 'itemName', 'brandName', 'itemDepartmemnt', 'itemCategory',
                                  'itemComposition', 'itemPairing'], quoting=csv.QUOTE_ALL)
w.writeheader()

url = HOME_URL + "brands/all"
r = requests.get(url)
brandsPage = BeautifulSoup(r.content, 'html.parser')
for brand in brandsPage.findAll('div', attrs={'class': 'bp-brand-name'}):
    print("Getting products for brand: " + brand.a.text)
    products = []
    r = requests.get('http:' + brand.a['href'])
    soup = BeautifulSoup(r.content, 'html.parser')
    for row in soup.findAll('article'):
        products.append(parse_item('http:' + row.section.div.h2.a['href'], brand.a.text))
    for c in products:
        w.writerow(c)
