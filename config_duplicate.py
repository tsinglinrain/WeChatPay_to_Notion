import os
import shutil


# 保护config.yaml文件，防止被上传到git仓库
# 请先运行此文件
def check_and_copy_config():
    if "config_private.yaml" in os.listdir("."):
        print("config_private.yaml has existed, please modify the configuration on it")
        print("config_private.yaml已经存在, 请务必在其上修改配置")
        return
    try:
        shutil.copy("config.yaml", "config_private.yaml")
        print("config.yaml copied to config_private.yaml. Please modify the configuration on it")
        print("config_private.yaml已经复制好, 请务必在其上修改配置")
    except FileNotFoundError:
        print("config.yaml not found. Please check if it exists.")
        print("config.yaml未找到, 请检查是否存在")


if __name__ == "__main__":
    check_and_copy_config()
