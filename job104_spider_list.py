# -*- coding: utf-8 -*-

import time
import random
import requests
import pandas as pd
import json
import os

# 設定標準輸出編碼為 utf-8
import sys
sys.stdout.reconfigure(encoding='utf-8')


class Job104Spider():
    def search(self, max_num=150, query=None): 
        """搜尋職缺"""
        
        # max_num: 指定最大職缺數 (-1 表示翻到最大數量)
        # 每頁提供 22 筆職缺資料，最多可找 150 * 22 = 3300 筆職缺
        
        jobs = []
        
        url = 'https://www.104.com.tw/jobs/search/api/jobs'
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
                print(f'URL：{url}?{params}')  # 顯示當前請求的 URL
                print(f'職缺清單請求失敗，狀態碼 {r.status_code}')
                print(f'encoding: {r.encoding}')
                
                # 錯誤訊息覆寫入指定檔案，協助除錯
                with open('error_message.json', 'w', encoding='utf-8') as f:
                    json.dump(r.json(), f, ensure_ascii=False, indent=4)  # 使用 indent=4 排版
                
                print(f"完整錯誤訊息：{r.text}")
                print(f"錯誤代碼 {r.json()['error']['code']}")
                print(f"錯誤訊息：{r.json()['error']['message']}")
                print(f"錯誤細節：{r.json()['error']['details']}")

                time.sleep(random.uniform(3, 5))
                break
            
            datas = r.json()
            
            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(
                data['link']['job'].split('/job/')[-1] for data in datas['data'])
            
            # 如果是最後一頁或空頁，就跳出迴圈
            if page == datas['metadata']['pagination']['lastPage'] or \
                datas['metadata']['pagination']['lastPage'] == 0:
                break
            
            print(f'清單資料({len(jobs)}筆)，緩衝中...')
            time.sleep(random.uniform(3, 5))

            page += 1
        
        return jobs[:max_num]

    def get_job(self, job_id):
        """取得職缺網址詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': f'https://www.104.com.tw/job/{job_id}',
        }

        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print(f'URL：{url}')  # 顯示當前請求的 URL
            print(f'職缺資訊請求失敗，狀態碼 {r.status_code}')
            print(f'encoding: {r.encoding}')
            
            # 錯誤訊息覆寫入指定檔案，協助除錯
            with open('error_message.json', 'w', encoding='utf-8') as f:
                json.dump(r.json(), f, ensure_ascii=False, indent=4)  # 使用 indent=4 排版
            
            print(f"完整錯誤訊息：{r.text}")
            print(f"錯誤代碼 {r.json()['error']['code']}")
            print(f"錯誤訊息：{r.json()['error']['message']}")
            print(f"錯誤細節：{r.json()['error']['details']}")

            time.sleep(random.uniform(3, 5))
            return

        job_data = r.json()['data']
        # 最後資料覆寫入指定檔案，協助除錯
        with open('final_job_url.json', 'w', encoding='utf-8') as f:
            f.write('//' + f'"encoding": "{r.encoding}"' + ', ' + f'"URL": "https://www.104.com.tw/job/{job_id}"\n')
            json.dump(job_data, f, ensure_ascii=False, indent=4)  # 使用 indent=4 美化 JSON

        # 部分職缺因時間差異，已經被關閉
        if job_data['switch'] == 'off':
            return 

        salary_type = {
            10: '面議',
            20: '論件計酬',
            30: '時薪',
            40: '日薪',
            50: '有薪',
            60: '年薪',
        }

        # 職缺 (全職、兼職、長短期假日工讀..)
        workType = '全職' if len(job_data['jobDetail']['workType']) == 0 \
            else ', '.join([item for item in job_data['jobDetail']['workType']])
        jobArea = job_data['jobDetail']['addressRegion'] \
            if len(job_data['jobDetail']['addressRegion']) == 3 \
                else job_data['jobDetail']['addressRegion'][3:]
        certificate = '無' if len(job_data['condition']['certificate']) == 0 \
            else ', '.join(info['name'] for info in job_data['condition']['certificate'])
        driverLicense_list = job_data['condition']['driverLicense']
        driverLicense = '無' if len(driverLicense_list) == 0 \
            else ', '.join([item for item in driverLicense_list])

        data_info = {
            '更新日期': job_data['header']['appearDate'],
            '學歷': job_data['condition']['edu'],
            '工作經驗': job_data['condition']['workExp'],
            '工作型態': workType,  
            '薪資類型': salary_type[job_data['jobDetail']['salaryType']],
            '最高薪資': int(job_data['jobDetail']['salaryMax']),
            '最低薪資': int(job_data['jobDetail']['salaryMin']),
            '工作縣市': job_data['jobDetail']['addressArea'],
            '工作里區': jobArea,
            '工作地址': job_data['jobDetail']['addressDetail'],
            '工作時段': job_data['jobDetail']['workPeriod'],
            '公司名稱': job_data['header']['custName'],
            '公司產業類別': job_data['industry'],
            '職缺名稱': job_data['header']['jobName'],
            '職缺描述': job_data['jobDetail']['jobDescription'],
            '104 職缺網址': f'https://www.104.com.tw/job/{job_id}',
            '證照': certificate,
            '駕駛執照': driverLicense,
            '法定福利': ', '.join(job_data['welfare']['legalTag']),
            #'其他福利': job_data['welfare']['welfare'],
        }

        return data_info

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 每個條件組合要取得的職缺數
    max_num = -1
    alljobs_set = set()

    # 讀取查詢條件
    with open('valid_params_list.csv', 'r', encoding='utf-8') as f:
        for idx, query in enumerate(f, start=1):
            query = query.strip()  # 去除換行符號
            jobs = job104_spider.search(max_num, query)

            # 只顯示當前處理的查詢編號
            print(f"正在處理第 {idx} 行查詢，共 {len(jobs)} 筆...", end='\r')

            alljobs_set.update(jobs)

    total_jobs = len(alljobs_set)  # 總職缺數
    print('總職缺數：', total_jobs)

    # 逐一取得職缺詳細資料
    print('逐一取得職缺詳細資料中...')

    job_details = []
    for idx, job_id in enumerate(alljobs_set, start=1):
        job_info = job104_spider.get_job(job_id)
        job_details.append(job_info)
        
        # 隨機等待幾秒
        time.sleep(random.uniform(1, 2))
                
        # 計算進度百分比
        progress = (idx / total_jobs) * 100
        print(f"職缺資料抓取進度：{progress:>6.2f} % ({idx}/{total_jobs})", 
              end='\r')

    # 將職缺資料存入 Excel
    df = pd.DataFrame(job_details)
    Output_Excel_FileName = '104jobs.xlsx'
    df.to_excel(Output_Excel_FileName, index=False)
    
    print(f"職缺資料已寫入 {Output_Excel_FileName}")
