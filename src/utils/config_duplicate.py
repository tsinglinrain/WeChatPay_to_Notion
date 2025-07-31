import os
import shutil


# 保护.env文件，防止被上传到git仓库
# 请先运行此文件
def check_and_copy_config():
    if ".env" in os.listdir("."):
        print(".env file already exists, please modify the configuration in it")
        print(".env文件已经存在, 请务必在其上修改配置")
        return
    try:
        shutil.copy(".env.template", ".env")
        print(".env.template copied to .env. Please modify the configuration in it")
        print(".env文件已经复制好, 请务必在其上修改配置")
    except FileNotFoundError:
        print(".env.template not found. Please check if it exists.")
        print(".env.template未找到, 请检查是否存在")


if __name__ == "__main__":
    check_and_copy_config()
