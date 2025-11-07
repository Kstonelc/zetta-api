import requests
import json


def web_search(query):
    url = "https://api.bochaai.com/v1/web-search"

    payload = json.dumps(
        {
            "query": query,
            "count": 5,
            "answer": True,
            "freshness": "noLimit",
            "summary": True,
        }
    )

    headers = {
        "Authorization": "Bearer sk-09096d0f58c14c7289f04b6b067e03d0",
        "Content-Type": "application/json",
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response


# search_res = web_search("20w落地的汽车推荐")
# if search_res.status_code == 200:
#     data = search_res.json().get("data")
#     print(data)
