from mail_client import MailClient
from unzip_att import FileExtractor
from move_file import FileMover
import yaml


def launch_signal(client):
    '''检测是否有发射信号'''
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.from_addr == client.username and client.subject == "原神启动!":
            print("launch successfully")
            print("时机已到,今日起兵!")
            break

def config_loader():
    # 加载 .yaml 文件
    with open('config_private.yaml', 'r', encoding="utf-8") as file:
        config = yaml.safe_load(file)

    # 获取配置变量
    email_config = config.get('email_config', {})

    username, password, imap_url = (i for i in email_config.values())

    notion_config = config.get('notion_config', {})
    database_id, token = (i for i in notion_config.values())

    return username, password, imap_url, database_id, token

def get_attachment(client):
    '''获取附件'''
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.get_passwd():
            print("Get password successfully")
            break
    if not client.paswd:
        raise Exception("Can't get password, maybe you forget to send the password email.")
    else:
        print("-"*20)
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
    username, password, imap_url, database_id, token = config_loader()

    # 连接邮箱,获取附件
    # payment_platform="wechatpay"
    payment_platform="alipay"
    client = MailClient(username, password, imap_url, payment_platform) # payment_platform="wechatpay"
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

if __name__ == '__main__':
    main()
