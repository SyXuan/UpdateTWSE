# UpdateTWSE
Python抓取證券交易所上市股票資料  
  
因為證交所2017年5月大改版，  
網路上其他opensource都無法抓資料，  
只好自己寫一個。  
  
會將股票資料透過 pandas 格式存到 save/[股票代碼].pickle  
  
## Requirement
  
python 2.7  
pandas (>=0.18.0)  
bs4  
lxml (if needed)  
wget (if needed)  
  
## Python files
UpdateTWSE.py  
  
參數設定:  
cleanData: 是否每次清除舊資料，預設False  
getRange:  是否從自設startDate開始，預設False，從81年1月1日開始  
startDate:  timedelta可設定往前幾天  
  
## 版本紀錄
### 2017.06.07
First commit.  
  
