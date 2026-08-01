import json
import os


CHINESE_TO_ENGLISH = {
    "沙特": "Saudi Arabia",
    "俄罗斯": "Russia",
    "阿联酋": "UAE",
    "伊拉克": "Iraq",
    "阿曼": "Oman",
    "新加坡": "Singapore",
    "巴西": "Brazil",
    "科威特": "Kuwait",
    "安哥拉": "Angola",
    "马来西亚": "Malaysia",
    "美国": "USA",
    "卡塔尔": "Qatar",
    "巴拿马": "Panama",
    "刚果（布）": "Congo (Brazzaville)",
    "加蓬": "Gabon",
    "埃及": "Egypt",
    "委内瑞拉": "Venezuela",
    "Y国": "Country Y",
    "哥伦比亚": "Colombia",
    "挪威": "Norway",
    "墨西哥": "Mexico",
    "利比亚": "Libya",
    "英国": "UK",
    "喀麦隆": "Cameroon",
    "加纳": "Ghana",
    "澳大利亚": "Australia",
    "乌拉圭": "Uruguay",
    "尼日利亚": "Nigeria",
    "加拿大": "Canada",
    "赤道几内亚": "Equatorial Guinea",
    "多哥": "Togo",
    "阿尔及利亚": "Algeria",
    "马耳他": "Malta",
    "塞内加尔": "Senegal",
    "苏丹": "Sudan",
    "巴布亚新几内亚": "Papua New Guinea",
    "丹麦": "Denmark",
    "以色列": "Israel",
    "特立尼达和多巴哥": "Trinidad and Tobago",
    "直布罗陀": "Gibraltar",
    "毛里求斯": "Mauritius",
    "也门": "Yemen",
    "南非": "South Africa",
    "巴林": "Bahrain",
    "刚果（金）": "Congo (Kinshasa)",
    "厄瓜多尔": "Ecuador",
    "越南": "Vietnam",
    "突尼斯": "Tunisia",
    "圭亚那": "Guyana",
    "科特迪瓦": "Côte d'Ivoire",
    "印尼": "Indonesia",
    "美属维尔京群岛": "US Virgin Islands",
    "阿鲁巴": "Aruba",
    "库拉索": "Curaçao",
    "泰国": "Thailand",
    "阿尔巴尼亚": "Albania",
    "比利时": "Belgium",
    "瑞典": "Sweden",
    "文莱": "Brunei",
    "葡萄牙": "Portugal",
    "圣尤斯特歇斯": "Sint Eustatius",
    "芬兰": "Finland",
    "摩洛哥": "Morocco",
    "巴哈马": "Bahamas",
    "爱沙尼亚": "Estonia",
    "阿塞拜疆": "Azerbaijan",
    "香港（中国）": "Hong Kong",
    "古巴": "Cuba",
    "菲律宾": "Philippines",
    "斯里兰卡": "Sri Lanka",
    "缅甸": "Myanmar",
    "希腊": "Greece",
    "波兰": "Poland",
    "克罗地亚": "Croatia",
    "西班牙": "Spain",
    "法国": "France",
    "罗马尼亚": "Romania",
    "保加利亚": "Bulgaria",
    "台湾（中国）": "Taiwan",
    "荷兰": "Netherlands",
    "土耳其": "Turkey",
    "意大利": "Italy",
    "印度": "India",
    "韩国": "South Korea",
    "日本": "Japan",
    "中国": "China",
    "其他产油国": "Other",
    "其他消费国": "Other",
}


def translate_name(name):
    return CHINESE_TO_ENGLISH.get(name, name)


def generate_combined_sankey_top30(json_path, output_dir="./"):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    all_flows = []
    total_export = {}
    total_import = {}

    for month, producers in data.items():
        year = month.split("-")[0]
        if year not in ("2022", "2023", "2024"):
            continue
        for loading_country, discharging_dict in producers.items():
            for discharging_country, volume in discharging_dict.items():
                if volume <= 0:
                    continue
                all_flows.append((loading_country, discharging_country, volume))
                total_export[loading_country] = total_export.get(loading_country, 0) + volume
                total_import[discharging_country] = total_import.get(discharging_country, 0) + volume

    top_exporters = set(
        sorted(total_export.items(), key=lambda x: x[1], reverse=True)[:29]
    )
    top_exporters = {name for name, _ in top_exporters}

    top_importers = set(
        sorted(total_import.items(), key=lambda x: x[1], reverse=True)[:29]
    )
    top_importers = {name for name, _ in top_importers}

    OTHER_PRODUCER = "其他产油国"
    OTHER_CONSUMER = "其他消费国"

    # 3. 重新映射流向
    new_flows = {}
    for src, tgt, val in all_flows:
        new_src = src if src in top_exporters else OTHER_PRODUCER
        new_tgt = tgt if tgt in top_importers else OTHER_CONSUMER

        key = (new_src, new_tgt)
        new_flows[key] = new_flows.get(key, 0) + val

    # 4. 生成文本
    header = """---
config:
  sankey:
    showValues: false
---
sankey
"""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "crude_sankey_2022_2024_top30.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "\n")
        for (src, tgt), val in sorted(new_flows.items()):
            en_src = translate_name(src)
            en_tgt = translate_name(tgt)
            f.write(f".{en_src},{en_tgt}.,{(val / 1e6):.2f}\n")

    print(f"✅ 已生成聚合桑基图（Top 30 + 其他）: {output_path}")
    print(f"   - 装货国数量: {len(top_exporters)} + 1（其他）")
    print(f"   - 卸货国数量: {len(top_importers)} + 1（其他）")
    print(f"   - 总连接数: {len(new_flows)}")


if __name__ == "__main__":
    json_file = "crude_oil_flow.json"
    print("正在生成 Top 30 聚合桑基图...")
    generate_combined_sankey_top30(json_file)
    print("\n🎉 完成！")
