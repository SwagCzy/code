import hashlib

def get_md5(url):                #数据加密储存
    if isinstance(url,str):      #str表示string，即代表unicode
        url=url.encode('utf_8')
    m=hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__=='__main__':
    print(get_md5('http://jobbole.com'.encode('utf-8')))