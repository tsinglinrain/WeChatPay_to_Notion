import requests

# post请求
def post_notion(properties, database_id, token):
    """post请求
    
    Args:
        properties: 需要post的内容
        
    Returns:
        response: 返回response
    """

    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": properties,
        #"children": ["string"],    # 不需要children
        #"icon": "string",
        #"cover": "string"
    }
    headers = {
        "accept": "application/json",
        "Notion-Version": "2022-06-28", # 版本号
        "content-type": "application/json",
        "Authorization": "".join(["Bearer", " ", token]) # 注意空格, 之前没注意空格, 一直报错
    }
    response = requests.post(url, json=payload, headers=headers)
    return response

def response_result(response):

    if response.status_code == 200:
        print("成功...")
    else:
        print("失败...")
        print(response.text)

# def main():
#     get_data_col(new_path2)  

# if __name__ == "__main__":
#     main()
