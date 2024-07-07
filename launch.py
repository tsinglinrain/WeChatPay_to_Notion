# 仅用于测试，实际使用时可能会将此部分代码整合至main.py中

from mail_client import MailClient
import yaml


def main():
    # 加载 .yaml 文件
    flag = False
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)

    # 获取配置变量
    email_config = config.get("email_config", {})
    username, password, imap_url = (
        i for i in email_config.values()
    )  # 写成这样更简洁,但需要注意顺序

    client = MailClient(username, password, imap_url)
    client.connect()
    client.fetch_mail()
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.from_addr == client.username and client.subject == "原神启动!":
            print("launch successfully")
            print("时机已到, 今日起兵!")
            flag = True
            break
    if not flag:
        print("Can't get signal, maybe you forget to send the signal email.")
        print("Only when you send a signal, you will launch the game.")


if __name__ == "__main__":
    main()
