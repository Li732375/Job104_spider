# Job104Spider - 104 人力銀行職缺爬蟲

## 前言

因使用數字人力銀行職缺搜尋時，部分條件限制數量導致使用受限，索性直接爬取自行過濾篩選資料更方便。

這是一個用 Python 寫的爬蟲程式，用於爬取 104 人力銀行的職缺資料，能依網站設定篩選條件搜尋職缺，並能將職缺的詳細資訊（如薪資、公司名稱、工作地點等）導出至 CSV 檔案。

---

## 需求

* Python 3.x
* 安裝以下 Python 套件：

  * requests：用於發送 HTTP 請求並取得職缺資料
  * playwright：啟動瀏覽器以取得 cookie / UA
  * playwright-stealth：降低被網站檢測自動化的機率

你可以使用 pip 安裝所需套件：

```bash
pip install requests==2.32.3
pip install playwright==1.57.0
pip install playwright-stealth==2.0.0
```

安裝 Playwright 瀏覽器核心：

```bash
python -m playwright install
```

---

## 使用方式

1. **搜尋職缺**
   使用 `search()` 方法進行職缺搜尋，可自訂最大職缺數量 `max_num`（設為 -1 表示無上限），以及篩選條件。

2. **設定篩選職缺條件**
   篩選條件包括學歷、工作經驗、薪資類型、工作型態等。程式中提供範例參數，可根據需要修改。更多參數詳見 [wiki](https://github.com/Li732375/Job104_spider/wiki)。

3. **資料輸出至 CSV**
   爬取完所有職缺詳細資料後，程式會將資料保存為 `104jobs_日期.csv`。

   * 若同一天多次執行，檔案會被覆蓋，因為檔名只到日期。

---

## 程式介紹

### 主要類別：`Job104Spider`

* `__init__()`
  初始化爬蟲，建立 requests session、清空舊的錯誤紀錄，並啟動瀏覽器取得初始驗證憑證。

* `refresh_session()`
  使用 Playwright 隱身瀏覽器刷新驗證憑證（cookies、user-agent），以應對網站防爬限制。

* `log_error(job_id, message, raw_data=None)`
  將錯誤訊息與原始資料寫入 `error_message.json`，便於後續除錯與紀錄追蹤。

* `fetch_with_retry(url, headers=None, params=None, max_retries=3)`
  對指定 URL 發送 GET 請求，遇到失敗或限制（如 429、403）會自動重試，並在需要時刷新 session。

* `search(max_num=150, filter_params=None)`
  搜尋符合篩選條件的職缺 ID 列表。  
  - `max_num`：最大職缺數量（-1 表示不限）  
  - `filter_params`：篩選條件字典（可包含地區、學歷、工作經驗等）

* `get_job(job_id)`
  取得指定職缺的詳細資訊，包括薪資、公司名稱、工作地點、工作型態、福利、證照要求等。  
  - `job_id`：職缺的唯一 ID  
  - 返回值：`(data_info, error_code)`，`data_info` 為職缺資料字典，`error_code` 表示狀態


---

### 範例程式

參見 [wiki](https://github.com/Li732375/Job104_spider/wiki) 列表，提供各項參數自行調整

```python
...略...

if __name__ == "__main__":
    job104_spider = Job104Spider()

    # 單選參數
    uni_filter_params = {
        's5': '0',  # 0:不需輪班, 256:輪班
        'isnew': '0',  # 更新日期，本日最新 0, 三日內 3, ...
        'wktm': '1',
    }

    # 多選參數
    mul_filter_params = {
        'area': '6001016001,6001016002,6001016003', 
        's9': '1',  # 上班時段：日班 1, 夜班 2, ...
        'jobexp': '1,3',  # 經歷：不拘/1年以下 1, 1-3年 3, ...
        'edu': '3,4,5',  # 學歷：專科 3, 大學 4, 碩士 5
        'jobcat': '2007001004,2007001018,2007001022',
    }

...略...
```

---

## 注意事項

1. 請適度調整 `time.sleep(random.uniform(0.5, 3))`，避免請求過快導致 IP 被封鎖。
2. `error_message.json` 錯誤記錄，如 11100、11025，代表請求過於頻繁，可增加等待時間。
3. CSV 若打開亂碼，可用文字檔開啟另存為 ANSI。
4. `104jobs_日期.csv` 檔名只到日，當天多次執行會覆蓋舊檔。
5. 若表格文字自動換行，可手動取消「自動換行」避免單元格過高。

<<<<<<< HEAD
---
=======
> 覺得 `104jobs_?.csv` 資料格子太高？ 全選表格 > 儲存格格式 > 對齊方式 > 文字控制 > 取消勾選 "自動換行"。

4.  `104jobs_?.csv` 因為檔名時間僅寫到 **日**，同一天的會被覆蓋掉喔！
>>>>>>> f1511dc060ce912e1dcebad99ea5b217ac8abace

## 後記

* 爬取時間依職缺數量而定，> 4000 筆可能需要數小時。
* 資料仍需自行分析與篩選條件。
* 曾嘗試改以 ThreadPoolExecutor 等多進程加速，但逢存取過快同時(使用 async 估計依然不適當)，加上無法執行機器人檢測。首度與 LLM 協作重構。
