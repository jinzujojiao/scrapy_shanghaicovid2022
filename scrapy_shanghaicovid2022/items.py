# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyShanghaicovid2022Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class InfectedNumberItem(scrapy.Item):
    date = scrapy.Field()
    totalControl = scrapy.Field()
    totalSocial = scrapy.Field()
    totalConfirmed = scrapy.Field()
    totalAsymp = scrapy.Field()
    asympToConfimed = scrapy.Field()
    controlConfirmed = scrapy.Field()
    controlAsymp = scrapy.Field()
    socialConfirmed = scrapy.Field()
    socialAsymp = scrapy.Field()

class RiskLevelItem(scrapy.Item):
    date = scrapy.Field()
    addresses = scrapy.Field()