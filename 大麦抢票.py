import os  # 创建文件夹, 文件是否存在
import time  # time 计时
import pickle  # 保存和读取cookie实现免登陆的一个工具
from time import sleep
from selenium import webdriver  # 操作浏览器的工具
from selenium.webdriver.common.by import By
 
"""
一. 实现免登陆
二. 抢票并且下单
"""
# 大麦网主页
damai_url = 'https://www.damai.cn/'
# 登录
login_url = 'https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F'
# 抢票目标页
target_url = 'https://detail.damai.cn/item.htm?spm=a2oeg.home.card_0.ditem_2.591b23e1AyXdAl&id=729700971838'
 
 
# class Concert:
class Concert:
    # 初始化加载
    def __init__(self):
        self.status = 0  # 状态, 表示当前操作执行到了哪个步骤
        self.login_method = 1  # {0:模拟登录, 1:cookie登录}自行选择登录的方式
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe')  # 当前浏览器驱动对象
 
    # cookies: 登录网站时出现的 记录用户信息用的
    def set_cookies(self):
        """cookies: 登录网站时出现的 记录用户信息用的"""
        self.driver.get(damai_url)
        print('###请点击登录###')
        # 我没有点击登录,就会一直延时在首页, 不会进行跳转
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        # 点击扫码成功，跳过首页title的校验
        print('###请扫码登录###')
        # 没有登录成功
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(1)
        # 登录成功，跳过扫码页面title的校验
        print('###扫码成功###')

        # get_cookies: driver里面的方法
        pickle.dump(self.driver.get_cookies(), open('cookies.pkl', 'wb'))
        print('###cookie保存成功###')
        self.driver.get(target_url)
 
    # 假如说我现在本地有 cookies.pkl 那么 直接获取
    def get_cookie(self):
        """假如说我现在本地有 cookies.pkl 那么 直接获取"""
        cookies = pickle.load(open('cookies.pkl', 'rb'))
        for cookie in cookies:
            cookie_dict = {
                'domain': '.damai.cn',  # 必须要有的, 否则就是假登录
                'name': cookie.get('name'),
                'value': cookie.get('value')
            }
            self.driver.add_cookie(cookie_dict)
        print('###载入cookie###')
 
    def login(self):
        """登录"""
        if self.login_method == 0:
            self.driver.get(login_url)
            print('###开始登录###')
        elif self.login_method == 1:
            # 创建文件夹, 文件是否存在
            if not os.path.exists('cookies.pkl'):
                self.set_cookies()  # 没有文件的情况下, 登录一下
            else:
                self.driver.get(target_url)  # 跳转到抢票页
                self.get_cookie()  # 并且登录
 
    def enter_concert(self):
        """打开浏览器"""
        print('###打开浏览器,进入大麦网###')
        # 调用登录
        self.login()  # 先登录再说
        self.driver.refresh()  # 刷新页面
        self.status = 2  # 登录成功标识
        print('###登录成功###')
        # 处理弹窗
        if self.isElementExist('/html/body/div[2]/div[2]/div/div/div[3]/div[2]'):
            self.driver.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/div/div[3]/div[2]').click()
 
    # 二. 抢票并且下单
    def choose_ticket(self):
        """选票操作"""
        if self.status == 2:
            print('=' * 30)
            print('###开始进行日期及票价选择###')
            while self.driver.title.find("确认订单") == -1:
                try:
                    buybutton = self.driver.find_element(By.CLASS_NAME, 'buybtn').text
                    if buybutton == '提交缺货登记':
                        self.status = 2  # 没有进行更改操作
                        self.driver.get(target_url)  # 刷新页面 继续执行操作
                    elif buybutton == '立即预定':
                        # 点击立即预定
                        self.driver.find_element('buybtn').click()
                        self.status = 3
                    elif buybutton == '立即购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 4
                    elif buybutton == '选座购买':
                        self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                        self.status = 5
                except:
                    print('###没有跳转到订单结算界面###')
                title = self.driver.title
                if title == '选座购买':
                    # 选座购买的逻辑
                    self.choice_seats()
                elif title == '确认订单':
                    # 实现下单的逻辑
                    while True:
                        # 如果标题为确认订单
                        print('正在加载.......')
                        # 如果当前购票人信息存在 就点击
                        if self.isElementExist('//*[@id="container"]/div/div[9]/button'):
                            # 下单操作
                            self.check_order()
                            break
 
    def choice_seats(self):
        """选择座位"""
        while self.driver.title == '选座购买':
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[1]/div[2]/img'):
                print('请快速选择你想要的座位!!!')
            while self.isElementExist('//*[@id="app"]/div[2]/div[2]/div[2]/div'):
                self.driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div[2]/div[2]/button').click()
 
    def check_order(self):
        """下单操作"""
        if self.status in [3, 4, 5]:
            print('###开始确认订单###')
            time.sleep(1)
            try:
                # 默认选第一个购票人信息
                self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[2]/div[2]/div[1]/div/label').click()
            except Exception as e:
                print('###购票人信息选中失败, 自行查看元素位置###')
                print(e)
            # 最后一步提交订单
            time.sleep(0.5)  # 太快了不好, 影响加载 导致按钮点击无效
            self.driver.find_element(By.XPATH, '//*[@id="container"]/div/div[9]/button').click()
            time.sleep(20)
 
    def isElementExist(self, element):
        """判断元素是否存在"""
        flag = True
        browser = self.driver
        try:
            browser.find_element(By.XPATH, element)
            return flag
        except:
            flag = False
            return flag
 
    def finish(self):
        """抢票完成, 退出"""
        self.driver.quit()
 
 
if __name__ == '__main__':
    con = Concert()
    try:
        con.enter_concert()  # 打开浏览器
        con.choose_ticket()  # 选择座位
    except Exception as e:
        print(e)
        con.finish()

"""
以下是对代码执行顺序及各个函数功能的详细解析：

---

### **一、代码执行顺序**
```python
if __name__ == '__main__':
    con = Concert()          # 1. 实例化 Concert 类
    try:
        con.enter_concert() # 2. 打开浏览器并登录
        con.choose_ticket() # 3. 进入抢票和下单流程
    except Exception as e:
        print(e)
        con.finish()        # 4. 异常时退出浏览器
```

**具体流程：**
1. **初始化 (`__init__`)**:
   - 创建 `Concert` 对象，初始化浏览器驱动 (`webdriver.Chrome`)。
   - 设置初始状态 `status=0` 和登录方式 `login_method=1`（默认使用 cookie 登录）。

2. **进入大麦网 (`enter_concert`)**:
   - 调用 `login()` 方法处理登录逻辑。
   - 若使用 cookie 登录 (`login_method=1`)，检查本地是否存在 `cookies.pkl`：
     - 存在：加载 cookie 并跳转到目标页。
     - 不存在：调用 `set_cookies()` 完成扫码登录并保存 cookie。
   - 刷新页面 (`refresh()`) 并处理可能的弹窗。

3. **选票和下单 (`choose_ticket`)**:
   - 根据页面按钮状态（立即预定/立即购买/选座购买）执行不同操作。
   - 若进入选座页面 (`title=选座购买`)，调用 `choice_seats()`。
   - 若进入订单确认页 (`title=确认订单`)，调用 `check_order()` 完成下单。

4. **退出浏览器 (`finish`)**:
   - 无论成功与否，最终通过 `driver.quit()` 关闭浏览器。

---

### **二、核心函数功能说明**

#### **1. 初始化方法**
```python
def __init__(self):
    self.status = 0          # 记录当前操作步骤（0-5）
    self.login_method = 1    # 登录方式（0: 模拟登录，1: cookie登录）
    self.driver = webdriver.Chrome(executable_path='chromedriver.exe')  # 浏览器驱动
```

#### **2. 登录相关函数**
- **`set_cookies()`**:
  - **功能**: 通过扫码登录获取并保存 cookie 到 `cookies.pkl`。
  - **流程**:
    1. 打开大麦首页，等待用户手动点击登录。
    2. 等待扫码成功，跳转回首页后保存 cookie。

- **`get_cookie()`**:
  - **功能**: 从本地 `cookies.pkl` 加载 cookie 到浏览器，实现免登录。

- **`login()`**:
  - **功能**: 根据 `login_method` 选择登录方式：
    - `login_method=0`: 跳转到登录页手动登录。
    - `login_method=1`: 使用本地 cookie 或调用 `set_cookies()` 登录。

#### **3. 浏览器操作**
- **`enter_concert()`**:
  - **功能**: 打开浏览器并进入大麦网，处理登录和弹窗。
  - **关键操作**:
    - 调用 `login()` 完成登录。
    - 刷新页面并关闭弹窗（如存在）。

#### **4. 抢票逻辑**
- **`choose_ticket()`**:
  - **功能**: 根据页面按钮状态执行抢票操作。
  - **关键逻辑**:
    - 检测按钮文本（立即预定/立即购买/选座购买）。
    - 根据按钮状态跳转到订单确认页或选座页。

- **`choice_seats()`**:
  - **功能**: 在选座页面等待用户手动选座，点击确认按钮。

- **`check_order()`**:
  - **功能**: 在订单确认页选择购票人信息并提交订单。
  - **操作**:
    1. 勾选第一个购票人。
    2. 点击提交订单按钮。

#### **5. 工具函数**
- **`isElementExist(element)`**:
  - **功能**: 检查指定 XPath 元素是否存在，用于判断页面状态。
  - **返回**: `True` 或 `False`。

- **`finish()`**:
  - **功能**: 关闭浏览器，释放资源。

---

### **三、关键技术与注意事项**

#### **1. 登录方式**
- **Cookie 免登录**: 通过 `pickle` 序列化存储 cookie，避免重复扫码。
- **模拟登录**: 需手动操作（代码中未完全实现）。

#### **2. 页面状态判断**
- 通过 `self.driver.title` 检测当前页面（如确认订单页、选座页）。
- 使用 `isElementExist()` 检查关键元素（如按钮、弹窗）。

#### **3. 潜在问题**
- **XPath 硬编码**: 如 `//*[@id="container"]/div/div[9]/button` 可能因页面结构变化失效。
- **缺乏显式等待**: 依赖 `time.sleep()` 可能导致稳定性问题（建议改用 `WebDriverWait`）。
- **异常处理不足**: 部分 `try-except` 块未细化异常类型。

#### **4. 改进建议**
1. **引入显式等待**:
   ```python
   from selenium.webdriver.support.ui import WebDriverWait
   from selenium.webdriver.support import expected_conditions as EC
   # 示例：等待按钮出现
   WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'buybtn')))
   ```
2. **动态 XPath**: 使用更稳定的定位方式（如 CSS 选择器）。
3. **多线程/自动化重试**: 增加抢票失败后的自动重试机制。

---

### **四、总结**
此代码通过 Selenium 实现了大麦网的自动化抢票，核心流程为 **登录 → 跳转目标页 → 检测票务状态 → 下单**。适合学习自动化测试和基础爬虫逻辑，但需进一步完善异常处理和页面交互细节才能投入实际使用。
"""