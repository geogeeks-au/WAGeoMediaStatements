import scrapy
from ..items import MediaStatement

class WAMediaStatementSpider(scrapy.Spider):
    name = "wams"
    allowed_domains = ["mediastatements.wa.gov.au"]
    start_urls = [
        "https://www.mediastatements.wa.gov.au/Pages/Default.aspx",
    ]

    def parse(self, response):
        for row in response.xpath('//table/tr'):
            table_row = row.xpath('td/p/text()').extract()
            # Still might need to skip the top
            if not len(table_row):
                continue
            media_item = MediaStatement()
            media_item['date'], media_item['minister'], media_item['portfolio'] = table_row

            media_item['title'] = row.xpath('td/a/text()').extract()
            media_item['link'] = row.xpath('td/a/@href').extract()
            yield media_item