import time
import random
import requests
from bs4 import BeautifulSoup


class HouseCrawler:
    def __init__(self, max_delay=5):
        self.max_delay = max_delay
        self.base_url = "https://sale.591.com.tw"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Macintosh Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        }

    def search(self, filter_params=None, sort_params=None, want_page=1):
        """search house

        :param filter_params: dict, filter parameters
        :param sort_params: dict, sort parameters
        :param want_page: int, number of pages to scrape
        :return: int, total_count, total number of houses found
        :return: list, house_list, list of houses found
        """
        total_count = 0
        house_list = []
        page = 0

        # record cookies & X-CSRF-TOKEN
        session = requests.Session()
        resp = session.get(self.base_url, headers=self.headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        csrf_token = soup.select_one('meta[name="csrf-token"]')

        headers = self.headers.copy()
        headers["X-CSRF-TOKEN"] = csrf_token.get("content")

        url = self.base_url + "/home/search/list-v2"
        params = "type=2&category=1&shType=list"
        if filter_params:
            params += "".join([f"&{key}={value}" for key, value, in filter_params.items()])

        session.cookies.set(
            "urlJumpIp",
            filter_params.get("region", "1") if filter_params else "1", domain=".591.com.tw",
        )

        if sort_params:
            params += "".join([f"&{key}={value}" for key, value, in sort_params.items()])

        # search house
        while page < want_page:
            params += f"&firstRow={page*30}"
            resp = session.get(url, params=params, headers=headers)
            if resp.status_code != requests.codes.ok:
                print("failed to request", resp.status_code)
                break
            page += 1

            data = resp.json()
            total_count = data["data"]["total"]
            house_list.extend(data["data"]["house_list"])
            # Be polite and wait between requests
            time.sleep(random.uniform(1, self.max_delay))

        return total_count, house_list


if __name__ == "__main__":
    crawler = HouseCrawler()

    filter_params = {
        "regionid": 3,  # 新北市
        "section": 40,  # 三峽區
        "price": "1_1500",  # 1500萬以下
        "shape": 2,  # 1: 公寓, 2: 電梯大樓, 3: 透天厝, 4: 別墅
        "pattern": "2,3",  # 2房, 3房
        "houseage": "0_20",  # 20年內
        "publish_day": 20,  # 20天內
        "area": "15_40",  # 15-40坪
        "unitprice": "0_50",  # 單價50萬以下
        "keywords": "北大",
    }

    # https://sale.591.com.tw/home/search/list-v2?type=2&category=1&shType=list&regionid=3&kind=9&section=40&price=1000_1250&pattern=2&houseage=0_5
    total_count, houses = crawler.search(filter_params=filter_params)
    print(f"Total houses found: {total_count}")
