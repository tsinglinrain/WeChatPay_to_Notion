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
    username, password, imap_url, database_id, token = main_mail.config_loader()

    # 连接邮箱,获取附件
    client = MailClient(
        username, password, imap_url, payment_platform
    )  # payment_platform="wechatpay"
    client.connect()
    client.fetch_mail()
    main_mail.get_attachment(client)

    # unzip_attachment
    path_att = "./attachment"
    path_target = "./bill_csv_raw"
    msg = main_mail.unzip_attachment(
        path_att, path_target, client.paswd, payment_platform
    )
    print(msg)

    # move_file
    csv_csv_path = "bill_csv_raw"
    target_path = "./"
    main_mail.move_file(csv_csv_path, target_path, payment_platform)

    # 初始化 NotionClient
    notionclient = NotionClient(database_id, token, payment_platform)
    main_notion.process_apply(notionclient, payment_platform)


def main():
    flag = input("Which platform's billing data do you want to import, or all of them? \n(0(wechatpay), 1(alipay), 2(all)): ")
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
