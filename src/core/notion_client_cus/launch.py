# 仅用于测试，实际使用时可能会将此部分代码整合至main.py中

from mail_client.mail_client import MailClient
from src.utils.config_env import get_email_config


def main():
    # 从环境变量加载配置
    flag = False
    try:
        username, password, imap_url = get_email_config()
    except ValueError as e:
        print(f"配置错误: {e}")
        return

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
