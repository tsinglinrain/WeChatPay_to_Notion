from mail_core.mail_client import MailClient
from mail_core.unzip_att import FileExtractor
from mail_core.move_file import FileMover
import config_env


def launch_signal(client):
    """检测是否有发射信号"""
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.from_addr == client.username and client.subject == "原神启动!":
            print("launch successfully")
            print("时机已到,今日起兵!")
            break


def config_loader():
    """
    从环境变量加载配置
    返回: (username, password, imap_url, data_source_id, token)
    """
    return config_env.config_loader()


def get_attachment(client: MailClient):
    """获取附件"""
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.get_passwd():
            print("Get password successfully")
            break
    if not client.paswd:
        raise Exception(
            "Can't get password, maybe you forget to send the password email."
        )
    else:
        print("-" * 20)
        for num in reversed(client.email_list):
            client.get_mail_info(num)
            if client.fetch_mail_attachment():
                print("Download attachment successfully")
                break


def unzip_attachment(path_att, path_target, password, payment_platform):
    extractor = FileExtractor(path_att, path_target, password, payment_platform)
    files = extractor.search_files()
    msg = extractor.unzip_earliest_file(files)
    return msg


def move_file(csv_csv_path, target_path, payment_platform):
    mover = FileMover(csv_csv_path, target_path, payment_platform)
    mover.copy_file()


def main():
    # 加载配置文件
    username, password, imap_url, data_source_id, token = config_loader()

    # 连接邮箱,获取附件
    # payment_platform="wechatpay"
    payment_platform = "alipay"
    client = MailClient(
        username, password, imap_url, payment_platform
    )  # payment_platform="wechatpay"
    client.connect()
    client.fetch_mail()
    get_attachment(client)

    # unzip_attachment
    path_att = "./attachment"
    path_target = "./bill_csv_raw"
    msg = unzip_attachment(path_att, path_target, client.paswd, payment_platform)
    print(msg)

    # move_file
    csv_csv_path = "bill_csv_raw"
    target_path = "./"
    move_file(csv_csv_path, target_path, payment_platform)


if __name__ == "__main__":
    main()
