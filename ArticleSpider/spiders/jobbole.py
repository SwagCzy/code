# -*- coding: utf-8 -*-
import scrapy
import re
import datetime
from scrapy.http import Request
from urllib import parse

from ArticleSpider.items import JobBoleArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
from scrapy.loader import ItemLoader

class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1.获取文章列表页中的文章url并交给scrapy下载后进行解析
        2.获取下一页的url并交给scrapy进行下载，下载完成后交给parse
        """
        # post_url = response.css('#archive .floated-thumb .post-thumb a::attr(href)')
        post_nodes=response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            image_url=post_node.css('img::attr(src)').extract_first('')
            post_url=post_node.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url,post_url),meta={'front_image_url':image_url},callback=self.parse_detail)     #将文章url具体详情交给scrapy
            #urjoin()的优势在于若post_url没有域名，就从response中提取出来给它，若有域名，则没有影响
            #提取下一页并交给scrapy进行下载
        next_url=response.css('.next.page-numbers::attr(href)').extract_first('')
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)   #返回为列表型url，继续执行parse（）
                #request()用于生成response


    def parse_detail(self, response):
        article_item =JobBoleArticleItem()
        #调用text（）只获取标签内的内容，不获取标签
        # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first()  #extract_first自带空字符异常处理,且为字符串形式
        # create_date=response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace('·', ' ').strip()
        # praise_num=response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()[0]
        # fav_num = response.xpath('//span[contains(@class,"bookmark-btn")]/text()').extract()[0]
        # match_re=re.match('.*？(\d+).*',fav_num)
        # if match_re:
        #     fav_num=int(match_re.group(1))
        # else:
        #     fav_num=0
        #
        # comment_num= response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        # match_re=re.match('.*？(\d+).*',comment_num)
        # if match_re:
        #     commment_num=int(match_re.group(1))
        # else:
        #     comment_num=0
        #
        # content=response.xpath('//div[@class="entry"]').extract()[0]
        #
        # tag_list= response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags=','.join(tag_list)        #','.join（）将字符串连接成新的列表

        #通过CSS选择器提取字段
        # front_image_url=response.meta.get('front_image_url','')      #文章封面图
        # title=response.css(".entry-header h1::text").extract()[0].strip()
        # create_date=response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace('·', ' ').strip()
        # praise_nums=response.css("span.vote-post-up h10::text").extract()[0].strip()
        #
        # fav_nums=response.css("span.bookmark-btn::text").extract()[0]
        # match_re=re.match('.*?(\d+).*',fav_nums)
        # if match_re:
        #     fav_nums=int(match_re.group(1))
        # else:
        #     fav_nums=0
        #
        # comment_nums=response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re=re.match('.*?(\d+).*',comment_nums)
        # if match_re:
        #     comment_nums=int(match_re.group(1))
        # else:
        #     comment_nums=0
        #
        # content = response.css("div.entry").extract()[0]
        # tag_list= response.css('p.entry-meta-hide-on-mobile a::text').extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith('评论')]
        # tags=','.join(tag_list)
        #
        # #填充item的值
        # article_item['url_object_id'] = get_md5(response.url)
        # article_item['title']=title
        # article_item['url']=response.url
        # try:
        #     create_date=datetime.datetime.striptime(create_date,'%Y/%m/%d').date()
        # except Exception as e:
        #     create_date=datetime.datetime.now().date()
        # article_item['create_date'] = create_date
        # article_item['front_image_url'] = [front_image_url]
        # article_item['praise_nums'] = praise_nums
        # article_item['comment_nums'] = comment_nums
        # article_item['fav_nums']=fav_nums
        # article_item['tags']=tags
        # article_item['content'] = content

        #通过item loader加载item
        front_image_url=response.meta.get('front_image_url','')      #文章封面图
        item_loader=ArticleItemLoader(item=JobBoleArticleItem(),response=response)
        item_loader.add_css('title',".entry-header h1::text")          #通过ccs选择器将值选择出来进行填充进title
        item_loader.add_value('url',response.url)                         #response将值传递给url
        item_loader.add_value('url_object_id', get_md5(response.url))
        item_loader.add_css('create_date', "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value('front_image_url', [front_image_url])
        item_loader.add_css('praise_nums', "span.vote-post-up h10::text")
        item_loader.add_css('comment_nums', "a[href='#article-comment'] span::text")
        item_loader.add_css('fav_nums', "span.bookmark-btn::text")
        item_loader.add_css('tags', "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css('content', 'div.entry')
        # 此为itemloader的主要三种方法
        # item_loader.add_css()
        # item_loader.add_xpath()
        # item_loader.add_value()

        article_item=item_loader.load_item()


        yield article_item    #传递到pipelines.py中

