# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter         #ctrl点击此函数进行跟踪
from twisted.enterprise import adbapi

import MySQLdb
import MySQLdb.cursors

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    #自定义json文件的导出
    def __init__(self):
        self.file=codecs.open('article.json','w',encoding='utf-8')
    def process_item(self,item,spider):     #传输item
        lines=json.dumps(dict(item),ensure_ascii=False)+'\n'
        #dict()将item转化成dict，ensure_ascii=false可接收其他编码，json将item转化成字符串
        self.file.write(lines)
        return item
    def spider_close(self,spider):
        self.file.close()    #当spider关闭时，调用此函数关闭file


class Mysqlpipeline(object):
    #采用同步机制写入MySQL
    def __init__(self):
        self.conn=MySQLdb.connect('localhost','czy','950329','article',charset='utf8mb4',use_unicode='True')
        self.cursor=self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql="""
            insert into jobbole_article(title,url,create_date,fav_nums)
            VALUES (%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))
        self.conn.commit()        #一定要有conn.commit()这句来提交事务,要不然不能真正的插入数据


class MysqlTwistedPipline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
            host=settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool=adbapi.ConnectionPool('MySQLdb',**dbparms)        #mysqldb为mySQL库的名称,*代表元组的可变参数，**代表字典可变参数
        return cls(dbpool)

    def process_item(self,item,spider):
        #使用twisted将MySQL插入变成异步执行
        # 在线程池dbpool中通过调用runInteraction()函数，来实现异步插入数据的操作。runInteraction()会insert_sql交由线程池中的某一个线程执行具体的插入操作。
        query=self.dbpool.runInteraction(self.do_insert,item)
        # addErrorback()数据库异步写入失败时，会执行addErrorback()内部的函数调用。
        query.addErrback(self.handle_error)

    def handle_error(self,failure):
        print(failure)

#上述MysqlTwistedPipline的函数均为制式步骤，复制粘贴即可，只需改动do_insert函数改变输出


    def do_insert(self,cursor,item):
        #执行具体的插入
        insert_sql="""
            insert into jobbole_article(title,url,create_date,fav_nums)
            VALUES (%s,%s,%s,%s)
        """
        cursor.execute(insert_sql,(item['title'],item['url'],item['create_date'],item['fav_nums']))



class JsonExporterPipeline(object):
    #调用scrapy提供的json export 导出json文件
    def __init__(self):
        self.file=open('articleexport.json','wb')
        #JsonItemExporter()输出 JSON 文件格式, 所有对象将写进一个对象的列表
        self.exporter=JsonItemExporter(self.file,encoding='utf-8',ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()       #停止导出
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item

class ArticleImagePipeline(ImagesPipeline):          #将图片与image_url_path绑定在一起
    def item_completed(self, results, item, info):
        if 'front_image_path' in item:
            for ok,value in results:
                image_file_path=value['path']
                item['front_image_path']=image_file_path

            return item