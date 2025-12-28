# -*- coding: utf-8 -*-

import time
import random
import requests
from itertools import product
import csv
import json
import sys
import os
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# 設定標準輸出編碼
sys.stdout.reconfigure(encoding='utf-8-sig')

class Job104Spider():
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = ""
        self.error_log_file = 'error_message.json'

        # 寫入空列表，清空舊紀錄
        with open(self.error_log_file, 'w', encoding='utf-8-sig') as f:
            json.dump([], f)

        self.refresh_session()

    def log_error(self, job_id, message, raw_data=None):
        """將錯誤訊息與原始資料存入 JSON 檔案"""
        error_entry = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'job_id': job_id,
            'error_message': str(message),
            'raw_data': raw_data
        }
        
        # 讀取現有紀錄並更新
        data = []
        if os.path.exists(self.error_log_file):
            try:
                with open(self.error_log_file, 'r', encoding='utf-8-sig') as f:
                    data = json.load(f)
            except:
                data = []
        
        data.append(error_entry)
        with open(self.error_log_file, 'w', encoding='utf-8-sig') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def refresh_session(self):
        print("正在啟動隱身瀏覽器通過驗證...", end='', flush=True)
        with Stealth().use_sync(sync_playwright()) as p:
            browser = p.chromium.launch(headless=True)
            
            # 模擬主流解析度，規避自動化偵測並確保網頁完整載入
            context = browser.new_context(viewport={'width': 1920, 
                                                    'height': 1080})
            page = context.new_page()
            
            try:
                page.goto('https://www.104.com.tw/', 
                          wait_until="domcontentloaded",  # 避免 networkidle 超時
                          timeout=60000  # 最多等待 60 秒
                          )
                # 短暫隨機等待(JavaScript 初始化完成，cookie/session 可用以及模擬真人停留時間)
                time.sleep(random.uniform(0.5, 3))
                self.user_agent = page.evaluate("navigator.userAgent")
                cookies = context.cookies()
                for cookie in cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'], 
                                             domain=cookie['domain'])
                print("已更新憑證")
            except Exception as e:
                self.log_error("SYSTEM", f"驗證失敗: {e}")
            finally:
                browser.close()

    def fetch_with_retry(self, url, headers=None, params=None, max_retries=3):
        attempt = 0
        if headers is None: headers = {}
        headers['User-Agent'] = self.user_agent
        headers['Referer'] = 'https://www.104.com.tw/'

        while attempt < max_retries:
            try:
                r = self.session.get(url, headers=headers, params=params, 
                                     timeout=15)
                if r.status_code == 200: return r, 0
                if r.status_code in (429, 403):
                    self.refresh_session()
                    time.sleep(random.uniform(5, 10))
                    attempt += 1
                    continue
                return None, r.status_code
            except Exception as e:
                attempt += 1
                time.sleep(2)
        return None, -1

    def search(self, max_num=150, filter_params=None): 
        jobs = []
        query_parts = ['jobsource=index_s', 'mode=s']
        if filter_params:
            for k, v in filter_params.items():
                query_parts.append(f'{k}={v}')
        query = '&'.join(query_parts)
        url = 'https://www.104.com.tw/jobs/search/api/jobs'
        headers = {'Accept': 'application/json, text/plain, */*'}
        page = 1
        
        while max_num == -1 or len(jobs) < max_num:
            full_params = f'{query}&page={page}&pagesize=20'
            r, error_code = self.fetch_with_retry(url, headers=headers, 
                                                  params=full_params)
            if r is None: break
            try:
                datas = r.json()
                if 'data' not in datas: break
                jobs.extend(data['link']['job'].split('/job/')[-1] for data in datas['data'])
                if page >= datas['metadata']['pagination']['lastPage']: break
                time.sleep(random.uniform(1, 2))
                page += 1
            except Exception as e:
                self.log_error("SEARCH", e)
                break
        return jobs[:max_num]

    def get_job(self, job_id):
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'
        headers = {'Referer': f'https://www.104.com.tw/job/{job_id}', 
                   'Accept': 'application/json'}
        
        r, error_code = self.fetch_with_retry(url, headers=headers)
        if r is None: return None, error_code
        
        job_data = None

        try:
            resp_json = r.json()
            job_data = resp_json.get('data')
            if not job_data or job_data.get('switch') == 'off': return None, 0

            salary_map = {10: '面議', 
                          20: '論件計酬', 
                          30: '時薪', 
                          40: '日薪', 
                          50: '有薪', 
                          60: '年薪', 
                          70: '其他',
                          }
            header = job_data.get('header', {})
            job_detail = job_data.get('jobDetail', {})
            condition = job_data.get('condition', {})
            welfare = job_data.get('welfare', {})

            workType = ', '.join(job_detail.get('workType', [])) or '全職'
            raw_area = job_detail.get('addressRegion', "")
            jobArea = raw_area if len(raw_area) == 3 else raw_area[3:]
            
            data_info = {
                '更新日期': header.get('appearDate'),
                '工作型態': workType,  
                '工作時段': job_detail.get('workPeriod'),
                '薪資類型': salary_map.get(job_detail.get('salaryType'), '其他'),
                '最低薪資': int(job_detail.get('salaryMin', 0)),
                '最高薪資': int(job_detail.get('salaryMax', 0)),
                '職缺名稱': header.get('jobName'),
                '學歷': condition.get('edu'),
                '工作經驗': condition.get('workExp'),
                '工作縣市': job_detail.get('addressArea'),
                '工作里區': jobArea,
                '工作地址': job_detail.get('addressDetail') or '無',
                '公司名稱': header.get('custName'),
                '職缺描述': job_detail.get('jobDescription') or '無',
                '其他描述': condition.get('other') or '無',
                '擅長要求': ', '.join(item.get('description', '') for item in condition.get('specialty', [])) or '無',
                '證照': ', '.join(item.get('name', '') for item in condition.get('certificate', [])) or '無',
                '駕駛執照': ', '.join(condition.get('driverLicense', [])) or '無',
                '出差': job_detail.get('businessTrip') or '無',
                '104 職缺網址': f'https://www.104.com.tw/job/{job_id}?apply=form',
                '公司產業類別': job_data.get('industry'),
                '法定福利': ', '.join(welfare.get('legalTag', [])) or '無',
            }
            return data_info, 0
        except Exception as e:
            self.log_error(job_id, e, raw_data=job_data)
            return None, -1

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 設定篩選條件
    uni_filter_params = {
        's5': '0',  # 0:不需輪班 256:輪班
        'isnew': '3',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        'wktm': '1',
        'ro': '1',
    }

    mul_filter_params = {
        'area': '6001016001,6001016002,6001016003,6001016004,6001016005,6001016007,6001016008,6001016011,6001016024,6001016027,6001014001,6001014002,6001014003,6001014004,6001014008,6001014014,6001001000',  # (地區) 
        'jobexp': '1,3',  # (經歷) 1: 不拘 / 1年以下, 3: 1-3年, 5: 3-5年, 10: 5-10年, 99: 10年以上
        'edu': '3,4,5',  # (學歷) 1: 高中職以下, 2: 高中職, 3: 專科, 4: 大學, 5: 碩士, 6: 博士
        'jobcat': '2007001004,2007001018,2007001022,2007001020,2007001012,2007001009,2007001010,2016001013',  # (職位類別)
        # 'wt': '1,2,4,8,16',  # (工讀類型) 1: 長期, 2: 短期, 4: 假日, 8: 寒假, 16: 暑假
    }

    # 產生多重篩選條件組合
    keys = list(mul_filter_params.keys())
    values = [v.split(',') for v in mul_filter_params.values()]
    combinations = list(product(*values))
    
    alljobs_set = set()
    # 依組合搜尋職缺 ID
    print(f"開始搜尋職缺 ID (組合數: {len(combinations)})...")
    for idx, combo in enumerate(combinations, 1):
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        jobs = job104_spider.search(max_num=20, filter_params=filter_params)
        alljobs_set.update(jobs)
        print(f"進度：{(idx/len(combinations))*100:6.2f} % | 累計職缺：{len(alljobs_set)}", end='\r')

    # 依職缺 ID 抓取職缺詳細資料並逐筆寫入 CSV
    print(f"\n開始抓取 {len(alljobs_set)} 筆詳情...")
    output_file = f'104jobs_{time.strftime("%Y-%m-%d")}.csv'
    fieldnames = ['更新日期', '工作型態', '工作時段', '薪資類型', '最低薪資', 
                  '最高薪資', '職缺名稱', '學歷', '工作經驗', '工作縣市', 
                  '工作里區', '工作地址', '公司名稱', '職缺描述', '其他描述', 
                  '擅長要求', '證照', '駕駛執照', '出差', '104 職缺網址', 
                  '公司產業類別', '法定福利']

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for idx, job_id in enumerate(alljobs_set, 1):
            info, _ = job104_spider.get_job(job_id)
            if info:
                writer.writerow({k: info.get(k, '無') for k in fieldnames})
                f.flush()
            print(f"進度：{(idx/len(alljobs_set))*100:6.2f} % ({idx}/{len(alljobs_set)})", end='\r')
            time.sleep(random.uniform(0.1, 1))

    # 依是否有錯誤紀錄，調整輸出結果
    with open('error_message.json', 'r', encoding='utf-8-sig') as f:
        errors = json.load(f)
    if errors:
        print(f"\n任務完成！\n資料已寫入 {output_file}\n有錯誤紀錄，請查看 error_message.json")
    else:
        print(f"\n任務完成！\n資料已寫入 {output_file}")