# Job104Spider - 104 人力銀行職缺爬蟲

這是一個用 Python 寫的爬蟲程式，主要用於爬取 104 人力銀行的職缺資料，並將結果儲存為 Excel 檔案。該程式支援依照特定篩選條件搜尋職缺，並能夠將職缺的詳細資訊（如薪資、公司名稱、工作地點等）導出至 Excel 檔案。

## 需求

- Python 3.x
- 安裝以下 Python 套件：
  - `requests`
  - `pandas`

您可以使用 pip 安裝所需的套件：

```
pip install requests pandas
```

## 使用方式

1. **搜尋職缺**  
   使用 `search()` 方法進行職缺搜尋，您可以設定最大職缺數量 `max_mun`，以及篩選條件 `filter_params`。如果您希望搜尋所有職缺，可以將 `max_mun` 設為 -1。

2. **篩選職缺條件**  
   篩選條件包括學歷、工作經驗、薪資類型、工作型態等。程式中提供了範例的篩選參數。您可以根據需要進行修改。

3. **獲取職缺詳細資料**  
   使用 `get_job()` 方法來獲取單一職缺的詳細資訊，返回一個包含職缺詳細資訊的字典。

4. **將資料輸出至 Excel**  
   當爬取完所有職缺的詳細資料後，程式會將這些資料保存為 `104jobs.xlsx` 的 Excel 檔案。

## 程式介紹

### 主要類別：`Job104Spider`

1. **search(max_mun=150, filter_params=None)**  
   用於搜尋職缺，您可以指定搜尋條件，並設定搜尋的最大職缺數量 `max_mun`。若 `max_mun` 設為 -1，則會搜尋所有可用的職缺。更多 `filter_params` 參數，見 [wiki](https://github.com/Li732375/Job104_spider/wiki)。

2. **get_job(job_id)**  
   用於獲取某一職缺的詳細資料，返回一個包含職缺詳細資訊的字典。

### 範例程式

```
if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 獨立篩選參數
    uni_filter_params = {
        's5': '0',  # 不需輪班
        'wktm': '1',  # 週休二日
        'isnew': '0',  # 本日最新
    }
    
    # 可複合篩選參數
    mul_filter_params = {
        'area': '6001016000',  # 地區
        's9': '1',  # 上班時段
        'jobexp': '1,3,5,10,99',  # 經歷要求
        'zone': '16',  # 公司類型
        'edu': '1,2,3,4,5',  # 學歷要求
    }

    # 解析篩選條件的所有組合
    keys = mul_filter_params.keys()
    values = [v.split(',') for v in mul_filter_params.values()]
    combinations = list(product(*values))  # 產生所有篩選條件的組合

    # 用 set 合併職缺 ID，避免重複
    alljobs_set = set()
    for combo in combinations:
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        total_count, jobs = job104_spider.search('python', max_mun=10, filter_params=filter_params)
        alljobs_set.update(jobs)  # 合併職缺 ID
    
    print('搜尋結果職缺總數：', len(alljobs_set))

    # 逐一獲取職缺詳細資料
    job_details = []
    for job_id in alljobs_set:
        job_info = job104_spider.get_job(job_id)
        job_details.append(job_info)

    # 儲存職缺資料至 Excel
    df = pd.DataFrame(job_details)
    df.to_excel('104jobs.xlsx', index=False)

    print("職缺資料已成功寫入 jobs.xlsx")
```

### 輸出結果

爬取的職缺資料將儲存於 `104jobs.xlsx` 檔案，包含以下欄位：

- 更新日期
- 學歷要求
- 工作經驗要求
- 薪資類型
- 最高薪資
- 最低薪資
- 工作型態
- 職缺名稱
- 職缺描述
- 公司名稱
- 工作縣市
- 工作時段
- 法定福利
- 其他福利
- 104 網址
- 公司網址

## 注意事項

1. 由於程式會進行多次 HTTP 請求，建議使用者遵守 104 人力銀行的使用規範。
2. 由於資料的篩選與搜尋範圍較大，建議設置合理的最大職缺數量。
