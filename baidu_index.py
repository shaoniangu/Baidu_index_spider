import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import pytesseract
import os
import re

options = webdriver.ChromeOptions()
# 设置中文
options.add_argument('lang=zh_CN.UTF-8')
browser = webdriver.Chrome(chrome_options=options)


from aip import AipOcr
# 请自行申请
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


# 打开浏览器
def openbrowser():
    url = "https://passport.baidu.com/v2/?login&tpl=mn&u=http%3A%2F%2Fwww.baidu.com%2F"
    browser.get(url)
    wait = WebDriverWait(browser, 10)

    # 找到id="TANGRAM__PSP_3__userName"的对话框
    # 清空输入框
    # 点击用户名输入
    # browser.find_element_by_id("TANGRAM__PSP_3__footerULoginBtn").clear()
    # browser.find_element_by_id("TANGRAM__PSP_3__userName").clear()
    # browser.find_element_by_id("TANGRAM__PSP_3__password").clear()

    # 输入账号密码
    # 输入账号密码
    account = []
    try:
        fileaccount = open("./account.txt", encoding='UTF-8')
        accounts = fileaccount.readlines()
        for acc in accounts:
            account.append(acc.strip())
        fileaccount.close()
    except Exception as err:
        print(err)
        input("请正确在account.txt里面写入账号密码")
        exit()
    print(account[0])
    print(account[1])
    footer_login_btn = wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_3__footerULoginBtn")))
    footer_login_btn.click()

    username_input = wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_3__userName")))
    password_input = wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_3__password")))
    login_btn = wait.until(EC.presence_of_element_located((By.ID, "TANGRAM__PSP_3__submit")))
    username_input.send_keys(account[0])
    password_input.send_keys(account[1])
    login_btn.click()

    print("等待网址加载完毕...")

    browser.minimize_window()
    select = input("请观察浏览器网站是否已经登陆(y/n)，若出现验证码请输入验证码后登录：")
    while 1:
        if select == "y" or select == "Y":
            print("登陆成功！")
            print("准备打开新的窗口...")
            break

        elif select == "n" or select == "N":
            selectno = input("账号密码错误请按0，验证码出现请按1...")
            # 账号密码错误则重新输入
            if selectno == "0":

                # 找到id="TANGRAM__PSP_3__userName"的对话框
                # 清空输入框
                username_input.clear()
                password_input.clear()

                # 输入账号密码
                account = []
                try:
                    fileaccount = open("./account.txt", encoding='UTF-8')
                    accounts = fileaccount.readlines()
                    for acc in accounts:
                        account.append(acc.strip())
                    fileaccount.close()
                except Exception as err:
                    print(err)
                    input("请正确在account.txt里面写入账号密码")
                    exit()

                username_input.send_keys(account[0])
                password_input.send_keys(account[1])
                # 点击登陆sign in
                # id="TANGRAM__PSP_3__submit"
                login_btn.click()

            elif selectno == "1":
                # 验证码的id为id="ap_captcha_guess"的对话框
                input("请在浏览器中输入验证码并登陆...")
                select = input("请观察浏览器网站是否已经登陆(y/n)：")

        else:
            print("请输入“y”或者“n”！")
            select = input("请观察浏览器网站是否已经登陆(y/n)：")


def getindex(keywords, day):
    openbrowser()

    # 这里开始进入百度指数
    for keyword in keywords:
        js = 'window.open("http://index.baidu.com");'
        browser.execute_script(js)
        # 新窗口句柄切换，进入百度指数
        # 获得当前打开所有窗口的句柄handles
        # handles为一个数组
        handles = browser.window_handles
        print(handles)
        # 切换到当前最新打开的窗口
        browser.switch_to.window(handles[-1])

        # 在新窗口里面输入网址百度指数
        # browser.get(url="http://index.baidu.com")
        wait = WebDriverWait(browser, 10)
        search_input = wait.until(EC.presence_of_element_located((By.XPATH, """//*[@id="search-input-form"]/input[3]""")))
        search_btn = wait.until(EC.presence_of_element_located((By.XPATH, """//*[@id="home"]/div[2]/div[2]/div/div[1]/div/div[2]/div/span/span""")))
        search_input.clear()
        # 写入需要搜索的百度指数
        search_input.send_keys(keyword)
        # 点击搜索
        search_btn.click()
        time.sleep(2)

        # 最大化窗口
        browser.maximize_window()

        if day == 1:
            sel_xpath = '//div[@class="box-toolbar"]//a[@rel="24h"]'
        elif 1 < day <= 180:
            sel_xpath = '//div[@class="box-toolbar"]//a[@rel="' + str(day) + '"]'
        else:
            sel_xpath = '//div[@class="box-toolbar"]//a[@rel="all"]'

        sel_btn = wait.until(EC.presence_of_element_located((By.XPATH, sel_xpath)))
        sel_btn.click()
        time.sleep(2)

        # 滑动思路：http://blog.sina.com.cn/s/blog_620987bf0102v2r8.html
        # 滑动思路：http://blog.csdn.net/zhouxuan623/article/details/39338511
        xoyelement = browser.find_elements_by_css_selector("#trend rect")[2]

        # 获得坐标长宽
        x = xoyelement.location['x']
        y = xoyelement.location['y']
        width = xoyelement.size['width']
        height = xoyelement.size['height']
        print(x, y, width, height)

        # 常用js:http://www.cnblogs.com/hjhsysu/p/5735339.html
        # 搜索词：selenium JavaScript模拟鼠标悬浮
        num = 1
        x_0 = 1
        y_0 = 50

        # 储存数字的数组
        index = []
        try:
            # webdriver.ActionChains(driver).move_to_element().click().perform()
            # 只有移动位置xoyelement[2]是准确的
            ActionChains(browser).move_to_element_with_offset(xoyelement, 1100, 50).perform()
            time.sleep(1)
            while True:
                # 坐标偏移量
                ActionChains(browser).move_to_element_with_offset(xoyelement, x_0, y_0).perform()
                time.sleep(1)
                # 构造规则
                if day == 1:
                    x_0 = x_0 + 20
                    if x_0 > 1200:
                        break
                elif day == 7:
                    x_0 = x_0 + 40
                    if x_0 > 1200:
                        break
                elif day == 30:
                    x_0 = x_0 + 20
                    if x_0 > 1200:
                        break
                elif day == 90:
                    x_0 = x_0 + 5
                    if x_0 > 1200:
                        break
                elif day == 180:
                    x_0 = x_0 + 3
                    if x_0 > 1200:
                        break
                else:
                    x_0 = x_0 + 1
                    if x_0 > 1200:
                        break

                # <div class="imgtxt" style="margin-left:-117px;"></div>
                imgelement = browser.find_element_by_xpath('//div[@id="viewbox"]')

                # 找到viewbox坐标
                locations = imgelement.location

                # 跨浏览器兼容
                scroll = browser.execute_script("return window.scrollY;")
                top = locations['y'] - scroll

                # 找到viewbox大小
                sizes = imgelement.size

                # 构造指数的位置
                rangle = (
                int(locations['x']), int(top),
                int(locations['x'] + sizes['width']), int(top + sizes['height']))

                # 截取当前浏览器
                if day <= 180:
                    file = './' + keyword + '_' + str(day) + '/image/'
                else:
                    file = './' + keyword + '_' + 'all'  + '/image/'

                if not os.path.exists(file):
                    os.makedirs(file)
                path = file + str(num)
                browser.save_screenshot(str(path) + "_raw.png")

                # 打开截图切割
                img = Image.open(str(path) + "_raw.png")
                jpg = img.crop(rangle)
                jpg.save(str(path) + "_cropped.png")

                # 图像识别
                try:
                    image = get_file_content(str(path) + "_cropped.png")
                    code = client.basicGeneral(image)
                    print('code : ', code)
                    if day <= 180:
                        r1 = re.compile('(\d+).*')
                        r2 = re.compile('\D+(\d+)')
                    else:
                        r1 = re.compile('(\d+\D\d+).*')
                        r2 = re.compile('\D+(\d+)')

                    dict = {}
                    dict['time'] = r1.findall(code['words_result'][0].get('words').strip().replace('-', ''))[0]
                    dict['index'] = int(r2.findall(code['words_result'][1].get('words').strip().replace(',', '').replace('■', ''))[0])
                    print('dict: ', dict)
                    index.append(dict)

                except:
                    index.append("")
                num = num + 1

        except Exception as err:
            print(err)
            print(num)

        print('Total index: ', index)
        # 日期也是可以图像识别下来的
        if day <= 180:
            file = open('./' + keyword + '_' + str(day) + "/total_index.txt", "w")
        else:
            file = open('./' + keyword + '_' + 'all' + "/total_index.txt", "w")

        for item in index:
            file.write(str(item) + "\n")
        file.close()

        index_set = {}
        for item in index:
            print(item)
            if item != '' and item['time'] != '' and item['index'] != '' and item['time'] not in index_set.keys():
                index_set[item['time']] = item['index']
        print('Index_set: ', index_set)
    
        if day <= 180:
            file = open('./' + keyword + '_' + str(day) + "/set_index.txt", "w")
        else:
            file = open('./' + keyword + '_' + 'all' + "/set_index.txt", "w")

        for key in index_set.keys():
            file.write(key + ':' + str(index_set[key]) + "\n")
        file.close()

    return browser


if __name__ == "__main__":
    # 每个字大约占横坐标12.5这样
    # 按照字节可自行更改切割横坐标的大小rangle
    # keyword = input("请输入查询关键字：")
    # sel = int(input("查询1天请按0,查询7天请按1，30天请按2，90天请按3，半年请按4，全部请按5："))
    keywords = ["股票"]
    sel = 1

    # Function avaliable: 1, 2, 3, 4, 5, 0 still has not been finished yet

    if sel == 0:
        day = 1
    elif sel == 1:
        day = 7
    elif sel == 2:
        day = 30
    elif sel == 3:
        day = 90
    elif sel == 4:
        day = 180
    else:
        day = 10000

    browser = getindex(keywords, day)
    for handle in browser.window_handles:
        browser.switch_to.window(handle)
        browser.close()
