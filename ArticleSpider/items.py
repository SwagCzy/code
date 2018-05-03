# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import datetime
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join     #Mapcompose可以连续调用多个函数


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def add_jobbole(value):
    return value+'jobbole'


def date_convert(value):
    try:
        create_date = datetime.datetime.striptime(value, '%Y/%m/%d').date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return create_date


def get_nums(value):
    match_re = re.match('.*?(\d+).*', value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    #去掉tag中提取的评论
    if '评论' in value:
        return ''
    else:
        return value


def return_value(value):
    return value



class ArticleItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()



class JobBoleArticleItem(scrapy.Item):
    # MapCompose（）函数，该函数将python函数或者lambda表达式作为参数（参数个数无限制），然后按顺序执行这些函数来产生最终的结果。譬如MapCompose(unicode.strip, float), 首先将xpath提取的信息去掉空格，再将其转换为float格式
    title=scrapy.Field(input_processor=MapCompose(add_jobbole))
    create_date=scrapy.Field(input_processor=MapCompose(date_convert))
    url=scrapy.Field()
    url_object_id=scrapy.Field()
    front_image_url=scrapy.Field(output_processor = MapCompose(return_value))
    front_image_path=scrapy.Field()   #封面图保存在本地的路径
    praise_nums=scrapy.Field(input_processor=MapCompose(get_nums))
    comment_nums=scrapy.Field(input_processor=MapCompose(get_nums))
    fav_nums=scrapy.Field(input_processor=MapCompose(get_nums))
    tags = scrapy.Field(input_processor=MapCompose(remove_comment_tags),output_processor =Join(','))
    content=scrapy.Field()
