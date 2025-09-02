# process_csv.py
import os
import pandas as pd
from glob import glob
from datetime import datetime, timedelta, timezone

# 获取 upload 文件夹下所有 CSV 文件
csv_files = glob('upload/esa_ip_list_*.csv')
if not csv_files:
    raise Exception("No CSV files found in upload folder.")

# 按文件名中的日期排序，获取最新文件
def extract_date(filename):
    base = os.path.basename(filename)
    date_str = base.replace('esa_ip_list_', '').replace('.csv', '')
    return datetime.strptime(date_str, '%Y%m%d')

latest_csv = sorted(csv_files, key=extract_date)[-1]

# 读取 CSV 内容
df = pd.read_csv(latest_csv, sep=',', engine='python')
esa_row = df[df['地址簿名称'].str.contains('ESA Back-to-origin Address', na=False)]

ip_data = esa_row['IP地址/域名'].values[0]
ip_list = ip_data.strip().split('\n')

# 获取当前时间（+8 时区）
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
timestamp = now.strftime('### %Y/%m/%d %H:%M')

# 写入 list 文件夹
os.makedirs('list', exist_ok=True)
with open('list/esa_ip_list_latest.txt', 'w') as f:
    f.write(timestamp + '\n')
    for ip in ip_list:
        f.write(ip.strip() + '\n')

# 移动 CSV 文件到 Archive 文件夹
os.makedirs('Archive', exist_ok=True)
archive_path = os.path.join('Archive', os.path.basename(latest_csv))
os.rename(latest_csv, archive_path)
