import scrapy
import re

module_id_pattern = r'([A-Z]{2}\d{4})'
lehrveranstaltungen_pattern = r'([A-Z]{2}.*)?: (.*) \((.*),.*([0-9]).*\)'

def get_elements_of_section(response, section_heading):
    table = response.xpath(f'//td[contains(h5/text(), "{section_heading}")]')    
    elements = table.xpath('.//li/text()').getall()
    if len(elements) == 0:
        elements = table.xpath('./text()').getall()
    return elements

class ModuleSpider(scrapy.Spider):
    name = 'uniluebeck'
    allowed_domains = ['uni-luebeck.de']
    start_urls = ['https://www.uni-luebeck.de/studium/studiengaenge/informatik/master/modulhandbuch/modulhandbuch-ab-ws-201920.html?draft=1']

    def parse(self, response):
        for href in response.xpath('//div[@id="No1"]//a/@href').getall():
            yield scrapy.Request(response.urljoin(href), self.parse_module)

    def parse_module(self, response):
        h1 = response.xpath('//h1/text()').re_first(module_id_pattern)        
        h2 = response.xpath('//h2/text()').get()       

        dauer = get_elements_of_section(response, 'Dauer:')[0]
        angebotsturnus = get_elements_of_section(response, 'Angebotsturnus:')[0]
        leistungspunkte = get_elements_of_section(response, 'Leistungspunkte:')[0]
        pruefungsart = get_elements_of_section(response, 'Benotung durch:')[0]

        veranstaltungen = get_elements_of_section(response, 'Lehrveranstaltungen:')
        items = []
        for veranstaltung in veranstaltungen:
            veranstaltung = veranstaltung.replace('siehe', '').replace('Siehe', '').strip()
            if ':' not in veranstaltung:
                veranstaltung = ': ' + veranstaltung
            groups = re.match(lehrveranstaltungen_pattern, veranstaltung).groups()
            item = dict(zip(['id', 'name', 'type', 'SWS'], groups))
            items.append(item)        
        
        yield {
            'id': h1,
            'name': h2,
            'dauer': dauer,
            'turnus': angebotsturnus,
            'ects': leistungspunkte,
            'consists_of': items,
            'pruefung': pruefungsart
            }