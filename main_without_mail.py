import main_mail as main_mail
import main_notion as main_notion
from notion_core.notion_client_cus import NotionClient
from mail_core.mail_client import MailClient
import config_duplicate


def bill_to_notion(payment_platform):
    if payment_platform not in ["alipay", "wechatpay"]:  # 防呆
        raise ValueError(
            "Invalid payment platform, payment platform must be 'alipay' or 'wechatpay'"
        )

    config_duplicate.check_and_copy_config()

    # 加载配置文件
    username, password, imap_url, data_source_id, token = main_mail.config_loader()

    # 因为下载后的附件名称不确定，所以舍去解压及复制文件的步骤，直接将附件下载到当前目录下
    # 如果不需要邮箱功能，请将账单重命名为`wechatpay_raw.csv`或`alipay_raw.csv`放在当前目录下

    # 初始化 NotionClient
    notionclient = NotionClient(data_source_id, token, payment_platform)
    main_notion.process_apply(notionclient, payment_platform)


def main():
    flag = input(
        "Which platform's billing data do you want to import, or all of them? \n(0(wechatpay), 1(alipay), 2(all)): "
    )
    flag = int(flag)
    try:
        if flag == 0:
            payment_platform = ("wechatpay",)
        elif flag == 1:
            payment_platform = ("alipay",)
        elif flag == 2:
            payment_platform = ("alipay", "wechatpay")
        else:
            raise ValueError("Invalid input, please enter 0, 1 or 2.")
    except:
        raise ValueError("Invalid input, please enter 0, 1 or 2.")

    for payment_platform in payment_platform:
        print(f"Processing {payment_platform}...")
        bill_to_notion(payment_platform)
        print(f"{payment_platform} processed successfully!")
        print("========================================")


if __name__ == "__main__":
    main()
