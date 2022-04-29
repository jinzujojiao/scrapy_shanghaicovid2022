import logging
from datetime import date, timedelta

import scrapy

from scrapy_shanghaicovid2022.items import RiskLevelItem


class SjrisklevelspiderSpider(scrapy.Spider):
    name = 'SJRiskLevelSpider'

    def start_requests(self):
        url = getattr(self, 'url')
        if url is None:
            logging.error("Url is empty")
            exit

        # by default, the data published today is about the one of yesterday
        d = date.today() - timedelta(days=1)
        # date format is: yyyy/mm/dd
        datestr = getattr(self, 'date', None)
        if datestr is not None:
            arr = datestr.split('/')
            d = date(int(arr[0]), int(arr[1]), int(arr[2]))

        requests = []
        request = scrapy.Request(
            url,
            callback=self.parse_page,
            cb_kwargs={'pub_date': d})
        requests.append(request)

        return requests

    def parse_page(self, response, pub_date):
        is_found = False
        miss_table = False
        span_list = []
        table_list = []
        sections = response.xpath('//div[@id="js_content"]/section[@data-id="93396" or @data-role="paragraph"]')
        for section in sections:
            if section.xpath('@data-id').get() is not None:
                street = section.xpath('descendant::section[@data-brushtype="text"]/text()').get()
                if '九里亭街道' == street:
                    is_found = True
                elif is_found:
                    break
            else:
                spans = section.xpath('descendant::strong/span')
                tables = section.xpath('descendant::table')
                table_idx = 0
                if miss_table:
                    table_list.append(tables[0])
                    table_idx = 1
                    miss_table = False
                is_break = False
                len_table = len(tables)
                for span in spans:
                    text = span.xpath('text()').get()
                    print(text)
                    if is_found:
                        if '封控区' == text or '管控区' == text or '防范区' == text:
                            print(span.get())
                            span_list.append(span)
                            if table_idx >= len_table:
                                miss_table = True
                            else:
                                print(tables[table_idx].get())
                                table_list.append(tables[table_idx])
                                table_idx += 1
                        else:
                            is_break = True
                            break
                    elif '九里亭街道' == text:
                        is_found = True
                    elif '封控区' == text or '管控区' == text or '防范区' == text:
                        table_idx += 1
                if is_break:
                    break
        i = 0
        addresses = {}
        for span in span_list:
            table = table_list[i]
            level = span.xpath('text()').get()
            tds = table.xpath('descendant::td')
            j = 2
            l = len(tds)
            while j < l:
                addresses[tds[j+1].xpath('span/text()').get()] = level
                j += 2
            i += 1

        item = RiskLevelItem()
        item['date'] = pub_date
        item['addresses'] = addresses

        yield item