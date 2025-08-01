from src.utils import config_env

from src.core.notion_client_cus.notion_client_cus import NotionClient
from src.core.file_handler.data_processor import DataProcessor
from src.core.file_handler.csv_transformer import CsvTransformer


def config_loader():
    """
    从环境变量加载配置
    返回: (username, password, imap_url, database_id, token)
    """
    return config_env.config_loader()


def csv_transformer(payment_platform):
    csvp = CsvTransformer(payment_platform)
    csvp.transform_to_standard_csv()

    path_std = csvp.path_std

    return path_std


def data_processor(payment_platform, path_std):
    processor = DataProcessor(path_std, payment_platform)
    processor.process_mandatory_fields()
    if payment_platform == "alipay":
        processor.filter_rows("收/支", ["收入", "不计收支"])
        processor.drop_columns(["对方账号", "交易状态", "收/支"])
        # processor.drop_columns(["交易订单号", "商家订单号"])
    elif payment_platform == "wechatpay":
        processor.filter_rows("收/支", ["收入"])
        processor.drop_columns(["当前状态", "收/支"])
        # processor_wechat.drop_columns(["交易单号", "商户单号"])
    else:
        raise ValueError("Invalid payment platform")
    df_processed = processor.get_processed_data()

    return df_processed


def process_apply(notionclient: NotionClient, payment_platform):
    path_std = csv_transformer(payment_platform)
    # path_std = "alipay_standard.csv"
    df_processed = data_processor(payment_platform, path_std)
    # print(df_processed.head(7))
    df_processed.apply(notionclient.process_row, axis=1)


def main():
    # 加载配置文件
    username, password, imap_url, database_id, token = config_loader()

    payment_platform = "alipay"
    # payment_platform = "wechatpay"
    if payment_platform not in ["alipay", "wechatpay"]:  # 防呆
        raise ValueError(
            "Invalid payment platform, payment platform must be 'alipay' or 'wechatpay'"
        )

    # 初始化 NotionClient
    notionclient = NotionClient(database_id, token, payment_platform)
    process_apply(notionclient, payment_platform)


if __name__ == "__main__":
    main()
