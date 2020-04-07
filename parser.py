import datetime
from collections import namedtuple

import bs4
import requests

InnerBlock = namedtuple('Block', 'title,price,date,url,place')


class Block(InnerBlock):

    def __str__(self):
        return f'{self.title} {self.place}  {self.price}  {self.date}\n{self.url}'


class AvitoParser:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
            'Accept-Language': 'ru',
        }

    def get_page(self, page: int = None, max_money: int = None):
        params = {
            'f': 'ASgBAQICAUSUA9AQAUDYCDTMWcpZzlk'
        }
        if page and page > 1:
            params['p'] = page
        if max_money:
            params['pmax'] = max_money
        url = 'https://www.avito.ru/kazan/doma_dachi_kottedzhi/prodam-ASgBAgICAUSUA9AQ'
        r = self.session.get(url, params=params)
        return r.text

    def parse_block(self, item):
        url_block = item.select_one('a.snippet-link')
        href = url_block.get('href')
        if href:
            url = 'https://www.avito.ru' + href
        else:
            url = None
        title_block = item.select_one('a.snippet-link').get('title')
        title = title_block.strip()
        price_block = item.select_one('span.snippet-price').get_text()
        price = price_block.strip()
        place_block = item.select_one('span.item-address__string').get_text()
        place = place_block.strip()
        date_block = item.select_one('div.snippet-date-info').get('data-tooltip')
        date = date_block.strip()
        return Block(
            title=title,
            price=price,
            place=place,
            date=date,
            url=url
        )

    def get_block(self, page: int = None):
        text = self.get_page(page=page, max_money=4000000)
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.snippet-horizontal.item.item_table.clearfix.js-catalog-item-enum.item-with-contact.js-item-extended')
        for item in container:
            block = self.parse_block(item=item)
            print(block)

    def get_pagination_limit(self):
        text = self.get_page(max_money=4000000)
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('span.pagination-item-1WyVp')
        last_pag = int(container[-2].get_text())
        return last_pag

    def parse_all(self):
        limit = self.get_pagination_limit()
        for i in range(1, limit+1):
            self.get_block(page=i)


def main():
    p = AvitoParser()
    p.parse_all()


if __name__ == '__main__':
    main()
