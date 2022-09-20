# 初步测试完毕，尝试使用peppeteer访问页面（记得conrol+ML，在launch的default选项中把'enable automation'注释掉）

# save模块的path命名有错误，注意加入/让保存位置正确(已解决)
# 注意保存的标题,需要加入年份防止不同年的同名文件覆盖(已解决,数据还未爬取到21年,效果有待考察)

# 页面的数量可通过主页获取
import os.path
import time
import pyppeteer
import asyncio
from pyppeteer import launch
from pyquery import PyQuery as pq
from bs4 import BeautifulSoup
import re


class Covid_Demo1(object):
    def __init__(self):
        self.home_url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'

    # ————————————追加功能模块————————————
    # extra_01利用该函数返回疫情数据页的总页数(首先确认数据保存可靠再进行此模块的设计)
    # content改为传入式,降低系统耦合度
    def update_num_of_pages(self, content):
        soup = BeautifulSoup(content, 'lxml')
        target1 = soup.find('div', attrs={'class': "pagination_index_last"})
        text = target1.text
        pageNum = int(re.findall('共 (\d*) 页', text)[0])
        return pageNum

    # 01 将 pyppeteer 的操作封装成 get_content_from_url 函数，用于发起网络请求，获取网页源码
    # (1)利用异步函数调用pyppeteer中的功能
    async def P_get_content_from_url(self, url):
        brower = await launch({'headless': False, 'dumpio': True, 'autoClose': True})
        page = await brower.newPage()

        await page.goto(url)
        await asyncio.wait([page.waitForNavigation()])
        # time.sleep(2) #必要时可利用time.sleep()让网页有充足的时间打开
        str = await page.content()
        await brower.close()
        return str

    # (2)利用函数运行接收异步函数的返回值
    def get_content_from_url(self, url):
        return asyncio.get_event_loop().run_until_complete(self.P_get_content_from_url(url))

    # 02 获取每一页的url，实现翻页功能
    # (注意，使用'yield'回增加耦合度，后续改进:将获取的页面保存再表中返回，遍历表翻页)
    def get_pageURL(self, pageNum):
        url = ""
        for page in range(1, pageNum+1):
            if page == 1:
                url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml'
            else:
                url = 'http://www.nhc.gov.cn/xcs/yqtb/list_gzbd_' + str(page) + '.shtml'
            yield url

    # 03 从页面中提取每日疫情信息链接
    # 注意python函数可以有多个返回值，可以结合for循环反复不断执行，遍历多个返回值
    # 因为传入的信息是类似list的文件，需要返回多次，故用yield代替return进行返回，在程序处理完数据后再继续返回
    # 需要学习BS的检索机制
    def get_url_from_perPage(self, content):
        soup = BeautifulSoup(content, 'lxml')
        titleList = soup.find('div', attrs={"class": "list"}).ul.find_all(
            "li")  # 目标列表在一个属性内,故用find,属性内有多个目标,故在内部引用find_all
        for item in titleList:
            link = "http://www.nhc.gov.cn" + item.a["href"]
            title = item.a["title"]
            date = item.span.text
            yield title, link, date

    # 04 获取每日信息正文
    def get_content_perday(self, html):
        soup = BeautifulSoup(html, 'lxml')
        # 以下部分的BS定位参数尚不明确
        # 进一步获取标签中的标签时，利用二次引用函数.find_all()
        content = soup.find('div', attrs={"id": "xw_box"}).find_all("p")
        s = ""
        if content:
            for item in content:
                s += item.text
            return s
        return "爬取失败！"

    # 05 通过save_file函数，将爬取的数据保存到本地txt文档中
    # 题目要求利用编程工具或开发包写入excel表中
    def save_file(self, path, filename, content):
        # (1) 判断路径是否存在，若不存在则创建路径
        if not os.path.exists(path):
            os.makedirs(path)
        # (2) 保存文件
        with open(path + filename + ".txt", 'w', encoding='utf-8') as f:
            f.write(content)

    # 以下run方法实现对模块的总体调度:
    # run1 实现demo样例的基本功能，将数据保存至txt文档中
    def run1(self):
        # 利用函数获取每页的url，实现”翻页“
        # 在此导入新模块，实时获取pageNum
        con = self.get_content_from_url(self.home_url)
        pageNum = self.update_num_of_pages(con)
        print("pageNum = %d"%(pageNum))
        for url in self.get_pageURL(pageNum):
            # 依次返回页面的每日信息url
            s = self.get_content_from_url(url)
            for title, link, date in self.get_url_from_perPage(s):
                # 注意把title修改,在前置加上年份,对print也需要稍微修改
                # print(title, link)  # 暂时当进度条用吧（泪）
                # 全国的疫情通报由2020-1-21开始，注意将此前的日期排除
                # 可以投入使用，需要在参考样例的基础上修改判断条件
                # 该模块使用到split函数，作用时利用特殊字符分割字符串，返回的时字符列表
                date_list = date.split("-")
                year = int(date_list[0])
                month = int(date_list[1])
                day = int(date_list[2])
                # (title修改
                title = date_list[0] + "年" + title
                print(title, link)
                # title修改)
                if year <= 2020 and month <= 1 and day < 21:
                    break
                # 在最早日期前，正常执行
                html = self.get_content_from_url(link)
                content = self.get_content_perday(html)
                self.save_file("E:\Applications\PyCharm\PythonDemo\Project-K Demo1\Covid_Datas\\", title, content)


    # ————————————测试模块————————————
    # 01 以下特殊的Test方法专供模块测试使用:
    def url_content_Test(self, url):
        content = self.get_content_from_url(url)
        print(content)

    # 02 以下方法用于测试页数更新模块
    def pageNum_Test(self):
        content = self.get_content_from_url(self.home_url)
        num = self.update_num_of_pages(content)
        print(num)


    # 待追加功能:(1)从home_page追溯总页数，并且返回总页数值
    #          (2)通过循环迭代实现url翻页
    #          (3)保存爬取到的信息，待下一步处理


if __name__ == '__main__':
    # 第一次测试:将信息保存为txt格式(测试完毕)
    # run1以加入新模块
    test01 = Covid_Demo1()
    test01.run1()

    # 第二次测试:自动更新页面数量（测试完毕）
    # test02 = Covid_Demo1()
    # test02.pageNum_Test()


# 需求记录
# 01 需要重新设计一个能精准保存到文件夹中的save模块，方便后续单独的数据处理
# 02 尝试将数据保存为Excel格式，或是其它格式，先学习可视化的相关知识，令保存的数据与可视化接轨
# 测试记录:
# 01 9.16 20:46,保存文件失败，初步分析为run方法中的变量没有转换完毕（已解决）
