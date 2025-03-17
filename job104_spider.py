import time
import random
import requests
from itertools import product
import pandas as pd

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
            'Referer': 'https://www.104.com.tw/jobs/search/',
        }
        
        page = 1
        pagesize = 20
        while max_num == -1 or len(jobs) < max_num:
            params = f'{query}&page={page}&pagesize={pagesize}'
            r = requests.get(url, params=params, headers=headers)
            
            if r.status_code != requests.codes.ok:
                print(f'職缺清單請求失敗 {r.status_code}')
                print(r.text)
                break
            
            datas = r.json()
            total_count = datas['metadata']['pagination']['total']
            
            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(data['link']['job'].split('/job/')[-1] for data in datas['data'])
            
            # 如果是最後一頁或空頁，就跳出迴圈
            if page == datas['metadata']['pagination']['lastPage'] or datas['metadata']['pagination']['lastPage'] == 0:
                break
            
            page += 1
            time.sleep(random.uniform(3, 5))
            print('清單資料緩衝計時中，請稍後...')
        
        return total_count, jobs

    def get_job(self, job_id):
        """取得職缺網址詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://www.104.com.tw/job/{job_id}',
        }

        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print('get_job 請求失敗', r.status_code)
            print(r.text)
            return

        job_data = r.json()['data']

        salary_type = {
            10: '面議',
            50: '有薪',
            30: '每小時工讀',
        }

        workType = job_data['jobDetail']['workType']  # 職缺 (全職、兼職、長短期假日工讀..)
        data_info = {
            '更新日期': job_data['header']['appearDate'],
            '學歷': job_data['condition']['edu'],
            '工作經驗': job_data['condition']['workExp'],
            '薪資類型 (面議 / 有薪資)': salary_type[job_data['jobDetail']['salaryType']],
            '最高薪資': int(job_data['jobDetail']['salaryMax']),
            '最低薪資': int(job_data['jobDetail']['salaryMin']),
            '工作型態': '全職' if len(workType) == 0 else ''.join([item for item in workType]),  
            '職缺名稱': job_data['header']['jobName'],
            '描述': job_data['jobDetail']['jobDescription'],
            '公司名稱': job_data['header']['custName'],
            '工作縣市': job_data['jobDetail']['addressArea'],
            '工作里區': job_data['jobDetail']['addressRegion'][3:],
            '工作時段': job_data['jobDetail']['workPeriod'],
            '職缺 104 網址': url,
            'job_104_company_url': job_data['header']['custUrl'],
            '法定福利': ''.join(job_data['welfare']['legalTag']),
            '其他福利': job_data['welfare']['welfare'],
        }
        
        # 隨機等待 3~5 秒
        time.sleep(random.uniform(3, 5))
        print('職缺資料緩衝計時中，請稍後...')

        return data_info

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 獨立參數
    uni_filter_params = {
        's5': '0',  # 0:不需輪班 256:輪班
        'wktm': '1',  # (休假制度) 週休二日
        'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
    }
    
    # 可複合參數
    mul_filter_params = {
        'area': '6001016000',  # (地區)
        's9': '1',  # (上班時段) 日班 1, 夜班 2, 大夜班 4, 假日班 8
        'jobexp': '1,3,5,10,99',  # (經歷要求) 1年以下 1, 1-3年 2, 3-5年 3, 5-10年 4, 10年以上 5
        'zone': '16',  # (公司類型) 16:上市上櫃 5:外商一般 4:外商資訊
        'edu': '1,2,3,4,5',  # (學歷要求) 高中職以下 1,高中職 2,專科 3,大學 4,碩士 5,博士 6
    }

    # 解析可複合篩選條件的所有可能組合
    keys = mul_filter_params.keys()
    values = [v.split(',') for v in mul_filter_params.values()]
    combinations = list(product(*values))  # 產生所有可能組合

    # 轉換成 set 合併重複職缺
    alljobs_set = set()
    for combo in combinations:
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        #total_count, jobs = job104_spider.search(max_mun=10, filter_params=filter_params)
        total_count, jobs = job104_spider.search(22)
        alljobs_set.update(jobs)  # 用 set.update() 合併職缺 ID，去除重複
    
    print('搜尋結果職缺總數：', len(alljobs_set))

    # 逐一取得職缺詳細資料
    job_details = []
    for job_id in alljobs_set:
        job_info = job104_spider.get_job(job_id)
        job_details.append(job_info)

    # 將職缺資料存入 Excel
    df = pd.DataFrame(job_details)
    df.to_excel('104jobs.xlsx', index=False)

    print("職缺資料已成功寫入 jobs.xlsx")
        