import logging
import re

import scrapy

from scrapy_shanghaicovid2022.items import InfectedNumberItem
from datetime import date, timedelta


class InfectednumberSpider(scrapy.Spider):
    name = 'InfectedNumber'

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
            cb_kwargs={'pub_date':d})
        requests.append(request)

        return requests

    def parse_page(self, response, pub_date):
        text = response.xpath('//strong')[1].xpath('text()').get()
        if text is None:
            text = response.xpath('//strong')[1].xpath('span')[0].xpath('text()').get()

        total_confimed = self.find(text, prefix='确诊病例')
        total_asymptomatic = self.find(text, prefix='本土无症状感染者')
        asymp_conf = self.find(text, suffix='例确诊病例为此前无症状感染者转归')
        control_confimed = self.find(text, suffix='例确诊病例和')
        if 0 == control_confimed:
            control_confimed = self.find(text, suffix='例确诊病例在隔离管控中发现')
        if 0 == control_confimed:
            control_confimed = self.find(text, suffix='例确诊病例均在隔离管控中发现')
        control_asymptomatic = self.find(text, suffix='例无症状感染者在隔离管控中发现')
        if 0 == control_asymptomatic:
            control_asymptomatic = self.find(text, suffix='例无症状感染者均在隔离管控中发现')
        social_confirmed = total_confimed - control_confimed - asymp_conf
        social_asymptomatic = total_asymptomatic - control_asymptomatic
        item = InfectedNumberItem()
        # the data published today is about the one of yesterday
        item['date'] = pub_date
        item['totalConfirmed'] = total_confimed
        item['totalAsymp'] = total_asymptomatic
        item['asympToConfimed'] = asymp_conf
        item['controlConfirmed'] = control_confimed
        item['controlAsymp'] = control_asymptomatic
        item['socialConfirmed'] = social_confirmed
        item['socialAsymp'] = social_asymptomatic
        item['totalControl'] = control_confimed + control_asymptomatic
        item['totalSocial'] = social_confirmed + social_asymptomatic

        yield item

    def find(self, text, prefix=None, suffix=None):
        pattern = ''
        if prefix is None:
            prefix = ''
        if suffix is None:
            suffix = ''
        pattern = prefix + '[0-9]+' + suffix

        p = re.compile(pattern)
        arr = p.findall(text)
        res = 0
        if len(arr) == 1:
            res = arr[0][len(prefix):]
            res = res[:len(res)-len(suffix)]
            res = int(res)
        return res