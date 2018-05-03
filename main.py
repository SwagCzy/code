from scrapy.cmdline import execute
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#os.path.abspath为当前main.py目录，os.path.dirname为包含当前文件的文件夹目录
execute(['scrapy','crawl','jobbole'])