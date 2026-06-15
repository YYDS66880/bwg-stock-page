import json
import requests
import re
from datetime import datetime

# 加载当前的数据源
with open('data.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

has_changed = False

print("开始监测搬瓦工 VPS 库存状态...")
for item in config['data']:
    url = item['link']
    # 如果链接是通往监测站本身的说明根本拿不到pid，直接跳过或者保留默认缺货状态
    if "aff.php" not in url:
        continue
        
    try:
        # 请求官方下单页面
        response = requests.get(url, headers=headers, timeout=15)
        html_content = response.text
        
        # 判断逻辑：官方缺货时，页面通常会包含 "Out of Stock"
        if "Out of Stock" in html_content or "is target unusable" in html_content:
            current_status = "缺货"
        else:
            current_status = "有货"
            
        if item['status'] != current_status:
            print(f"方案【{item['name']}】状态改变: {item['status']} -> {current_status}")
            item['status'] = current_status
            has_changed = True
            
    except Exception as e:
        print(f"检测方案【{item['name']}】失败: {e}")

# 无论有无变化，都更新检测时间
config['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 写入回文件
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=2)

print("库存检测结束。")
