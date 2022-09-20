#

# 01 先打开单个文件,解决完数据提取问题后再考虑遍历文件的问题
# 02 数据处理与数据获取可封装为两个进程

# 03 基于None判断的保护代码没用，findall会返回'',非空
# 需要解决的问题是正则表达式在无法找到特定数据时的自适配方案，本代码未做自适配处理
# 当前只能处理2022.5.1之后的数据，且当正则表达式无法匹配文本时程序会报错

# 2022.9.20本代码作为删去屎山的测试样例，暂时宣告失败

import re
import xlwt
import datetime
import os.path

# provinces = ["河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川",
#              "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "北京", "天津", "上海", "重庆", "香港", "澳门"]

import re
import xlwt
import datetime
import os.path

# provinces = ["河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川",
#              "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "北京", "天津", "上海", "重庆", "香港", "澳门"]

class Covid_ExcelMaker(object):
    # 00 制表常量界定
    def __init__(self):
        # 为制表方便，将对中国大陆的总计也作为一栏于各省放一起
        self.provinces =["中国大陆","河北", "山西", "辽宁", "吉林", "黑龙江", "江苏", "浙江", "安徽", "福建", "江西", "山东", "河南", "湖北", "湖南", "广东", "海南", "四川",
                        "贵州", "云南", "陕西", "甘肃", "青海", "台湾", "内蒙古", "广西", "西藏", "宁夏", "新疆", "北京", "天津", "上海", "重庆", "香港", "澳门"]

#——————————辅助功能模块——————————
    # 01 此模块实现根据Pname在t_list中定位，返回坐标
    def get_location(self,Pname,t_list):
        dest = -1
        for to_be_w in t_list:
            if to_be_w["地区"] == Pname:
                dest = t_list.index(to_be_w)
                break
        return dest
#——————————主要功能模块——————————
    # 01 根据文件名读取txt文件，返回str数据
    # 模块测试完毕，输入参数为txt文件名
    # 需要加入os模块辅助判断文件是否存在
    def read_txt(self,filename):
        filename = filename + ".txt"
        path = "E:\Applications\PyCharm\PythonDemo\Project-K Demo1\Covid_Datas\\"
        with open(path+filename,"r",encoding="utf-8") as file:
            str_of_txt = file.read()
        return str_of_txt

    # 02 构建list作为excel的输出模板,从str0中提取信息导入到list中,返回list（初步测试完毕）
    def get_excelMsg(self,str_to_be_deal):
        # (1)首先构造出list的框架
        target_list = []
        for province in self.provinces:
            target_data = {}
            target_data["地区"] = province
            target_data["新增确诊"] = None
            target_data["新增无症状"] = None
            target_list.append(target_data)
        # (2)利用正则表达式开始提取信息,更新list
        # 1.首先处理确诊病例（使用正则表达式注意贪婪与非贪婪匹配的区别）
        # 贪婪匹配（.*）最大长度匹配
        # 非贪婪匹配（.*?）最小长度匹配
            # 01获取本土新增病例
        #——————增加if判断作为findall为空时的保护——————
        mainland_new = re.findall("新增确诊病例.*?本土病例(\d*)例",str_to_be_deal)
        if len(mainland_new)==0:
            print("get nothing from findall")
        else:
            mainland_new = mainland_new[0]
            mainland_new = int(mainland_new)
            # print("本土新增：%d"%(mainland_new)) #测试完毕，本土新增已获取
            # 如何写入:利用遍历找到匹配的地区名，以index返回坐标，写入
            dest = self.get_location("中国大陆",target_list)
            target_list[dest]["新增确诊"] = mainland_new
        # ——————保护结束——————

            # 02 获取本土无症状
        # ——————增加if判断作为findall为空时的保护——————
        mainland_none = re.findall("。31个省.*?新增无症状感染者\d*例.*?本土(\d*)例",str_to_be_deal)
        if len(mainland_none)==0:
            print("get nothing from findall")
        else:
            mainland_none = mainland_none[0]
            mainland_none = int(mainland_none)
            dest = self.get_location("中国大陆",target_list)
            target_list[dest]["新增无症状"] = mainland_none
        # ——————保护结束——————


            # 03 获取各省新增病例（考虑split）
        # ——————增加if判断作为findall为空时的保护——————
        str_new = re.findall("新增确诊病例.*?本土病例\d*例（(.*?)）",str_to_be_deal)
        if len(str_new)==0:
            print("get nothing from findall")
        else:
            str_new = str_new[0]
            list_new = str(str_new).split("，")
            # print(list_new) #通过测试，split因为特殊原因无法直接触发,str强制转换
            # length =  len(list_new)
            # 遍历list_new，并且写入数据
            for mini_str in list_new:
                #——————加入保护——————
                name = re.findall("(\D*)\d*例",mini_str)
                if len(name)>0:
                    name = name[0]
                else:
                    name = None
                num = re.findall("(\d*)例",mini_str)
                if len(num)>0:
                    num = num[0]
                else:
                    num = None
                    continue
                #——————保护结束——————
                # print("name:%s,num:%s"%(name,num))
                dest = self.get_location(name,target_list)
                target_list[dest]["新增确诊"] = int(num)
        # ——————保护结束——————

            # 04 获取各省新增无症状
        # ——————增加if判断作为findall为空时的保护——————
        str_new1 = re.findall("。31个省.*?新增无症状感染者\d*例.*?本土\d*?例（(.*?)）",str_to_be_deal)
        if len(str_new1)==0:
            print("get nothing from findall")
        else:
            str_new1 = str_new1[0]
            list_new1 = str(str_new1).split("，")
            # print(str_new1)
            for mini_str in list_new1:
                name = re.findall("(\D*)\d*例",mini_str)[0]
                num = re.findall("(\d*)例",mini_str)[0]
                # print("name:%s,num:%s"%(name,num))
                dest = self.get_location(name,target_list)
                target_list[dest]["新增无症状"] = int(num)
        # ——————保护结束——————
        return target_list

    # 03 此函数根据传入的指定格式list创造excel表格，并且按照来源文件命名，保存到指定文件夹
    def excel_maker(self,t_list,filename):
        cov_excel = xlwt.Workbook()
        sheet = cov_excel.add_sheet("cov_sheet")
        # 创建表头
        title_list = ["地区","新增确诊","新增无症状"]
        for i in title_list:
            sheet.write(0,title_list.index(i),i)
        # 填入t_list信息
        i = 1
        for msg in t_list:
            sheet.write(i,0,msg["地区"])
            sheet.write(i,1,msg["新增确诊"])
            sheet.write(i,2,msg["新增无症状"])
            i = i + 1
        path = "Excels\\" + filename + ".xlsx"
        cov_excel.save(path)


#——————————总体调度模块——————————
    # 01 该模块目前作测试用
    def run1(self):
        filename = "2022年截至9月17日24时新型冠状病毒肺炎疫情最新情况"
        str0 = self.read_txt(filename)
        # 接下来利用正则表达式从str0中提取信息
        list0 = self.get_excelMsg(str0)
        print(list0)
        self.excel_maker(list0,filename)
    # 02 该模块实现核心功能:遍历所有记事本并且生成excel
    def run2(self):
        # *大框架为遍历各月份（利用datetime模块实现）
        # 该进程尽量与进程1适应，实现参数的自适应更新
        date_point = datetime.date(2022,5,1)
        while date_point <= datetime.date(2022,9,17):
            date_str = str(date_point)
            date_list = date_str.split("-")
            year = date_list[0]
            month = date_list[1]
            day = date_list[2]
            # 在月份和日为个位数时不补0，使用强制类型转换除去
            month = int(month)
            month = str(month)
            day = int(day)
            day = str(day)
            filename = year + "年截至" + month + "月" + day + "日24时新型冠状病毒肺炎疫情最新情况"
            # ————在调用程序之前，先使用os.path检测文件是否存在，加入自适应保护机制，尽可能匹配————
            path = "E:\Applications\PyCharm\PythonDemo\Project-K Demo1\Covid_Datas\\" + filename + ".txt"
            if os.path.exists(path):
                # 开始程序调用
                self.run3(filename)
                # 程序调用结束
            else:
                print("文件:\'%s\'不存在"%(filename))
            # ————保护机制结束————
            date_point = date_point + datetime.timedelta(days = 1)
    # 03 该模块目前作为run1的可输入参数版本
    def run3(self,filename):
        str0 = self.read_txt(filename)
        # 接下来利用正则表达式从str0中提取信息
        list0 = self.get_excelMsg(str0)
        # print(list0)
        self.excel_maker(list0,filename)

if __name__=="__main__":
    CM = Covid_ExcelMaker()
    # str0 = CM.read_txt("2022年截至9月17日24时新型冠状病毒肺炎疫情最新情况")
    # # 接下来利用正则表达式从str0中提取信息
    # list0 = CM.get_excelMsg(str0)
    # print(list0)
    # CM.run1()
    CM.run2()
    # 注意文件名可能有变化，加入检测适应机制
# 报错记录:
# IndexError: list index out of range，findall返回的内容可能为空，记得加入检测保护机制