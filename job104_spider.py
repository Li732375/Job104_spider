# -*- coding: utf-8 -*-

import time
import random
import requests
from itertools import product
import csv
import json

# 設定標準輸出編碼為 utf-8-sig，避免 cmd、PowerShell、記事本顯示亂碼
import sys
sys.stdout.reconfigure(encoding='utf-8-sig')


class Job104Spider():
    def search(self, max_num=150, filter_params=None): 
        """搜尋職缺"""
        
        # max_num: 指定最大職缺數 (-1 表示翻到最大數量)
        # 每頁提供 22 筆職缺資料，最多可找 150 * 22 = 3300 筆職缺
        
        jobs = []
        total_count = 0
        valid_urls = []
        params = [f'&{key}={value}' for key, value in filter_params.items()]
        
        url = 'https://www.104.com.tw/jobs/search/api/jobs'
        query = f'jobsource=index_s&mode=s'
        
        if filter_params:
            query += ''.join(params)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'Referer': 'https://www.104.com.tw/jobs/search/?',
        }
        
        page = 1
        pagesize = 20
        rework_time = 0
        while max_num == -1 or len(jobs) < max_num:
            params = f'{query}&page={page}&pagesize={pagesize}'
            r = requests.get(url, params=params, headers=headers)
            
            if r.status_code != requests.codes.ok:
                print(f'URL：{url}?{params}')  # 顯示當前請求的 URL
                print(f'職缺清單請求失敗，狀態碼 {r.status_code}')
                print(f'encoding: {r.encoding}')
                
                # 錯誤訊息覆寫入指定檔案，協助除錯
                with open('error_message.json', 'w', encoding='utf-8-sig') as f:
                    json.dump(r.json(), f, ensure_ascii=False, indent=4)  # 使用 indent=4 排版
                
                print(f"完整錯誤訊息：{r.text}")
                print(f"錯誤代碼 {r.json()['error']['code']}")
                print(f"錯誤訊息：{r.json()['error']['message']}")
                print(f"錯誤細節：{r.json()['error']['details']}")
                
                error_code = r.json()['error']['code']
                if rework_time <= 3 and error_code in (11100, 11025):
                    time.sleep(random.uniform(3, 5))
                    rework_time += 1
                    continue
                else:
                    rework_time = 0
                    break
            
            rework_time = 0
            datas = r.json()
            # 最後資料覆寫入指定檔案，協助除錯
            with open('final_job_search_list.json', 'w', encoding='utf-8-sig') as f:
                f.write('//' + f'"encoding": "{r.encoding}"' + '\n')
                json.dump(datas, f, ensure_ascii=False, indent=4)

            total_count = datas['metadata']['pagination']['total']
            
            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(
                data['link']['job'].split('/job/')[-1] \
                    for data in datas['data'])
            
            # 如果是最後一頁或空頁，就跳出迴圈
            if page == datas['metadata']['pagination']['lastPage'] or \
                datas['metadata']['pagination']['lastPage'] == 0:
                if total_count != 0:
                    valid_urls.append(f'{query}')
                break
            
            time.sleep(random.uniform(1.5, 2.5))

            page += 1
        
        # 如果 max_num 超過 jobs 長度，會自動調整切片範圍，不會拋出 IndexError。
        return valid_urls, jobs[:max_num]

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
            with open('error_message.json', 'w', encoding='utf-8-sig') as f:
                json.dump(r.json(), f, ensure_ascii=False, indent=4)  # 使用 indent=4 排版
            
            print(f"完整錯誤訊息：{r.text}")
            print(f"錯誤代碼 {r.json()['error']['code']}")
            print(f"錯誤訊息：{r.json()['error']['message']}")
            print(f"錯誤細節：{r.json()['error']['details']}")
                
            return None, r.json()['error']['code']

        job_data = r.json()['data']
        # 最後資料覆寫入指定檔案，協助除錯
        with open('final_job_url.json', 'w', encoding='utf-8-sig') as f:
            f.write('//' + f'"encoding": "{r.encoding}"' + ', ' + 
                    f'"URL": "https://www.104.com.tw/job/{job_id}"\n')
            json.dump(job_data, f, ensure_ascii=False, indent=4)  # 使用 indent=4 美化 JSON

        # 部分職缺因時間差異，已經被關閉
        if job_data['switch'] == 'off':
            return None, 0

        salary_type = {
            10: '面議',
            20: '論件計酬',
            30: '時薪',
            40: '日薪',
            50: '有薪',
            60: '年薪',
            70: '其他',
        }

        # 職缺 (全職、兼職、長短期假日工讀..)
        workType = '全職' if len(job_data['jobDetail']['workType']) == 0 \
            else ', '.join([item for item in job_data['jobDetail']['workType']])
        jobArea = job_data['jobDetail']['addressRegion'] \
            if len(job_data['jobDetail']['addressRegion']) == 3 \
                else job_data['jobDetail']['addressRegion'][3:]
        jobAddress = '無' if len(job_data['jobDetail']['addressDetail']) == 0 \
            else job_data['jobDetail']['addressDetail']
        jobDes =  '無' if len(job_data['jobDetail']['jobDescription']) == 0 \
            else job_data['jobDetail']['jobDescription']
        jobDesOther =  '無' if len(job_data['condition']['other']) == 0 \
            else job_data['condition']['other']
        cert = job_data['condition']['certificate']
        certificate = '無' if len(cert) == 0 \
            else ', '.join(item['name'] for item in cert)
        driverLicense_list = job_data['condition']['driverLicense']
        driverLicense = '無' if len(driverLicense_list) == 0 \
            else ', '.join([item for item in driverLicense_list])
        businessTrip = '無' if len(job_data['jobDetail']['businessTrip']) == 0 \
            else job_data['jobDetail']['businessTrip']
        specialty =  '無' if len(job_data['condition']['specialty']) == 0 \
            else ', '.join(item['description'] for item in \
                           job_data['condition']['specialty'])
        isActivelyHiring = '是' if job_data['header']['isActivelyHiring'] == \
            True else '否'
        legalTag = '無' if len(job_data['welfare']['legalTag']) == 0 \
            else ', '.join(job_data['welfare']['legalTag'])

        data_info = {
            '更新日期': job_data['header']['appearDate'],
            '工作型態': workType,  
            '工作時段': job_data['jobDetail']['workPeriod'],
            '薪資類型': salary_type[job_data['jobDetail']['salaryType']],
            '最高薪資': int(job_data['jobDetail']['salaryMax']),
            '最低薪資': int(job_data['jobDetail']['salaryMin']),
            '職缺名稱': job_data['header']['jobName'],
            '學歷': job_data['condition']['edu'],
            '工作經驗': job_data['condition']['workExp'],
            '工作縣市': job_data['jobDetail']['addressArea'],
            '工作里區': jobArea,
            '工作地址': jobAddress,
            '公司名稱': job_data['header']['custName'],
            '職缺描述': jobDes,
            '其他描述': jobDesOther,
            '擅長要求': specialty,
            '證照': certificate,
            '駕駛執照': driverLicense,
            '出差': businessTrip,
            '積極徵才': isActivelyHiring,
            '104 職缺網址': f'https://www.104.com.tw/job/{job_id}',
            '公司產業類別': job_data['industry'],
            '法定福利': legalTag,
            #'其他福利': job_data['welfare']['welfare'],
        }

        return data_info, 0

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 獨立參數(單選)
    uni_filter_params = {
        's5': '0',  # 0:不需輪班 256:輪班
        'isnew': '3',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        'wktm': '1',
        'ro': '1',
    }
    
    # 可複合參數(多選)，可能要避免使用 '\' 換行，雖然能執行，卻會影響輸出內容
    mul_filter_params = {
        'area': '6001016001,6001016002,6001016003,6001016004,6001016005,6001016007,6001016008,6001016011,6001016024,6001016027,6001014001,6001014002,6001014003,6001014004,6001014008,6001014014,6001001000',  # (地區) 
        'jobexp': '1,3',  # (經歷) 1: 不拘 / 1年以下, 3: 1-3年, 5: 3-5年, 10: 5-10年, 99: 10年以上
        'edu': '3,4,5',  # (學歷) 1: 高中職以下, 2: 高中職, 3: 專科, 4: 大學, 5: 碩士, 6: 博士
        'jobcat': '2007001004,2007001018,2007001022,2007001020,2007001012,2007001009,2007001010,2016001013',  # (職位類別)
        # 'wt': '1,2,4,8,16',  # (工讀類型) 1: 長期, 2: 短期, 4: 假日, 8: 寒假, 16: 暑假
    }

    # 解析可複合篩選條件的所有可能組合
    keys = mul_filter_params.keys()
    values = [v.split(',') for v in mul_filter_params.values()]
    combinations = list(product(*values))  # 產生所有可能組合
    print('搜尋條件組合總數：', len(combinations))

    # 無論檔案是否存在(不再就建立一個)，再清空紀錄檔案
    open('valid_params_list.csv', 'w', encoding='utf-8').close()

    # 每個條件組合要取得的職缺數
    max_num = 20

    # 使用篩選條件，轉換成 set 合併重複職缺
    alljobs_set = set()

    for idx, combo in enumerate(combinations, start=1):  # 避免從 0 開始影響百分比計算
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        valid_url_list, jobs = job104_spider.search(max_num=max_num, 
                                       filter_params=filter_params)
        
        # 紀錄有效網址參數
        with open('valid_params_list.csv', 'a', encoding='utf-8') as f:
            for param in valid_url_list:
                f.write(param + '\n')
        
        # 計算當前進度百分比
        progress = (idx / len(combinations)) * 100
        print(f"更換條件探索中：{progress:>6.2f} % ({idx}/{len(combinations)})", 
              end='\r')

        # 若是常常逢錯誤 11100，可以考慮放緩頻率
        time.sleep(random.uniform(0.5, 1.5))
        
        alljobs_set.update(jobs)  # 用 set.update() 合併，去除重複職缺 ID

    """
    # 不使用篩選條件，如果只想取得最新職缺，註解掉上面的區域
    total_count, jobs = job104_spider.search(max_num)
    alljobs_set = set(jobs)
    """ 
    total_jobs = len(alljobs_set)  # 總職缺數
    print('總職缺數：', total_jobs)

    # 逐一寫入取得的職缺詳細資料
    print('逐一取得職缺詳細資料中...')

    today = time.strftime("%Y-%m-%d")
    Output_csv_FileName = f'104jobs_{today}.csv'

    for idx, job_id in enumerate(alljobs_set, start=1):
        job_info, error_code = job104_spider.get_job(job_id)

        error_time = 0
        while error_time <= 3 and error_code in (11100, 11025):
            time.sleep(random.uniform(3, 5))
            job_info, error_code = job104_spider.get_job(job_id)
            error_time += 1

        if job_info is not None:
            if idx == 1:
                with open(Output_csv_FileName, mode='w', encoding='utf-8-sig', 
                          newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(job_info.keys())
                    writer.writerow(job_info.values())
            else:
                with open(Output_csv_FileName, mode='a', encoding='utf-8-sig', 
                          newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(job_info.values())

        # 隨機等待幾秒
        time.sleep(random.uniform(0.5, 1.5))
        
        # 計算進度百分比
        progress = (idx / total_jobs) * 100
        print(f"職缺資料抓取進度：{progress:>6.2f} % ({idx}/{total_jobs})", 
              end='\r')
    
    print(f"職缺資料已寫入 {Output_csv_FileName}")
