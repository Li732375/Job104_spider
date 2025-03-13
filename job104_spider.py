import time
import random
import requests


class Job104Spider():
    def search(self, max_mun=150): 
        """搜尋職缺"""

        # 這裡的 max_mun 指前面頁的職缺筆數(即使總值缺數更大，但上限僅供到 150 頁)
        # 每頁提供 22 筆職缺資料，所以最多只能找 150 * 22 = 3300 筆職缺資料

        jobs = []
        total_count = 0

        url = 'https://www.104.com.tw/jobs/search/api/jobs?'
        query = f'jobsource=joblist_search&mode=s'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Refreer': 'strict-origin-when-cross-origin',
        }

        page = 1
        pagesize = 20
        while len(jobs) < max_mun:
            params = f'{query}&page={page}&pagesize={pagesize}'
            r = requests.get(url, params=params, headers=headers)
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                data = r.json()
                break

            datas = r.json()
            total_count = datas['metadata']['pagination']['total']

            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(data['link']['job'].split('/job/')[-1] for data in datas['data'])
            
            # 如果是最後一頁，就跳出迴圈
            if (page == datas['metadata']['pagination']['lastPage']) or (datas['metadata']['pagination']['lastPage'] == 0):
                break
            # 如果不是最後一頁，就繼續下一頁
            page += 1
            # 隨機等待 3~5 秒
            time.sleep(random.uniform(3, 5))

        return total_count, jobs
    
    def search(self, max_mun=150, filter_params=None): 
        """搜尋職缺"""

        # 這裡的 max_mun 指前面頁的職缺筆數(即使總值缺數更大，但上限僅供到 150 頁)
        # 每頁提供 22 筆職缺資料，所以最多只能找 150 * 22 = 3300 筆職缺資料

        jobs = []
        total_count = 0

        url = 'https://www.104.com.tw/jobs/search/api/jobs?'
        query = f'jobsource=joblist_search&mode=s'
        if filter_params:
            # 加上篩選參數，要先轉換為 URL 參數字串格式
            query += ''.join([f'&{key}={value}' for key, value, in filter_params.items()])
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Refreer': 'strict-origin-when-cross-origin',
        }

        page = 1
        pagesize = 20
        while len(jobs) < max_mun:
            params = f'{query}&page={page}&pagesize={pagesize}'
            r = requests.get(url, params=params, headers=headers)
            if r.status_code != requests.codes.ok:
                print('請求失敗', r.status_code)
                data = r.json()
                break

            datas = r.json()
            total_count = datas['metadata']['pagination']['total']

            # 將每一頁的職缺網址代碼加入 jobs
            jobs.extend(data['link']['job'].split('/job/')[-1] for data in datas['data'])
            
            # 如果是最後一頁或空頁，就跳出迴圈
            if (page == datas['metadata']['pagination']['lastPage']) or (datas['metadata']['pagination']['lastPage'] == 0):
                break
            # 如果不是最後一頁，就繼續下一頁
            page += 1
            # 隨機等待 3~5 秒
            time.sleep(random.uniform(3, 5))

        return total_count, jobs

    def get_job(self, job_id):
        """取得職缺網址詳細資料"""
        url = f'https://www.104.com.tw/job/ajax/content/{job_id}'

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Refreer': 'strict-origin-when-cross-origin',
        }

        r = requests.get(url, headers=headers)
        if r.status_code != requests.codes.ok:
            print('請求失敗', r.status_code)
            return

        data = r.json()

        # 職缺資料細節
        data_info = {
            data['data']['welfare']['tag'] + data['data']['welfare']['legalTag'],
            data['data']['jobDetail'],
        }
        
        # 隨機等待 3~5 秒
        time.sleep(random.uniform(3, 5))

    def search_job_transform(self, job_data):
        """將職缺資料轉換格式、補齊資料"""
        job_url = f"https:{job_data['link']['job']}"
        job_company_url = f"https:{job_data['link']['cust']}"
        salary_high = int(job_data['salaryLow'])
        salary_low = int(job_data['salaryHigh'])

        salary_type = {
            10: '面議',
            50: '有薪',
        }

        edu = {
            1: '高中以下',
            2: '高中',
            3: '專科',
            4: '大學',
            5: '碩士',
            6: '博士',
        }

        period = {
            0: '不拘',
            1: 'bug 修正回報',
            2: '1年以上',
            3: '2年以上',
            4: '3年以上',
        }

        jobRo = {
            1: '全職',
            2: '工讀',
        }

        job = {
            'appear_date': job_data['appearDate'],  # 更新日期
            'education': edu[max(job_data['optionEdu'])],  # 最高學歷
            'period': period[job_data['period']],  # 幾年以上工作經驗
            'salary_type': salary_type[job_data['s10']],  # 薪資類型 (面議 / 有薪資)
            'salary_high': salary_high,  # 薪資最高
            'salary_low': salary_low,  # 薪資最低
            'jobRo': jobRo[job_data['jobRo']],  # 職缺工作型態 (全職、兼職、工讀)
            'name': job_data['jobName'],  # 職缺名稱
            'desc': job_data['descSnippet'],  # 描述
            'company_name': job_data['custName'],  # 公司名稱
            'company_city': job_data['jobAddrNoDesc'][:3],  # 工作縣市
            'company_district': job_data['jobAddrNoDesc'][3:],  # 工作里區
            'time': job_data['d3'],  # 工作時段
            'job_url': job_url,  # 職缺網頁
            'job_104_company_url': job_company_url,  # 公司 104 介紹網頁
            'tags': job_data['tags'],  # 標籤
        }
        
        return job


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
        'area': '6001016000',  # (地區) 複
        's9': '1',  # (上班時段) 複 日班,夜班,大夜班,假日班
        'jobexp': '1,3,5,10,99',  # (經歷要求) 1年以下,1-3年,3-5年,5-10年,10年以上
        'zone': '16',  # (公司類型) 16:上市上櫃 5:外商一般 4:外商資訊
        'edu': '1,2,3,4,5,6',  # (學歷要求) 高中職以下,高中職,專科,大學,碩士,博士
        # 'excludeJobKeyword': '科技',  # 排除關鍵字
    }

    # 委託排列組合非複合參數執行搜索
    filter_params = uni_filter_params | mul_filter_params
    total_count, jobs = job104_spider.search('python', max_mun=10, filter_params=filter_params)

    # 轉換成 set 合併重複職缺


    #print('搜尋結果職缺總數：', )

    # 待交叉比對職缺資料結果再行取用
    for jobid in jobs:
        job104_spider.get_job(jobid)
        #print(jobs)
