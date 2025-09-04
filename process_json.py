# process_json.py
import os
import json
from datetime import datetime, timedelta, timezone

# 输入 JSON 文件路径
json_file = 'upload/data.json'
if not os.path.exists(json_file):
    raise Exception(f"JSON file not found: {json_file}")

# 读取 JSON 内容
with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 阿里云 API 返回的地址簿列表
# 假设 data 是一个字典，里面有 "Acls" 键
acls = data.get("Acls", [])
if not acls:
    raise Exception("No Acls data found in JSON file.")

# 获取当前时间（+8 时区）
tz = timezone(timedelta(hours=8))
now = datetime.now(tz)
timestamp = now.strftime('### %Y/%m/%d %H:%M')

# 创建输出目录
os.makedirs('docs', exist_ok=True)
os.makedirs('docs/address_books', exist_ok=True)

# 遍历所有地址簿，生成独立 txt 文件
for acl in acls:
    name = str(acl.get('Name', '')).strip().replace(' ', '_').replace('/', '_')
    ip_data = acl.get('AddressList', '')

    # AddressList 可能是字符串或列表
    if isinstance(ip_data, list):
        ip_list = ip_data
    elif isinstance(ip_data, str):
        ip_list = [ip.strip() for ip in ip_data.strip().split('\n') if ip.strip()]
    else:
        continue

    if not ip_list:
        continue

    file_path = os.path.join('docs/address_books', f'{name}.txt')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(timestamp + '\n')
        for ip in ip_list:
            f.write(ip.strip() + '\n')

# 单独处理 ESA 地址簿（保留原逻辑）
esa_acl = next((acl for acl in acls if 'ESA Back-to-origin Address' in acl.get('Name', '')), None)
if esa_acl:
    ip_data = esa_acl.get('AddressList', '')
    if isinstance(ip_data, list):
        ip_list = ip_data
    elif isinstance(ip_data, str):
        ip_list = [ip.strip() for ip in ip_data.strip().split('\n') if ip.strip()]
    else:
        ip_list = []

    with open('docs/esa_ip_list_latest.txt', 'w', encoding='utf-8') as f:
        f.write(timestamp + '\n')
        for ip in ip_list:
            f.write(ip.strip() + '\n')

# 生成 index.html 导航页面
index_path = 'docs/index.html'
with open(index_path, 'w', encoding='utf-8') as f:
    f.write('<html><head><meta charset="UTF-8"><title>地址簿导航</title></head><body>\n')
    f.write('<h1>📒 地址簿列表</h1><ul>\n')
    for file in sorted(os.listdir('docs/address_books')):
        if file.endswith('.txt'):
            name = file.replace('.txt', '')
            f.write(f'<li><a href="address_books/{file}">{name}</a></li>\n')
    f.write('</ul></body></html>')

# 归档 JSON 文件（按日期+序号命名）
os.makedirs('Archive', exist_ok=True)

# 获取当天日期字符串
date_str = now.strftime('%Y%m%d')  # 例如 20250904
base_name = f"data{date_str}"

# 找出当天已有的归档文件，确定序号
existing_files = [f for f in os.listdir('Archive') if f.startswith(base_name) and f.endswith('.json')]
if existing_files:
    # 提取已有文件的序号部分
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

# 生成新的归档文件名
new_filename = f"{base_name}-{next_num}.json"
archive_path = os.path.join('Archive', new_filename)

# 移动并重命名文件
os.rename(json_file, archive_path)
print(f"已归档到: {archive_path}")

