import json
import validators
import scrapy
from scrapy.crawler import CrawlerProcess
from ..items import Job as Job_item


class YcSpider(scrapy.Spider):
    name = 'yc'
    allowed_domains = ['ycombinator.com']
    start_urls = ['https://news.ycombinator.com/jobs']
    pages_to_crawl = 20
    pages_scraped = 0
    job_links = []

    def parse(self, response):
        jobs = []
        table = response.xpath('//table[@class="itemlist"]')
        rows = table.xpath('.//tr[@class="athing"]')
        for row in rows:
            link = row.xpath('.//span[@class="titleline"]/a/@href').extract_first()
            jobs.append(link)
        self.job_links.extend(jobs)
        next_page = response.xpath('//a[@class="morelink"]/@href').extract_first()
        if next_page is not None:
            next_page = next_page.split('jobs')[1]
            next_page = response.urljoin(next_page)
            self.pages_scraped += 1
            if self.pages_scraped < self.pages_to_crawl:
                yield scrapy.Request(next_page, callback=self.parse)
            else:
                for job in self.job_links:
                    if validators.url(job):
                        yield scrapy.Request(job, callback=self.parse_job)
        else:
            for job in self.job_links:
                if validators.url(job):
                    yield scrapy.Request(job, callback=self.parse_job)

    def parse_job(self, response):
        Job = Job_item()
        json_data = response.xpath('/html/body/script[2]/text()').extract_first()
        job = json.loads(json_data).get('job')
        if job is not None:
            Job['job_id'] = job.get('id')
            Job['title'] = job.get('title').strip()
            Job['location'] = job.get('location')
            Job['company'] = job.get('companyName')
            yield Job