import os
import imaplib
import email
from email.header import decode_header
from email.utils import parseaddr
from email.message import Message

# from bs4 import BeautifulSoup
from lxml import html
import re
import requests
from urllib.parse import quote
from urllib.parse import unquote
import yaml


class MailClient:
    def __init__(self, username, password, imap_url, payment_platform=None):
        self.username = username
        self.password = password
        self.imap_url = imap_url
        self.mail = None
        self.email_list = None
        self.email_message = None
        self.from_addr = None
        self.paswd = None
        self.subject = None
        self.payment_platform = payment_platform

    def connect(self):
        # 连接到服务器
        self.mail = imaplib.IMAP4_SSL(self.imap_url)

        # 163需要添加
        if self.imap_url == "imap.163.com":
            imaplib.Commands["ID"] = "NONAUTH"
            self.mail._simple_command(
                "ID", '("name" "test" "version" "0.0.1")'
            )  # 163邮箱需要设置

        # 验证
        self.mail.login(self.username, self.password)

        result_sel, data_sel = self.mail.select("inbox")
        print(f"login status: {result_sel}, {data_sel}")

    def fetch_mail(self):
        # 搜索邮件
        result_search, data_search = self.mail.uid("search", None, "ALL")
        self.email_list = data_search[0].split()

    def get_mail_info(self, num):
        """获取邮件信息,包括发件人,主题"""
        result, data = self.mail.uid("fetch", num, "(BODY.PEEK[])")
        raw_email = data[0][1].decode("utf-8")
        self.email_message: Message = email.message_from_string(raw_email)

        # 获取邮件发件人
        from_header_parts = decode_header(self.email_message["From"])
        from_header = "".join(
            (
                part.decode(encoding if encoding else "utf-8")
                if isinstance(part, bytes)
                else part
            )
            for part, encoding in from_header_parts
        )
        from_name, self.from_addr = parseaddr(from_header)  # 解析邮件地址以及名称

        # 获取邮件主题
        subject_parts = decode_header(self.email_message["Subject"])
        self.subject = "".join(
            (
                part.decode(encoding if encoding else "utf-8")
                if isinstance(part, bytes)
                else part
            )
            for part, encoding in subject_parts
        )

    def get_passwd(self):
        # 检查邮件发件邮箱是否是自己的邮箱
        flag = False
        print("From:", self.from_addr)
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

    @staticmethod
    def walk_message(part: Message, count=0):
        if not os.path.exists("attachment"):
            os.makedirs("attachment")

        print(f"Content Type {count}:, {part.get_content_type()}")
        filename = part.get_filename()
        print(f"Filename_ori:{filename}")
        if filename:
            filename = "".join(
                (
                    part.decode(encoding if encoding else "utf-8")
                    if isinstance(part, bytes)
                    else part
                )
                for part, encoding in decode_header(filename)
            )
            print("Filename_decoded:", filename)

            # 下载附件
            payload = part.get_payload(decode=True)
            with open(os.path.join("attachment", filename), "wb") as f:
                f.write(payload)

        # 如果payload是HTML类型,尝试从中提取网址,微信就是
        if part.get_content_type() == "text/html":
            # soup = BeautifulSoup(part.get_payload(decode=True), 'html.parser')
            # link_elements = soup.find_all('a')
            tree = html.fromstring(
                part.get_payload(decode=True), parser=html.HTMLParser(encoding="utf-8")
            )
            # print(html.tostring(tree, pretty_print=True).decode('utf-8'))  # 打印HTML树
            print(f"tree:{tree}")
            # link_elements = tree.xpath('/html/body/tr[4]/td/div/a')   # 我下载了其html,按照层级写的,不知道为什么是空值
            link_elements = tree.xpath('//a[contains(@href, "http")]')

            print(f"link_elements:{link_elements}")
            for link in link_elements:
                url = link.get("href")
                if url and re.match(
                    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                    url,
                ):
                    print(f"url:{url}")  # 打印找到的网址

                    # 下载网址指向的文件
                    response = requests.get(url)
                    print(f"status_code:{response.status_code}")
                    print(f"response.headers:{response.headers}")

                    # 检查状态码
                    if response.status_code != 200:
                        raise Exception(
                            f"Request failed with status {response.status_code}"
                        )

                    # 检查错误消息
                    error_message = "请在微信中重新申请导出"  # 当前文件已过期，请在微信中重新申请导出 or 当前文件下载次数已超出限制，如有需要请在微信中重新申请导出
                    if error_message in response.text:
                        raise Exception(
                            f"Request failed: 不要慌, {error_message}, 并且要重新发送密码邮件"
                        )

                    if "Content-Disposition" in response.headers:
                        filename = re.findall(
                            "filename=([^;]*)", response.headers["Content-Disposition"]
                        )[0]
                        print(f"filename_html_ori:{filename}")
                        filename = unquote(filename)  # 解码文件名
                        print(f"filename_html_decoded:{filename}")
                    else:
                        filename = url.split("/")[-1][:10]  # 实际上用不到,暂时保留

                    with open(
                        os.path.join(
                            "attachment", re.sub(r'[\\/*?:"<>|]', "", filename)
                        ),
                        "wb",
                    ) as f:
                        f.write(response.content)

        if part.is_multipart():
            for subpart in part.get_payload():
                count += 1
                MailClient.walk_message(subpart, count)

    def fetch_mail_attachment(self):
        flag = False
        # 创建一个字典,由于表示支付平台来源
        payment_platform_dict = {
            "alipay": "service@mail.alipay.com",
            "wechatpay": "wechatpay@tencent.com",
        }

        if self.from_addr == payment_platform_dict[self.payment_platform]:

            print("Subject, From fetch_mail_attachment:", self.subject)
            self.walk_message(self.email_message)
            flag = True
            return flag


# 使用
def main():
    # 加载 .yaml 文件,文件在上一级目录
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "config_private.yaml"
    )
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    # 获取配置变量
    email_config = config.get("email_config", {})
    username, password, imap_url = (
        i for i in email_config.values()
    )  # 写成这样更简洁,但需要注意顺序
    # username = email_config.get('username')
    # password = email_config.get('password')
    # imap_url = email_config.get('imap_url')

    # client = MailClient(username, password, imap_url, payment_platform="alipay") # payment_platform="wechatpay"
    client = MailClient(
        username, password, imap_url, payment_platform="wechatpay"
    )  # payment_platform="wechatpay"

    client.connect()
    client.fetch_mail()
    for num in reversed(client.email_list):
        client.get_mail_info(num)
        if client.get_passwd():
            print("Get password successfully")
            break
    if not client.paswd:
        print("Can't get password, maybe you forget to send the password email.")
        print("Only when you send a password, you will download the attachment.")
    else:
        print("-" * 20)
        for num in reversed(client.email_list):
            client.get_mail_info(num)
            if client.fetch_mail_attachment():
                print("Download attachment successfully")
                break


if __name__ == "__main__":
    main()
