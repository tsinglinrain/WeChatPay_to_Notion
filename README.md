<div align="center">
  <img src="https://socialify.git.ci/tsinglinrain/WeChatPay_to_Notion/image?custom_description=WeChat+and+Alipay+bills+are+sent+to+emails%2C+and+email+attachments+are+extracted+and+imported+into+Notion.%0A%E5%BE%AE%E4%BF%A1%E5%92%8C%E6%94%AF%E4%BB%98%E5%AE%9D%E8%B4%A6%E5%8D%95%E5%8F%91%E9%80%81%E8%87%B3%E9%82%AE%E7%AE%B1%EF%BC%8C%E9%82%AE%E4%BB%B6%E6%8F%90%E5%8F%96%E9%99%84%E4%BB%B6%E5%AF%BC%E5%85%A5Notion&description=1&font=Jost&language=1&logo=https%3A%2F%2Fgithub.com%2Ftsinglinrain%2FWeChatPay_to_Notion%2Fraw%2Fmain%2Fimage%2Flogo%2FBill2notion24.svg&name=1&owner=1&pattern=Brick+Wall&theme=Light" alt="WeChatPay_to_Notion" width="640" height="320" />
</div>

<p align="center">
  <img alt="Static Badge" src="https://img.shields.io/badge/Notion-Integration-black">
  <img alt="Static Badge" src="https://img.shields.io/badge/Bill-WeChat%20Pay-1AAD19">
  <img alt="Static Badge" src="https://img.shields.io/badge/Bill-Alipay-1890FF">
  <a href="https://github.com/ambv/black"><img alt="Static Badge" src="https://img.shields.io/badge/code_style-black-black"></a>
  <img alt="Static Badge" src="https://img.shields.io/badge/Python-3-green">
  <a href="https://github.com/ramnes/notion-sdk-py"><img alt="Static Badge" src="https://img.shields.io/badge/notion--sdk--py-notion--client-blue"></a>
</p>

<p align="center">
  [<a href="docs/README_EN.md">English</a>] | [<a href="docs/README_zh_Hant.md">中文(繁體)</a>]
</p>

<div align="center">
  <img src="./image/banner/preview.gif" alt="Bill2Notion_zh_cn" style="width:100%; height:auto;" />
</div>

<div align="center">
  <img src="./image/banner/Bill2Notion_Workflow_zh_cn.svg" alt="Bill2Notion_Workflow_zh_cn" style="width:100%; height:auto;" />
</div>

<details>
  <summary>导入效果静态图</summary>
    <div align="center">
      <img src="./image/banner/visualization_static.png" alt="visualization_static" style="width:100%; height:auto;" />
</div>
</details>

## 其他说明

> 寻找相关记账的模板，配合使用效果更佳哦。

> 没有使用WeChat Pay以及Alipay的官方API）微信支付和支付宝官方API仅仅对商户开放使用，普通人目前无法使用。<br>
详情点击:<br>
    [简介-接口规则 | 微信支付商户平台文档中心](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay-1.shtml) <br>
    [查询账单接口 - 支付宝文档中心 (alipay.com)](https://opendocs.alipay.com/open-v3/b6ddabc9_alipay.ebpp.bill.get)

> 灵感来源于**少数派**的[这篇文章](https://sspai.com/post/66658)，感谢少数派提供的思路。


## 实现思路

微信或支付宝软件中手动点击获取账单，随后微信或支付宝把账单下载链接发送至邮箱，解压密码发送至微信或支付宝。
然后我在把微信或者支付宝的解压密码，自己邮箱发送给自己邮箱。
随后本项目中代码实现从邮箱中下载压缩包，解压，复制转移，格式化成标准csv文件，数据处理，最后利用Notion API上传。
对于用户而言，配置好`.env`中的各种参数，
最后运行本项目的`main.py`函数，就可实现账单上传。


## 快速开始

- 开通某个邮箱的IMAP协议，请自行互联网搜寻。
- 这里给163邮箱的开通流程作为示例，[帮助中心_常见问题IMAP (163.com)](https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2a5feb28b66796d3b)
- 这里给出QQ邮箱示例，[QQ邮箱开通IMAP步骤](https://i.mail.qq.com/app/app_register_help/imap_163.html)

- 导出账单，发送至邮箱
<div align="center">
  <img src="./image/bill_get/wechatpay_bill.png" alt="wechatpay_bill" style="width:100%; height:auto;"/>
  <img src="./image/bill_get/alipay_bill.png" alt ="aliapy_bill" style="width:100%; height:auto;"/>
</div>

- 拷贝示例数据库，建议`duplicate`此[账单导入Notion模板](https://tsinglin.notion.site/Notion-Dashboard-2aa99f72bada807082e7ee900eae92d6)，熟悉之后可自行修改

- 内部集成认证流程设置
  
  <details>
    <summary>Notion Integration</summary>

    可以参考官方文档[Internal integration auth flow set-up](https://developers.notion.com/docs/authorization)

    键入`https://www.notion.so/profile/integrations`

    <img src="./image/Notion_Integration/Notion_Integration_step1.png" alt="Notion_Integration_step1" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step2.png" alt="Notion_Integration_step2" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step3.png" alt="Notion_Integration_step3" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step4.png" alt="Notion_Integration_step4" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step5.png" alt="Notion_Integration_step5" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step6.png" alt="Notion_Integration_step6" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step7.png" alt="Notion_Integration_step7" style="width:80%; height:auto;"/>
    <img src="./image/Notion_Integration/Notion_Integration_step8.png" alt="Notion_Integration_step8" style="width:80%; height:auto;"/>
  </details>

- 配置环境
  - python版本 >= 3.8(粗略的, 未测试过更低版本)
  - IDE, 如VSCode, PyCharm等
  - Docker(可选, 如果使用Docker部署, **暂时没上线**)

- 下载本项目

  注意本项目没有release， 需要自行下载所有代码。
  
  ```python
  git clone https://github.com/tsinglinrain/WeChatPay_to_Notion.git
  ```

  或者

  下载本项目代码，右上角点击绿色的"code"按钮，选择"Download ZIP"下载压缩包，然后解压。

- 安装所需库

  进入文件夹，注意如果是压缩包一定是解压过的。
  ```python
  pip install -r requirements.txt
  ```

- **环境变量配置**: 使用环境变量配置

  本项目现在支持环境变量配置，更适合Docker部署：
  
  1. 复制环境变量模板文件
  
      windows下复制粘贴`.env.template`，把文件名改成`.env`
      
      或者Linux下
      ```bash
      cp .env.template .env
      ```

  2. 编辑 `.env` 文件，填入您的配置信息
      ```bash
      
      EMAIL_USERNAME=your_email@example.com
      EMAIL_PASSWORD=your_email_password
      EMAIL_IMAP_URL=imap.example.com
      NOTION_DATABASE_ID=your_notion_database_id
      NOTION_TOKEN=your_notion_token
      ```


  3. `data_source_id` 获取

      请注意，Notion在2025年9月3日发布了新版本的Notion API, 新增data source的理念。简单来说, 现在database数据库的概念是能够包含多个数据源data source的容器, data source不能单独存在，必须依赖database这个容器来展现。
      所以我们现在需要对数据源data source进行内容的填充。
      具体获取方式请先参看官方[链接](https://developers.notion.com/docs/working-with-databases#adding-pages-to-a-data-source)。
    
      <details>
      <summary>示意图如下</summary>
      <img src="./image/data_source_get/data_source_get1.png" alt="Notion_Integration_step8" style="width:100%; height:auto;"/>

      <img src="./image/data_source_get/data_source_get2.png" alt="Notion_Integration_step8" style="width:100%; height:auto;"/>

- 账单发送到邮箱后，会有消息告知密码。请复制此密码，**自己邮箱发送密码给自己**，**格式必须如下**：（110110只是示例，图片中的也只是示例，输入自己的**微信支付**那个服务号发过来的和支付宝**服务消息**发过来解压密码）
  ```text
  wechatpay解压密码110110
  alipay解压密码110110
  ```
  <details>
  <summary>格式具体示例</summary>
  <img src="./image/alipay_password.jpg" alt="alipay_password" style="width:40%; height:auto;"/>

  即自己发给自己且标题必须形为`alipay解压密码123456`或者`wechatpay解压密码123456`，原因是代码规定如此，改了必报错。
  ```python
  def get_passwd(self):
    # 检查邮件发件邮箱是否是自己的邮箱
    flag = False
    if self.from_addr == self.username:
        print("Subject,from get_passwd:", self.subject)
        if self.payment_platform == "alipay":
            if re.match("^alipay解压密码[0-9]{6}$", self.subject):
                print("Subject:", self.subject)
                self.paswd = self.subject[-6:]
                print("Password:", self.paswd)
                flag = True
        elif self.payment_platform == "wechatpay":
            if re.match("^wechatpay解压密码[0-9]{6}$", self.subject):
                print("Subject:", self.subject)
                self.paswd = self.subject[-6:]
                print("Password:", self.paswd)
                flag = True
    return flag
  ```
  </details>

## 运行

### 本地Python运行

- 运行`main.py`

  ```bash
  python main.py
  ```

  然后根据提示选择，输入`0`表示导入微信支付账单，输入`1`表示导入支付宝账单。输入2代表全部。暂时不支持异步，后续会支持的。


### Docker运行(暂时没有上线)

- **使用 docker compose（推荐）**

  ```bash
  # 1. 确保已配置 .env 文件
  cp .env.template .env
  # 编辑 .env 文件填入配置信息
  
  # 2. 构建并运行
  docker compose up --build
  ```

- **直接使用 Docker**

  ```bash
  # 构建镜像
  docker build -t wechatpay-to-notion .
  
  # 运行容器
  docker run --rm \
    -e EMAIL_USERNAME="your_email@example.com" \
    -e EMAIL_PASSWORD="your_email_password" \
    -e EMAIL_IMAP_URL="imap.example.com" \
    -e NOTION_DATA_SOURCE_ID="your_notion_data_source_id" \
    -e NOTION_TOKEN="your_notion_token" \
    -v $(pwd)/attachment:/app/attachment \
    -v $(pwd)/bill_csv_raw:/app/bill_csv_raw \
    wechatpay-to-notion
  ```

## 自定义

pass

## 下一步计划

- `Linux`环境下自动化

- 导入成功后邮件返回提醒

- 可以设置每月自动导出提醒

## Star History


[![Star History Chart](https://api.star-history.com/svg?repos=tsinglinrain/WeChatPay_to_Notion&type=Date)](https://star-history.com/#tsinglinrain/WeChatPay_to_Notion&Date)
