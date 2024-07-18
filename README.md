<div align="center">
<img src="./image/BillNotionSmart.excalidraw.svg" alt="Bill2NotionLogo" style="width:12%; height:auto;" />
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

<p align="center">
  [<a href="docs/README_EN.md">English</a>] | [<a href="docs/README_zh_TW.md">中文(繁體)</a>] | [<a href="docs/README_JP.md">日本語</a>]
</p>

<div align="center">
<img src="./image/Bill_to_Notion_excalidraw.svg" alt="Bill2NotionLogo" style="width:100%; height:auto;" />
</div>
## 其他说明

> 寻找相关记账的模板，配合使用效果更佳哦。

> 没有使用WeChat Pay以及Alipay的官方API）微信支付和支付宝官方API仅仅对商户开放使用，普通人目前无法使用。<br>
详情点击:<br>
    [简介-接口规则 | 微信支付商户平台文档中心](https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay-1.shtml) <br>
    [查询账单接口 - 支付宝文档中心 (alipay.com)](https://opendocs.alipay.com/open-v3/b6ddabc9_alipay.ebpp.bill.get)

> 灵感来源于**少数派**的[这篇文章](https://sspai.com/post/66658)，感谢少数派提供的思路。

## 快速开始

- 下载本项目

- 填写`config_private.yaml`文件

```yaml
email_config:
  imap_url: "l3*********@163.com"
  password: "HZ************TG"
  username: "imap.163.com"

notion_config:
  database_id: "c1a348********************4c7"  # 数据库ID
  token: "secret_OHvKVP*******************Lq" # token
```

- 运行`main.py`

## 自定义

pass

## 下一步计划

- `Linux`环境下自动化

- 导入成功后邮件返回提醒

- 可以设置每月自动导出提醒


