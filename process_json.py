# process_json.py
import os
import glob
import json
from datetime import datetime, timedelta, timezone

# 1. 找到 upload 目录下最新的 data*.json
json_files = glob.glob('upload/data*.json')
if not json_files:
    raise Exception("No JSON files found in upload folder.")

json_file = max(json_files, key=os.path.getmtime)
print(f"Processing latest JSON file: {json_file}")

# 2. 读取 JSON
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 3. 兼容两种结构
if isinstance(data, dict):
    acls = data.get("Acls", [])
elif isinstance(data, list):
    acls = data
else:
    raise Exception("Unexpected JSON structure")

print(f"Found {len(acls)} address book entries")

# 4. 获取当前时间（+8 时区）
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
timestamp = now.strftime('### %Y/%m/%d %H:%M')

# 5. 创建输出目录
os.makedirs('docs/address_books', exist_ok=True)

# 6. 遍历生成 txt 文件
for acl in acls:
    name = str(acl.get('GroupName', '')).strip().replace(' ', '_').replace('/', '_')
    ip_list = acl.get('AddressList', [])
    if not ip_list:
        continue
    file_path = os.path.join('docs/address_books', f'{name}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(timestamp + '\n')
        for ip in ip_list:
            f.write(ip.strip() + '\n')

# 7. 单独处理 ESA 地址簿
esa_acl = next((acl for acl in acls if 'ESA Back-to-origin Address' in acl.get('GroupName', '')), None)
if esa_acl:
    ip_list = esa_acl.get('AddressList', [])
    with open('docs/esa_ip_list_latest.txt', 'w', encoding='utf-8') as f:
        f.write(timestamp + '\n')
        for ip in ip_list:
            f.write(ip.strip() + '\n')

# 8. 生成 index.html
index_path = 'docs/index.html'
with open(index_path, 'w', encoding='utf-8') as f:
    f.write('<html><head><meta charset="UTF-8"><title>地址簿导航</title></head><body>\n')
    f.write('<h1>📒 地址簿列表</h1><ul>\n')
    for file in sorted(os.listdir('docs/address_books')):
        if file.endswith('.txt'):
            name = file.replace('.txt', '')
            f.write(f'<li><a href="address_books/{file}">{name}</a></li>\n')
    f.write('</ul></body></html>')

# 9. 归档 JSON 文件（dataYYYYMMDD-N.json）
os.makedirs('Archive', exist_ok=True)
date_str = now.strftime('%Y%m%d')
base_name = f"data{date_str}"
existing_files = [f for f in os.listdir('Archive') if f.startswith(base_name) and f.endswith('.json')]

if existing_files:
    nums = []
    for f in existing_files:
        try:
            num_part = f.replace(base_name, '').replace('.json', '').lstrip('-')
            nums.append(int(num_part))
        except ValueError:
            continue
    next_num = max(nums) + 1 if nums else 1
else:
    next_num = 1

new_filename = f"{base_name}-{next_num}.json"
archive_path = os.path.join('Archive', new_filename)
os.rename(json_file, archive_path)
print(f"已归档到: {archive_path}")
