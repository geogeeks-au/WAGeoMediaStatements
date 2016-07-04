import scrapy
from ..items import Minister
import logging
import sys

class WAMediaStatementSpider(scrapy.Spider):
    name = "wamins"
    allowed_domains = ["parliament.wa.gov.au"]
    start_urls = [
        "http://www.parliament.wa.gov.au/parliament/memblist.nsf/wallmembers",
        "http://www.parliament.wa.gov.au/parliament/memblist.nsf/WAllRetiredMembers"
    ]
    page_num = 1


    def parse(self, response):
        """
        Parses a the media statements page.
        @url https://www.mediastatements.wa.gov.au/Pages/Default.aspx
        @returns item 1 100
        @returns requests 1
        @scrapes date minister portfolio title statement
        """
        # The page for retired members is slightly different
        retired = False
        if not response:
            return
        table = response.xpath('//table')[2].xpath('table/tr')
        if not table:
            table = response.xpath('//table')[1].xpath('tr')
            retired = True
        for row in table:
            minister_item = Minister()
            first_names = row.xpath('td/font/a/text()')
            if first_names:
                minister_item = Minister()
                minister_item['first_name'] = first_names.extract()[0]
            else:
                continue
            if not retired:
                minister_item['email'] = row.xpath('td/font/a/text()').extract()[1]
                minister_item['office_address'] = ", ".join([add.strip('\n ') for add in
                                                             row.xpath('td/font/text()')[1:].extract()
                                                             if "Ph" not in add and "Fax" not in add and
                                                             "Email" not in add and "Office" not in add
                                                             and "Website" not in add and
                                                             "Freecall" not in add and "Postal" not in add])
                minister_item['electorate'] = row.xpath('td/font/font/text()').extract()[0].lstrip("Electorate: ")
                minister_item['party'] = row.xpath('td/font/font/text()').extract()[1].lstrip("Party: ")
                position = row.xpath('td/font/font/i/text()')
                if position:
                    minister_item['position'] = position[0].extract()
            else:
                minister_item['electorate'] = row.xpath('td/font/font/font/text()').extract()[0].strip(
                    'Electorate: Former Member for the Electorate of ')
                minister_item['party'] = row.xpath('td/font/font/font/text()').extract()[1].lstrip('Party: ')
            minister_item['page'] = response.urljoin(row.xpath('td/font/a/@href').extract()[0])
            # Still might need to skip the top
            minister_item['last_name'] = row.xpath('td/font/a/b/text()').extract()[0]
            minister_item['house'] = row.xpath('td/font/text()')[0].extract().strip('\n ')

            logging.info(minister_item['last_name'])

            yield minister_item
            # Probably check this was ok parsed_statement
