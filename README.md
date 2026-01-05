# JobE04Spider - 數字人力銀行職缺爬蟲

## 前言

因使用數字人力銀行職缺搜尋時，部分條件限制數量導致使用受限，索性直接爬取自行過濾篩選資料更方便。

這是一個用 Python 寫的爬蟲程式，用於爬取數字人力銀行的職缺資料，能依網站設定篩選條件搜尋職缺，並能將職缺的詳細資訊（如薪資、公司名稱、工作地點等）導出至 CSV 檔案。

---

## 需求

* Python 3.x
* 安裝以下 Python 套件：

  * requests：用於發送 HTTP 請求並取得職缺資料
  * playwright：啟動瀏覽器以取得 cookie / UA
  * playwright-stealth：降低被網站檢測自動化的機率

安裝所需套件（以 pip 為例）：

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

1. **設定篩選職缺條件**
   篩選條件包括學歷、工作經驗、薪資類型、工作型態等。程式中提供範例參數，可根據需要修改。更多參數詳見 [wiki](https://github.com/Li732375/JobE04_spider/wiki)。

2. **資料輸出至 CSV**
   爬取完所有職缺詳細資料後，將資料存至 `job_list_日期.csv`。

   * 若同一分鐘內完成多次執行，檔案會被覆蓋，因為檔名只到分鐘。

---

## 程式介紹

### 流程

```
初始化 → 取得篩選條件 → 產生組合 → 搜尋職缺 ID → 抓取詳情 → 輸出 CSV
```

若程式中途停掉：

* CSV 裡的資料不會發生「因中斷導致整批沒寫」的情況

---

結論：
> **先蒐集完全部 job id → 然後逐筆抓詳情 → 每抓到一筆就立刻寫入 CSV**

### 範例程式

參見 [wiki](https://github.com/Li732375/JobE04_spider/wiki) 列表，提供各項參數自行增添調整

```python
...略...
class JobE04Spider():
    def __init__(self):
        self.session = requests.Session()
        self.headers_user_agent: str = ""
        self.error_log_file: str = 'error_message.json'

        # 獨立篩選條件{}
        self.uni_filter_params: Dict[str, str] = { 
            's5': '0',  # 0:不需輪班, 256:輪班
            'isnew': '3',  # 更新日期，本日最新 0, 三日內 3, ...
            'wktm': '1',  # 週休二日:有
            'ro': '1',  # 工作型態
        }
        # 複合篩選條件{}
        self.mul_filter_params: Dict[str, str] = {
            'area': '6001001000,6001016000,6001002011',  # 工作地區:台北/高雄/新店
            's9': '1',  # 上班時段：日班 1, 夜班 2, ...
            'jobexp': '1,3',   # 經歷：不拘/1年以下 1, 1-3年 3, ...
            'edu': '3,4,5',  # 學歷：專科 3, 大學 4, 碩士 5
            'jobcat': '2007001004,2007001020',  # 職務類別:軟體工程師/AI工程師
        }
        # 職缺欄位順序[]
        self.field_names_order: List[str] = [
            '更新日期', '工作型態', '工作時段', '薪資類型', '最低薪資',
            '最高薪資', '職缺名稱', '學歷', '工作經驗', '工作縣市',
            '工作里區', '工作地址', '公司名稱', '職缺描述', '其他描述',
            '擅長要求', '證照', '駕駛執照', '出差', '104 職缺網址',
            '公司產業類別', '法定福利'
        ]

...略...
```

---

## 注意事項

1. 請適度調整 `time.sleep(random.uniform(0.5, 3))`，避免請求過快導致 IP 被封鎖。
2. `error_message.json` 錯誤記錄，如 11100、11025，代表請求過於頻繁，可增加等待時間。
3. CSV 若打開亂碼，可用文字檔開啟另存為 ANSI。
4. 若表格文字自動換行，可手動取消「自動換行」避免單元格過高。

---

> 覺得 `job_list_日期_?.csv` 資料格子太高？ 全選表格 > 儲存格格式 > 對齊方式 > 文字控制 > 取消勾選 "自動換行"。

5. `job_list_日期_?.csv` 因為檔名時間僅寫到 **分**，同一分鐘完成的會被覆蓋掉喔！

## 後記

* 爬取時間依職缺數量而定，> 4000 筆可能需要數小時。
* 資料仍需自行分析與篩選條件。
* 曾嘗試改以 ThreadPoolExecutor 等多進程加速，但逢存取過快同時(使用 async 估計依然不適當)，加上無法執行機器人檢測。首度與 Chatgpt 協作重構。
