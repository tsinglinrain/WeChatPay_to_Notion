<div align="center">
  <img src="../image/BillNotionSmart.excalidraw.svg" alt="Bill2NotionLogo" style="width:12%; height:auto;" />
</div>

<p align="center"><b>WeChat and Alipay bills are sent to emails, and email attachments are extracted and imported into Notion</b></p>
<p align="center"><b>微信和支付宝账单发送至邮箱，邮件提取附件导入Notion</b></p>

<p align="center">
  <img alt="Static Badge" src="https://img.shields.io/badge/Notion-Integration-black">
  <img alt="Static Badge" src="https://img.shields.io/badge/WeChat%20Pay-Bill-green">
  <img alt="Static Badge" src="https://img.shields.io/badge/Alipay-Bill-blue">
  <img alt="Static Badge" src="https://img.shields.io/badge/Code_style-black-black">
  <img alt="Static Badge" src="https://img.shields.io/badge/Python-green">
</p>

<div align="center">
  <img src="../image/Bill_to_Notion_excalidraw.svg" alt="Bill_to_Notion_excalidraw" style="width:100%; height:auto;" />
</div>

## Additional Notes

> It is recommended to find a related accounting template to achieve better results when using this tool.

> This project does not use the official APIs of WeChat Pay and Alipay. The official APIs are only available to merchants, and ordinary users currently cannot use them.
For more details, click:
[Introduction - Interface Rules | WeChat Pay Merchant Platform Documentation Center](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay-1.shtml)
[Query Bill Interface - Alipay Documentation Center (alipay.com)](https://opendocs.alipay.com/open-v3/b6ddabc9_alipay.ebpp.bill.get)

> This project was inspired by [this article](https://sspai.com/post/66658) from **SSPai**. Thanks to SSPai for providing the idea.

## Quick Start

- Enable the IMAP protocol for your email account. You can search the internet for instructions. Here is an example of how to enable it for a 163.com email account: [Help Center - Common Questions about IMAP (163.com)](https://help.mail.163.com/faqDetail.do?code=d7a5dc8471cd0c0e8b4b8f4f8e49998b374173cfe9171305fa1ce630d7f67ac2a5feb28b66796d3b)

- Export the bills and send them to your email.
<div align="center">
  <img src="../image/wechatpay_bill.png" alt="wechatpay_bill" style="width:100%; height:auto;"/>
  <img src="../image/alipay_bill.png" alt ="aliapy_bill" style="width:100%; height:auto;"/>
</div>

- Copy the sample data_source. It is recommended to `duplicate` this [Bill Import to Notion Template](https://tsinglin.notion.site/68951a1caaba487a884cafcd5086810c?v=3d0c405e7cae405599aed2fe0f5233cc). After getting familiar with it, you can modify it as needed.

- Customize the Notion Integration
  <details>
    <summary>Notion Integration</summary>
    Enter `https://www.notion.so/profile/integrations`
    <img src="../image/Notion_Integration/Notion_Integration_step1.png" alt="Notion_Integration_step1" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step2.png" alt="Notion_Integration_step2" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step3.png" alt="Notion_Integration_step3" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step4.png" alt="Notion_Integration_step4" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step5.png" alt="Notion_Integration_step5" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step6.png" alt="Notion_Integration_step6" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step7.png" alt="Notion_Integration_step7" style="width:80%; height:auto;"/>
    <img src="../image/Notion_Integration/Notion_Integration_step8.png" alt="Notion_Integration_step8" style="width:80%; height:auto;"/>
  </details>

- Download this project

- Run the `config_duplicate.py` file

- Fill in the `config_private.yaml` file as follows:

  ```yaml
  email_config:
    imap_url: "l3*********@163.com"
    password: "HZ************TG"
    username: "imap.163.com"

  notion_config:
    data_source_id: "c1a348********************4c7"  # Database ID
    token: "secret_OHvKVP*******************Lq" # Token
  ```
  <details>
    <summary> Details about data_source_id </summary>
    <img src="../image/alipay_password.jpg" alt="Notion_Integration_step8" style="width:40%; height:auto;"/>
    
    https://www.notion.so/tsinglin/68111a1sssssss487a884cafcd5333310c?v=3d0c405e7cae405599aed2fe0f5233cc

    data_source_id: 68111a1sssssss487a884cafcd5333310c
  </details>