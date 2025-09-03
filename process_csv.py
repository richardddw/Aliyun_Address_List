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

# 获取当前时间（+8 时区）
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
timestamp = now.strftime('### %Y/%m/%d %H:%M')

# 创建输出目录
os.makedirs('docs', exist_ok=True)
os.makedirs('docs/address_books', exist_ok=True)

# 遍历所有地址簿行，生成独立 txt 文件
for _, row in df.iterrows():
    name = str(row['地址簿名称']).strip().replace(' ', '_').replace('/', '_')
    ip_data = str(row['IP地址/域名']).strip()
    if not ip_data or ip_data.lower() == 'nan':
        continue
    ip_list = ip_data.split('\n')
    file_path = os.path.join('docs/address_books', f'{name}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(timestamp + '\n')
        for ip in ip_list:
            f.write(ip.strip() + '\n')

# 单独处理 ESA 地址簿（保留原逻辑）
esa_row = df[df['地址簿名称'].str.contains('ESA Back-to-origin Address', na=False)]
ip_data = esa_row['IP地址/域名'].values[0]
ip_list = ip_data.strip().split('\n')
with open('docs/esa_ip_list_latest.txt', 'w') as f:
    f.write(timestamp + '\n')
    for ip in ip_list:
        f.write(ip.strip() + '\n')

# 生成 index.html 导航页面
index_path = 'docs/index.html'
with open(index_path, 'w', encoding='utf-8') as f:
    f.write('<html><head><meta charset="UTF-8"><title>地址簿导航</title></head><body>\n')
    f.write('<h1>📒 地址簿列表</h1><ul>\n')
    for file in sorted(os.listdir('docs/address_books')):
        name = file.replace('.txt', '')
        f.write(f'<li><a href="address_books/{file}">{name}</a></li>\n')
    f.write('</ul></body></html>')

# 移动 CSV 文件到 Archive 文件夹
os.makedirs('Archive', exist_ok=True)
archive_path = os.path.join('Archive', os.path.basename(latest_csv))
os.rename(latest_csv, archive_path)

# 清理 upload 文件夹中剩余的 CSV 文件
for f in glob('upload/esa_ip_list_*.csv'):
    if os.path.exists(f):
        os.remove(f)
