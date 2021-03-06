# encoding: utf-8
__author__ = 'MisT'
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request,FormRequest
from scrapy import log
from Newland.items import WeiboItem
from weibo_login import Fetcher
import random
import os
import sys
import redis
import cookielib
#from Newland.schedule import Schedule

'''
    This is a crawler for weibo.cn
    ^w^
'''
__version__='v1.0.7'

class WeiboSpiderBasic(scrapy.Spider):
    conn_r=redis.Redis(host='localhost', port=6379, db='1')
    login_cookies={}
    cklist=[]
    print 'creating a Fetcher'
    fetcher=Fetcher()
    cookiefiles=fetcher.login()
    for filename in cookiefiles:
        ck=self.read_cookie(filename=filename)
        login_cookies[filename]=ck
        cklist.append(filename)
    print 'len:',len(login_cookies)

    def rand_cookie(self):
        r=random.choice(self.cklist)
        return r

    def handle_302(self,response):
        if response.status == 302:
            print '<302>Redirect to:'
            if 'Location' in response.headers:
                print'<',response.headers['Location'],'>'
            print response.meta['ck']
            try:
                del self.login_cookies[response.meta['ck']]
                self.cklist.remove(response.meta['ck'])
            except:
                pass
            if len(self.cklist)==0:
                print 'you have no cookies'
                os.system('pause')
            print 'len:',len(self.login_cookies)
            return 1
        return 0

    def read_cookie(self,filename):
        log.msg("reading cookie... " , level=log.INFO)
        print 'cookie in >',filename,'<:'
        cookie_jar = cookielib.LWPCookieJar(filename)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        cookie = dict()
        for ck in cookie_jar:
            cookie[ck.name] = ck.value
        print cookie
        log.msg("done " , level=log.INFO)
        return cookie

class WeiboSpider(scrapy.Spider):
    # f=open('map.log','a')
    # f.write('thats ok')
    # f.write('i am fine')
    # sch=Schedule('list')
    name="weibo"
    #allowed_domains = ["weibo.cn"]
    #check=['start','ok']
    #print 'here>'
    conn_r = redis.Redis(host='localhost', port=6379, db='1')
    #print'here<'
    login_cookies = {}
    cklist=[]
    def start_requests(self):
        log.msg("start" , level=log.INFO)
        #print >>self.f, 'start.'
        try:
            try:
                print 'creating a Fetcher'
                self.fetcher=Fetcher()
                self.cookiefiles=self.fetcher.login()
                for filename in self.cookiefiles:
                    ck=self.read_cookie(filename=filename)
                    self.login_cookies[filename]=ck
                    self.cklist.append(filename)

                print 'len:',len(self.login_cookies)
            except:
                print 'oh'
            ck=self.rand_cookie()
            yield Request(url='http://weibo.cn/tfyiyangqianxi',cookies=self.login_cookies[ck],dont_filter=True,callback=self.parse_user_new,meta=
                {
                'ck':ck,
                'nick':u'TFBOYS-易烊千玺',
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
            #yield Request(url='http://weibo.cn/pub/topmblog?page=2',callback=self.parse_hot,cookies=self.login_cookie)
            #yield Request(url='http://weibo.cn/1768346942/follow',callback=self.get_user,cookies=self.login_cookie)

            '''
            for i in range(1,25):
                hot_url = "http://weibo.cn/pub/topmblog?page="+str(i)
                yield Request(url=hot_url,callback=self.parse_hot,cookies=self.login_cookie,meta=
                {
                    #'dont_redirect': True,
                    #'handle_httpstatus_list': [302]
                })
            '''
        except Exception, e:
            log.msg("Fail to start" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)

    def parse_hot(self,response):
        log.msg("parse_hot:"+response.url , level=log.INFO)
        try:
            sel=Selector(text=response.body)
            users=sel.xpath('//a[@class="nk"]').extract()
            for user in users:
                sel=Selector(text=user)
                url=sel.xpath('//@href').extract()[0]
                nick=sel.xpath('//text()').extract()[0]
                #print nick,url
                #'''
                if(self.handle_url(url)):
                #'''
                    yield Request(url=url,cookies=self.rand_cookie(),callback=self.parse_user,meta=
                    {
                        'nick':nick

                        #'dont_redirect': True,
                        #'handle_httpstatus_list': [302]
                    })
        except Exception, e:
            log.msg("Fail to parse_hot" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)

    def parse_user(self,response):
        log.msg("parse_user:"+response.url, level=log.INFO)
        #print >>self.f, u'user:['+response.meta['nick']+u'],<',response.url,'>'
        print u'user:['+response.meta['nick']+u'],<',response.url,'>'
        try:
            if self.handle_302(response=response):
                ck=self.rand_cookie()
                yield Request(url=response.url,cookies=self.login_cookies[ck],dont_filter=True,callback=self.parse_user,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
                return
            sel=Selector(text=response.body)
            url=sel.xpath('//div[@class="tip2"]').re('<a href="(.*?)follow">.*?</a>')[0]
            uid=url.split('/')[1]
            #print uid
            #os.system("pause")
            '''
            #####################################################################################
            self.sch.pop_all()
            self.sch.push('http://weibo.cn'+url+'follow')
            self.sch.push('http://weibo.cn'+url+'fans')
            next_url=self.sch.request_url()
            while next_url==-1:
                print 'no more urls'
                next_url=self.sch.request_url()
            ck=self.rand_cookie()
            print type(next_url)
            print next_url
            print'here?'
            yield Request(url=next_url,cookies=self.login_cookies[ck],callback=self.get_user,meta=
                {
                'ck':ck,
                #'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
            ##################################################################################
            '''
            ck=self.rand_cookie()
            yield Request(url='http://weibo.cn'+url+'follow',dont_filter=True,cookies=self.login_cookies[ck],callback=self.get_user,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})

            yield Request(url='http://weibo.cn'+url+'fans',dont_filter=True,cookies=self.login_cookies[ck],callback=self.get_user,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})



            mids=sel.xpath('//div[@class="c"]/@id').re('M_(.*)')
            for i in mids:
                #print i
                # yield Request(url='http://weibo.com/'+uid+'/'+i,cookies=self.login_cookie,callback=self.parse_single,
                #               meta={'nick':response.meta['nick'],'index':i,'uid':uid})
                ck=self.rand_cookie()
                yield Request(url='http://weibo.cn/comment/'+i,dont_filter=True,cookies=self.login_cookies[ck],callback=self.parse_comnt,meta=
                            {
                            'ck':ck,
                            'nick':response.meta['nick'],
                            'mid':i,
                            'uid':uid,
                            'dont_redirect': True,
                            'handle_httpstatus_list': [302]})


            # url=sel.xpath('//div[@class="tip2"]').re('<a href="(.*?)follow">.*?</a>')[0]
            # #print urls
            # #os.system("pause")
            # yield Request(url='http://weibo.cn'+url+'follow',cookies=self.login_cookie,callback=self.get_user)
            # yield Request(url='http://weibo.cn'+url+'fans',cookies=self.login_cookie,callback=self.get_user)
            """
                magic,"yield" may created a stack(LIFO),so parse_comnt first in order to avoid mistake
            """



        except Exception, e:
            log.msg("Fail to parse_user" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)

    def parse_comnt(self,response):
        log.msg("parse_comnt:"+response.url, level=log.INFO)
        #print >>self.f, u'single from:['+response.meta['nick']+u'],<', response.url, '>'
        print u'single from:['+response.meta['nick']+u'],<', response.url, '>'
        try:

            if self.handle_302(response=response):
                ck=self.rand_cookie()
                yield Request(url=response.url,cookies=self.login_cookies[ck],dont_filter=True,callback=self.parse_comnt,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'mid':response.meta['mid'],
                'uid':response.meta['uid'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
                return

            sel=Selector(text=response.body)
            text=''.join(sel.xpath('//div[@id="M_"]//span[@class="ctt"]/text()').extract())
            time=sel.xpath('//div[@id="M_"]//span[@class="ct"]/text()').extract()[0]
            item=WeiboItem(mid=response.meta['mid'],text=text,time=time,user=response.meta['nick'],uid=response.meta['uid'])
            yield item
        except Exception, e:
            log.msg("Fail to parse_comnt" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)

    def get_user(self,response):
        log.msg("get_user:"+response.url, level=log.INFO)
        #print >>self.f, u'get user from:['+response.meta['nick']+u'],<',response.url,'>'
        print u'get user from:['+response.meta['nick']+u'],<',response.url,'>'
        try:
            #print'get user:'
            if self.handle_302(response=response):
                ck=self.rand_cookie()
                yield Request(url=response.url,cookies=self.login_cookies[ck],dont_filter=True,callback=self.get_user,meta=
                {
                'nick':response.meta['nick'],
                'ck':ck,
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
                return

            users=Selector(text=response.body).xpath('//tr/td[@valign="top"][2]').extract()
            #print users
            #os.system("pause")
            for user in users:
                sel=Selector(text=user)
                url=sel.xpath('//a/@href').extract()[0]
                nick=sel.xpath('//a/text()').extract()[0]
                #print url
                #os.system("pause")

                #print 'here?'
                if(self.handle_url(url)):
                    #print nick
                    #log.msg("get:"+nick , level=log.DEBUG)
                    #print >>self.f, u'get:['+nick+u']from<'+response.meta['nick']+u'>.'
                    ck=self.rand_cookie()
                    yield Request(url=url,cookies=self.login_cookies[ck],callback=self.parse_user_new,dont_filter=True,meta=
                    {
                        'ck':ck,
                        'nick':nick,
                        'dont_redirect': True,
                        'handle_httpstatus_list': [302]})
                #print 'here ok'
                #print url,nick
        except Exception, e:
            log.msg("Fail to get_user" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)
    def parse_user_new(self,response):
        log.msg("parse_user_new:"+response.url, level=log.INFO)
        print u'user:['+response.meta['nick']+u'],<',response.url,'>'
        try:
            if self.handle_302(response=response):
                ck=self.rand_cookie()
                yield Request(url=response.url,cookies=self.login_cookies[ck],dont_filter=True,callback=self.parse_user_new,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
                return
            sel=Selector(text=response.body)
            url=sel.xpath('//div[@class="tip2"]').re('<a href="(.*?)follow">.*?</a>')[0]
            uid=url.split('/')[1]
            singles=sel.xpath('//div[@class="c"][position()<last()-1]').extract()
            for i in singles:
                sel=Selector(text=i)
                try:
                    mid=sel.xpath('//@id').re('M_(.*)')[0]
                    text=''.join(sel.xpath('//span[@class="ctt"]/text()').extract())
                    #print text.encode('gbk','ignore')
                    #os.system("pause")
                    time=sel.xpath('//span[@class="ct"]/text()').extract()[0]
                    item=WeiboItem(mid=mid, text=text, time=time, user=response.meta['nick'], uid=uid)
                    yield item
                except:
                    print 'error:'
                    print i.encode('gbk','ignore')
            ck=self.rand_cookie()
            yield Request(url='http://weibo.cn'+url+'follow',dont_filter=True,cookies=self.login_cookies[ck],callback=self.get_user,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})

            yield Request(url='http://weibo.cn'+url+'fans',dont_filter=True,cookies=self.login_cookies[ck],callback=self.get_user,meta=
                {
                'ck':ck,
                'nick':response.meta['nick'],
                'dont_redirect': True,
                'handle_httpstatus_list': [302]})
        except Exception, e:
            log.msg("Fail to parse_user_new" , level=log.ERROR)
            log.msg(str(e), level=log.ERROR)





    def handle_url(self,url):
        # if url in self.check:
        #     print url,'is in check'
        #     return 0
        #
        # self.check.append(url)
        # print url,'has been insert to check'
        # print 'elements:',len(self.check)
        # return 1

        if self.conn_r.get(url):
            print url,'is in list[',self.conn_r.dbsize(),']'
            return 0

        self.conn_r.set(url,1)
        print url,'has been insert to list[',self.conn_r.dbsize(),']'
        return 1

    def rand_cookie(self):
        #print'rand_cookie...'
        r=random.choice(self.cklist)
        #print r
        # os.system("pause")
        return r

    def handle_302(self,response):
        if response.status == 302:
            print '<302>Redirect to:'
            if 'Location' in response.headers:
                print'<',response.headers['Location'],'>'
            print response.meta['ck']
            try:
                del self.login_cookies[response.meta['ck']]
                self.cklist.remove(response.meta['ck'])
            except:
                pass
            if len(self.cklist)==0:
                print 'you have no cookies'
                os.system('pause')
            print 'len:',len(self.login_cookies)
            #os.system('pause')
            #self.login_cookies.remove(response.cookies)
            return 1
        return 0



    def read_cookie(self,filename):
        log.msg("reading cookie... " , level=log.INFO)
        print 'cookie in >',filename,'<:'
        cookie_jar = cookielib.LWPCookieJar(filename)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        cookie = dict()
        for ck in cookie_jar:
            cookie[ck.name] = ck.value
        print cookie
        log.msg("done " , level=log.INFO)
        return cookie
    # def clean_html(html):
    #     html = html.replace('\\t', '')
    #     html = html.replace('\\r', '')
    #     html = html.replace('\\n', '')
    #     html = html.replace('\\', '')
    #     return html

w = WeiboSpiderBasic()





