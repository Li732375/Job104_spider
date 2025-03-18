# -*- coding: utf-8 -*-

import time
import random
import requests
from itertools import product
import pandas as pd
import json

# 設定標準輸出編碼為 utf-8
import sys
sys.stdout.reconfigure(encoding='utf-8')


class Job104Spider():
    def search(self, max_num=150, filter_params=None): 
        """搜尋職缺"""
        
        # max_num: 指定最大職缺數 (-1 表示翻到最大數量)
        # 每頁提供 22 筆職缺資料，最多可找 150 * 22 = 3300 筆職缺
        
        jobs = []
        total_count = 0
        
        url = 'https://www.104.com.tw/jobs/search/api/jobs'
        query = f'jobsource=index_s&mode=s'
        
        if filter_params:
            query += ''.join([f'&{key}={value}' for key, value in filter_params.items()])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/?',
        }
        
        page = 1
        pagesize = 20
        while max_num == -1 or len(jobs) < max_num:
            params = f'{query}&page={page}&pagesize={pagesize}'
            r = requests.get(url, params=params, headers=headers)
            
            if r.status_code != requests.codes.ok:
                print(f'{url}?{params}')  # 顯示當前請求的 URL
                print(f'職缺清單請求失敗 {r.status_code}')
                print(f'當前 encoding: {r.encoding}')
                print(r.text)
                break
            
            datas = r.json()
            # 最後資料覆寫入指定檔案，協助除錯
            with open('job_search_list.json', 'w', encoding='utf-8') as f:
                f.write('{' + f'encoding: {r.encoding}' + '}\n')
                json.dump(datas, f, ensure_ascii=False, indent=4)  # 使用 indent=4 排版

            total_count = datas['metadata']['pagination']['total']
            
            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(
                data['link']['job'].split('/job/')[-1] for data in datas['data'])
            
            # 如果是最後一頁或空頁，就跳出迴圈
            if page == datas['metadata']['pagination']['lastPage'] or \
                datas['metadata']['pagination']['lastPage'] == 0:
                break
            
            print(f'篩選條件清單資料({len(jobs)})，緩衝中...')
            time.sleep(random.uniform(3, 5))

            page += 1
        
        return total_count, jobs[:max_num]

    def get_job(self, job_id):
        """取得職缺網址詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': f'https://www.104.com.tw/job/{job_id}',
        }

        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print('get_job 請求失敗', r.status_code)
            print(f'當前 encoding: {r.encoding}')
            print(r.text)
            return

        job_data = r.json()['data']
        # 最後資料覆寫入指定檔案，協助除錯
        with open('job_url.json', 'w', encoding='utf-8') as f:
            f.write('{' + f'"encoding": "{r.encoding}"' + ', ' + f'"URL": "https://www.104.com.tw/job/{job_id}"' + '}\n')
            json.dump(job_data, f, ensure_ascii=False, indent=4)  # 使用 indent=4 美化 JSON

        salary_type = {
            10: '面議',
            20: '論件計酬',
            30: '時薪',
            50: '有薪',
            60: '年薪',
        }

        # 職缺 (全職、兼職、長短期假日工讀..)
        workType = '全職' if len(job_data['jobDetail']['workType']) == 0 else ', '.join([item for item in job_data['jobDetail']['workType']])
        
        data_info = {
            '更新日期': job_data['header']['appearDate'],
            '學歷': job_data['condition']['edu'],
            '工作經驗': job_data['condition']['workExp'],
            '工作型態': workType,  
            '薪資類型': salary_type[job_data['jobDetail']['salaryType']],
            '最高薪資': int(job_data['jobDetail']['salaryMax']),
            '最低薪資': int(job_data['jobDetail']['salaryMin']),
            '工作縣市': job_data['jobDetail']['addressArea'],
            '工作地址': job_data['jobDetail']['addressDetail'],
            '工作時段': job_data['jobDetail']['workPeriod'],
            '公司名稱': job_data['header']['custName'],
            '公司產業類別': job_data['industry'],
            '職缺名稱': job_data['header']['jobName'],
            '描述': job_data['jobDetail']['jobDescription'],
            '104 職缺網址': f'https://www.104.com.tw/job/{job_id}',
            '法定福利': ', '.join(job_data['welfare']['legalTag']),
            #'其他福利': job_data['welfare']['welfare'],
        }
        
        # 隨機等待 3~5 秒
        time.sleep(random.uniform(1, 3))

        return data_info

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 獨立參數(單選)
    uni_filter_params = {
        's5': '0',  # 0:不需輪班 256:輪班
        'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        'wktm': '1',
    }
    
    # 可複合參數(多選)
    mul_filter_params = {
        'area': '6001016001,6001016002,6001016003,6001016004,6001016005,\
            6001016007,6001016008,6001016011,6001016024,6001016027,6001018001,\
                6001014001,6001014002,6001014003,6001014004,6001014008,\
                    6001014014,6001001000',  # (地區) 
        's9': '1',  # (上班時段) 日班 1, 夜班 2, 大夜班 4, 假日班 8
        'jobexp': '0,1,3',  # (經歷要求) 不拘 0, 1年以下 1, 1-3年 3, 3-5年 5, 5-10年 10, 10年以上 99
        'edu': '1,2,3,4,5',  # (學歷要求) 高中職以下 1,高中職 2,專科 3,大學 4,碩士 5,博士 6
        'jobcat': '2007001004,2007001018,2007001022,2007001020,2007001012,\
            2002001011,2007001009,2007001010,2016001013',
        #'wt': '1,2,4,8,16',  # 長期 1, 短期 2, 假日 4, 寒假 8, 暑假 16
    }

    # 解析可複合篩選條件的所有可能組合
    keys = mul_filter_params.keys()
    values = [v.split(',') for v in mul_filter_params.values()]
    combinations = list(product(*values))  # 產生所有可能組合
    print('搜尋條件組合總數：', len(combinations))
    
    # 每個條件組合取得的職缺數
    max_num = 100
    # 使用篩選條件，轉換成 set 合併重複職缺
    alljobs_set = set()
    for idx, combo in enumerate(combinations, start=1):  # 避免從 0 開始影響百分比計算
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        _, jobs = job104_spider.search(max_num=max_num, 
                                       filter_params=filter_params)
        
        # 計算當前進度百分比
        progress = (idx / len(combinations)) * 100
        print(f"處理進度：{progress:.2f}% ({idx}/{len(combinations)})", end='\r')

        time.sleep(random.uniform(0.4, 2))
        
        alljobs_set.update(jobs)  # 用 set.update() 合併職缺 ID，去除重複

    print('職缺總數：', len(alljobs_set))
    """
    # 不使用篩選條件
    total_count, jobs = job104_spider.search(100)
    alljobs_set = set(jobs)
    """ 

    """ 
    # 進度符號
    progress_symbols = ['|', '/', '-', '\\']  # 定義進度符號的順序
    progress_index = 0  # 進度符號的初始索引
    """

    # 逐一取得職缺詳細資料
    job_details = []
    for job_id in alljobs_set:
        job_info = job104_spider.get_job(job_id)
        job_details.append(job_info)

        """
        # 更新進度符號顯示（動態顯示 | / - \）
        sys.stdout.write(f'\r職缺資料({len(job_details)})，緩衝中... {progress_symbols[progress_index]}') 
        sys.stdout.flush()  # 強制刷新輸出到螢幕
        # 更新進度符號索引
        progress_index = (progress_index + 1) % len(progress_symbols)
        """
    
    """
    print()  # 讓進度列結束後換行
    """

    # 將職缺資料存入 Excel
    df = pd.DataFrame(job_details)
    df.to_excel('104jobs.xlsx', index=False)

    print("職缺資料已寫入 104jobs.xlsx")
