import matplotlib.pyplot as plt
import numpy as np
import json
import os

PRODUCER_GROUPS = {
    "沙特": "中东", "伊拉克": "中东", "阿联酋": "中东", "科威特": "中东",
    "阿曼": "中东", "卡塔尔": "中东", "巴林": "中东", "也门": "中东",
    "俄罗斯": "俄罗斯",
    "尼日利亚": "西非", "安哥拉": "西非", "加蓬": "西非", "刚果（布）": "西非",
    "赤道几内亚": "西非", "喀麦隆": "西非", "加纳": "西非", "塞内加尔": "西非",
    "科特迪瓦": "西非", "多哥": "西非", "刚果（金）": "西非", "苏丹": "西非",
    "美国": "美洲", "加拿大": "美洲", "巴西": "美洲", "墨西哥": "美洲",
    "委内瑞拉": "美洲", "哥伦比亚": "美洲", "厄瓜多尔": "美洲", "圭亚那": "美洲",
    "乌拉圭": "美洲", "巴拿马": "美洲",
    "阿尔及利亚": "其他产油国", "利比亚": "其他产油国", "埃及": "其他产油国", "突尼斯": "其他产油国",
    "挪威": "其他产油国", "英国": "其他产油国", "丹麦": "其他产油国",
    "马来西亚": "东南亚产油", "印尼": "东南亚产油", "文莱": "东南亚产油",
    "越南": "东南亚产油", "泰国": "东南亚产油", "巴布亚新几内亚": "东南亚产油",
    "澳大利亚": "东南亚产油",
    "Y国": "其他产油国", "以色列": "其他产油国", "直布罗陀": "其他产油国",
    "马耳他": "其他产油国", "毛里求斯": "其他产油国", "美属维尔京群岛": "其他产油国",
    "阿鲁巴": "其他产油国", "库拉索": "其他产油国", "圣尤斯特歇斯": "其他产油国",
    "阿尔巴尼亚": "其他产油国", "瑞典": "其他产油国", "比利时": "其他产油国", "希腊": "其他产油国",
}

CONSUMER_GROUPS = {
    "中国": "中国", "香港（中国）": "中国", "台湾（中国）": "中国",
    "印度": "印度", "日本": "日本", "韩国": "韩国",
    "法国": "欧洲", "意大利": "欧洲", "西班牙": "欧洲", "荷兰": "欧洲",
    "比利时": "欧洲", "希腊": "欧洲", "波兰": "欧洲", "罗马尼亚": "欧洲",
    "保加利亚": "欧洲", "克罗地亚": "欧洲", "芬兰": "欧洲", "爱沙尼亚": "欧洲",
    "葡萄牙": "欧洲", "瑞典": "欧洲", "阿尔巴尼亚": "欧洲", "土耳其": "欧洲", "阿塞拜疆": "欧洲",
    "新加坡": "其他", "泰国": "其他", "其他": "其他", "印尼": "其他",
    "马来西亚": "其他", "缅甸": "其他", "越南": "其他", "文莱": "其他",
    "古巴": "其他", "巴哈马": "其他",
    "摩洛哥": "其他", "斯里兰卡": "其他", "毛里求斯": "其他",
    "圣尤斯特歇斯": "其他", "美属维尔京群岛": "其他",
}


def aggregate_by_year(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    yearly_data = {"2022": {}, "2023": {}, "2024": {}}

    for month, producers in data.items():
        year = month.split("-")[0]
        if year not in yearly_data:
            continue

        for loading_country, discharging_dict in producers.items():
            prod_region = PRODUCER_GROUPS.get(loading_country, "其他产油国")

            for discharging_country, volume in discharging_dict.items():
                cons_region = CONSUMER_GROUPS.get(discharging_country, "其他")

                yd = yearly_data[year]
                if prod_region not in yd:
                    yd[prod_region] = {}
                yd[prod_region][cons_region] = yd[prod_region].get(cons_region, 0) + volume

    return yearly_data


def plot_yearly_flow(aggregated, year, output_dir="plots"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_exports = {pr: sum(consumers.values()) for pr, consumers in aggregated.items()}
    producer_regions = sorted(aggregated.keys(), key=lambda x: total_exports[x], reverse=True)

    all_consumers = set()
    for consumers in aggregated.values():
        all_consumers.update(consumers.keys())
    consumer_regions = sorted(all_consumers)

    data_matrix = {}
    for cons in consumer_regions:
        data_matrix[cons] = [aggregated.get(prod, {}).get(cons, 0) / 1e6 for prod in producer_regions]

    fig, ax = plt.subplots(figsize=(12, 8))
    bottom = np.zeros(len(producer_regions))

    custom_6_colors = ["#EFB1C7", "#FCD97D", "#E5E1BB", "#84C9EF", "#5D7AB5", "#A2D188"]
    colors = [custom_6_colors[i % 6] for i in range(len(consumer_regions))]

    for i, cons in enumerate(consumer_regions):
        values = data_matrix[cons]
        ax.bar(producer_regions, values, bottom=bottom, label=cons, color=colors[i % len(colors)])
        bottom += values

    ax.text(x=-0.045, y=0.98, s="MT", transform=ax.transAxes, fontsize=12, color='black', weight='bold')
    ax.set_title(f"{year} 年全球原油流向（按产油与消费经济体分组）", fontsize=18)
    ax.legend(title="消费经济体", bbox_to_anchor=(1, 1), fontsize=16, title_fontsize=16)
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)

    output_path = os.path.join(output_dir, f"crude_flow_{year}.png")
    plt.savefig(output_path, dpi=300)
    plt.close(fig)  # 释放内存
    print(f"✅ 已保存 {year} 年图表: {output_path}")


def plot_combined_flow(yearly_aggregated, output_dir="plots"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_producers = set()
    for yd in yearly_aggregated.values():
        all_producers.update(yd.keys())

    total_by_prod = {}
    for year, yd in yearly_aggregated.items():
        for prod, cons_dict in yd.items():
            total_by_prod[prod] = total_by_prod.get(prod, 0) + sum(cons_dict.values())
    producer_regions = sorted(total_by_prod.keys(), key=lambda x: total_by_prod[x], reverse=True)

    all_consumers = set()
    for yd in yearly_aggregated.values():
        for cons_dict in yd.values():
            all_consumers.update(cons_dict.keys())
    consumer_regions = sorted(all_consumers)

    years = ["2022", "2023", "2024"]
    n_years = len(years)
    n_producers = len(producer_regions)

    bar_width = 0.24
    intra_spacing = 0.06
    group_center = np.arange(n_producers)

    offsets = []
    for i in range(n_years):
        offset = group_center + (i - (n_years - 1) / 2) * (bar_width + intra_spacing)
        offsets.append(offset)

    custom_6_colors = ["#EFB1C7", "#FCD97D", "#E5E1BB", "#84C9EF", "#5D7AB5", "#A2D188"]
    colors = [custom_6_colors[i % 6] for i in range(len(consumer_regions))]

    fig, ax = plt.subplots(figsize=(12, 8))

    for y_idx, year in enumerate(years):
        bottom = np.zeros(n_producers)
        year_data = yearly_aggregated[year]

        for i, cons in enumerate(consumer_regions):
            values = []
            for prod in producer_regions:
                vol = year_data.get(prod, {}).get(cons, 0) / 1e6
                values.append(vol)
            values = np.array(values)

            ax.bar(
                offsets[y_idx], values, bottom=bottom, width=bar_width,
                label=cons if y_idx == 0 else "", color=colors[i % len(colors)]
            )
            bottom += values

    ax.set_xticks(group_center)
    ax.set_xticklabels(producer_regions)

    ax.text(x=-0.045, y=0.98, s="MT", transform=ax.transAxes, fontsize=12, color='black', weight='bold')
    ax.set_title("2022–2024 全球原油流向（按产油与消费经济体分组）", fontsize=18)
    ax.legend(title="消费经济体", bbox_to_anchor=(1, 1), fontsize=16, title_fontsize=16)
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)

    output_path = os.path.join(output_dir, "crude_flow_combined.png")
    plt.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"✅ 已保存三年合并图表: {output_path}")


if __name__ == "__main__":
    json_file = "crude_oil_flow.json"
    print("正在按年聚合数据...")
    yearly_aggregated = aggregate_by_year(json_file)

    print("正在绘制年度图表...")
    plt.rcParams['font.sans-serif'] = ['Lolita']

    for year in ["2022", "2023", "2024"]:
        plot_yearly_flow(yearly_aggregated[year], year)

    plot_combined_flow(yearly_aggregated)

    print("\n🎉 所有图表已生成！")
