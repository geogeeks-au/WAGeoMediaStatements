import scrapy
from ..items import MediaStatement
import logging
import requests

class WAMediaStatementSpider(scrapy.Spider):
    name = "wams"
    allowed_domains = ["mediastatements.wa.gov.au"]
    start_urls = [
        "https://www.mediastatements.wa.gov.au/Pages/Default.aspx",
        "https://www.mediastatements.wa.gov.au/Archived-Statements/Pages/By-Government-Carpenter-Labor-Government.aspx",
        "https://www.mediastatements.wa.gov.au/Archived-Statements/Pages/By-Government-Gallop-Labor-Government.aspx",
        "https://www.mediastatements.wa.gov.au/Archived-Statements/Pages/By-Government-Court-Coalition-Government.aspx",
        "https://www.mediastatements.wa.gov.au/Archived-Statements/Pages/By-Government-Lawrence-Labor-Government.aspx"
    ]
    page_num = 1



    def parse(self, response):
        if not response:
            return
        table = response.xpath('//table/tr')
        for row in table:
            table_row = row.xpath('td/p/text()').extract()
            # Still might need to skip the top
            if not len(table_row):
                continue
            media_item = MediaStatement()
            media_item['date'], media_item['minister'], media_item['portfolio'] = table_row

            media_item['title'] = row.xpath('td/a/text()').extract()[0]
            logging.info(media_item['title'])
            media_item['link'] = response.urljoin(row.xpath('td/a/@href').extract()[0])
            request = scrapy.Request(media_item['link'], callback=self.parse_media_statement)
            request.meta['item'] = media_item
            yield request
            # Probabley check this was ok parsed_statement

        self.page_num += 1
        url = response.urljoin("?QualitemContentRollupPage={page_num}&".format(page_num=self.page_num))
        r = requests.get(url)
        tr = scrapy.http.TextResponse(r.text, r.encoding)
        if r.ok and tr.xpath('//table/tr') == table:
            return
        yield scrapy.Request(url, callback=self.parse)

        # Get next page xpath(//ul//li//a//text().extract() == "Next"
        # Might just have to use the url + QualitemContentRollupPage={page_num}&
        #for links in response.xpath('//ul'):
        #    print "Links {}".format(links.xpath('li/a/text()').extract())
        #    if links.xpath('li/a/text()').extract() == u"Next":
        #        follow_link = links.xpath('li/a/@href')[0].extract()
        #        follow_url = response.urljoin(follow_link)
        #        print follow_url

    def parse_media_statement(self, response):
        media_item = response.meta['item']
        for sel in response.xpath('//body'):
            # heading = sel.xpath('//h1/text()').extract()[0]
            # drop u'\xa0' and join on stuff
            stuff = sel.xpath('//div[@class="ms-rtestate-field"]/p/text()').extract()
            if not stuff:
                stuff = sel.xpath('//div[@class="ms-rtestate-field"]/font/text()').extract()
            media_item['statement'] = " ".join([x for x in stuff if x != u'\xa0'])
            yield media_item

