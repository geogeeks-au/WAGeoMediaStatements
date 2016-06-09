import scrapy
from ..items import MediaStatement
from polyglot.text import Text
import geocoder

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
            media_item['link'] = row.xpath('td/a/@href').extract()[0]
            yield scrapy.Request(response.urljoin(media_item['link']), callback=self.parse_media_statement)

        # Get next page xpath(//ul/li/a/text().extract() == "Next"
        # Might just have to use the url + QualitemContentRollupPage={page_num}&
        for links in response.xpath('//ul'):
            print links
            print "Links {}".format(links.xpath('li/a/text()').extract())
            if links.xpath('li/a/text()').extract() == u"Next":
                follow_link = links.xpath('li/a/@href')[0].extract()
                follow_url = response.urljoin(follow_link)
                print follow_url

    def parse_media_statement(self, response):
        for sel in response.xpath('//body'):
            title = sel.xpath('//h1/text()').extract()
            # drop u'\xa0' and join on stuff
            stuff = sel.xpath('//div[@class="ms-rtestate-field"]/p/text()').extract()
            statement = " ".join([x for x in stuff if x != u'\xa0'])
            print "Processing statement {}".format(title)
            text = Text(statement)
            # For all I-LOC make an attempt to geocode but restrict to WA
            locations = set([" ".join(e) for e in text.entities if e.tag == u'I-LOC'])
            geocoded = []
            for loc in locations:
                if loc not in ["WA", "Western Australia"]:
                    g = geocoder.google(loc, components="country:AU")
                    accuracy = g.accuracy
                    address = g.address
                    geom = g.geometry
                    geocoded.append((accuracy,address,geom))