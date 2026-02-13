
import requests
import pandas as pd
from loguru import logger
import os

# Create data directory if it doesn't exist
if not os.path.exists("starbucks_stores/data"):
    os.makedirs("starbucks_stores/data")

logger.add("starbucks_stores/data/scraping_{time}.log", rotation="500 MB")

def get_starbucks_stores():
    all_stores = []
    for sido_cd in range(1, 18):
        p_sido_cd = f"{sido_cd:02d}"
        url = "https://www.starbucks.co.kr/store/getStore.do?r=X2D6LNU8AB"
        payload = {
            "in_biz_cds": "0",
            "in_scodes": "0",
            "ins_lat": "37.56682",
            "ins_lng": "126.97865",
            "search_text": "",
            "p_sido_cd": p_sido_cd,
            "p_gugun_cd": "",
            "isError": "true",
            "in_distance": "0",
            "in_biz_cd": "",
            "iend": "1000",
            "searchType": "C",
            "set_date": "",
            "rndCod": "9QQ7ILZT2H",
            "all_store": "0",
            "T03": "0",
            "T01": "0",
            "T27": "0",
            "T12": "0",
            "T09": "0",
            "T30": "0",
            "T05": "0",
            "T22": "0",
            "T21": "0",
            "T36": "0",
            "T43": "0",
            "Z9999": "0",
            "T64": "0",
            "T66": "0",
            "P02": "0",
            "P10": "0",
            "P50": "0",
            "P20": "0",
            "P60": "0",
            "P30": "0",
            "P70": "0",
            "P40": "0",
            "P80": "0",
            "whcroad_yn": "0",
            "P90": "0",
            "P01": "0",
            "new_bool": "0",
        }
        headers = {
            "host": "www.starbucks.co.kr",
            "origin": "https://www.starbucks.co.kr",
            "referer": "https://www.starbucks.co.kr/store/store_map.do",
            "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
        }
        
        logger.info(f"Scraping stores for sido_cd: {p_sido_cd}")
        response = requests.post(url, data=payload, headers=headers)
        
        if response.status_code == 200:
            stores = response.json()["list"]
            logger.info(f"Found {len(stores)} stores for sido_cd: {p_sido_cd}")
            all_stores.extend(stores)
        else:
            logger.error(f"Failed to scrape stores for sido_cd: {p_sido_cd}. Status code: {response.status_code}")
            
    return all_stores

if __name__ == "__main__":
    all_starbucks_stores = get_starbucks_stores()
    df = pd.DataFrame(all_starbucks_stores)
    
    output_path = "starbucks_stores/data/starbucks_ai.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"Scraping complete. Data saved to {output_path}")

