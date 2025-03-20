# Job104Spider - 104 人力銀行職缺爬蟲

這是一個用 Python 寫的爬蟲程式，主要用於爬取 104 人力銀行的職缺資料，並將結果儲存為 Excel 檔案。該程式支援依照特定篩選條件搜尋職缺，並能夠將職缺的詳細資訊（如薪資、公司名稱、工作地點等）導出至 Excel 檔案。

## 需求

- Python 3.x
- 安裝以下 Python 套件：
   - requests：用於發送 HTTP 請求並取得職缺資料
   - pandas：用於處理資料並輸出 Excel 檔案
   - openpyxl：支援 Excel 2007 (.xlsx) 格式的寫入

您可以使用 pip 安裝所需的套件：

```
pip install requests pandas openpyxl
```

## 使用方式

1. **搜尋職缺**  
   使用 `search()` 方法進行職缺搜尋，您可以自訂最大職缺數量 `max_mun` (設為 -1 表示上限)，以及兩類篩選條件欄位與內容。更多參數，見 [wiki](https://github.com/Li732375/Job104_spider/wiki)。

2. **篩選職缺條件**  
   篩選條件包括學歷、工作經驗、薪資類型、工作型態等。程式中提供了範例的篩選參數。您可以根據需要進行修改。

3. **獲取職缺詳細資料**  
   使用 `get_job()` 方法來獲取單一職缺的詳細資訊。

4. **將資料輸出至 Excel**  
   當爬取完所有職缺的詳細資料後，程式會將這些資料保存為 `104jobs.xlsx` 的 Excel 檔案。

## 程式介紹

### 主要類別：`Job104Spider`

1. **search(max_mun=150, filter_params=None)**  
   用於搜尋條件下職缺清單。

2. **get_job(job_id)**  
   獲取某一職缺的詳細資訊。

### 範例程式

```
if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 獨立參數 (單選)
    uni_filter_params = {
        's5': '0',  # 0:不需輪班 256:輪班
        'isnew': '0',  # (更新日期) 0:本日最新 3:三日內 7:一週內 14:兩週內 30:一個月內
        'wktm': '1',
    }
    
    # 可複合參數 (多選)，可能要避免使用 '\' 換行，雖然能執行，卻會影響輸出
    mul_filter_params = {
        'area': '6001016001,6001016002,6001016003,6001016004,6001016005,6001016007,6001016008,6001016011,6001016024,6001016027',  # (地區) 
        's9': '1',  # (上班時段) 日班 1, 夜班 2, 大夜班 4, 假日班 8
        'jobexp': '1,3',  # (經歷) 不拘/1年以下 1, 1-3年 3, 3-5年 5, 5-10年 10, 10年以上 99
        'edu': '3,4,5',  # (學歷) 高中職以下 1,高中職 2,專科 3,大學 4,碩士 5,博士 6
        'jobcat': '2007001004,2007001018,2007001022',  # (職位類別)
        #'wt': '1,2,4,8,16',  # (工讀類型) 長期 1, 短期 2, 假日 4, 寒假 8, 暑假 16
    }

    ... code ...

    print('搜尋條件組合總數：', len(combinations))

    # 無論檔案是否存在(不再就建立一個)，再清空紀錄檔案
    open('valid_params_list.csv', 'w', encoding='utf-8').close()

    # 每個條件組合要取得的職缺數
    max_num = 100

    ... code ...

    for idx, combo in enumerate(combinations, start=1):  # 避免從 0 開始影響百分比計算
        filter_params = {**uni_filter_params, **dict(zip(keys, combo))}
        valid_url_list, jobs = job104_spider.search(max_num=max_num, 
                                       filter_params=filter_params)
        ... code ...
    ... code ...

    print('總職缺數：', len(alljobs_set))

    # 逐一取得職缺詳細資料
    print('逐一取得職缺詳細資料...')

    ... code ...

    # 將職缺資料存入 Excel

    ... code ...

```

### 輸出結果

1. 爬取的職缺資料將儲存於 `104jobs.xlsx` 檔案，包含以下欄位：

- 更新日期
- 學歷
- 工作經驗
- 工作型態
- 薪資類型
- 最高薪資
- 最低薪資
- 工作縣市
- 工作地址
- 工作時段
- 公司名稱
- 公司產業類別
- 職缺名稱
- 職缺描述
- 104 職缺網址
- 法定福利
- 其他福利 (需要再自行增減欄位，json 內抓的到就行)

2. 輸出有資料的參數都記錄於 `valid_params_list.csv`，下次就可以直接用另一支程式 `job104_spider_list.py` 執行囉！

3. 有問題的職缺清單連結都記錄於 `final_job_search_list`

4. 有問題的職缺資訊連結都記錄於 `final_job_url.json`

5. 有問題的爬取資訊記錄於 `error_message.json`

## 注意事項

1. 由於資料的篩選與搜尋範圍較大，請適當調整 time.sleep(random.uniform(1, 2)) 的等待時間，避免過快請求導致 IP 被封鎖。
2. 如果頻繁遇到錯誤碼 11100，可能是請求過於頻繁，請增加等待時間。
