from preprocess import corridor_filter
from indicators import density_2h, conflict_2h, speed_2h, teu_2h
from weight import entropy_weight_2h, risk_score_2h, plot_2h_risk
from config import log, safe_exit, OUT_PUT

# ---------- 数据解算 ----------

gdf = corridor_filter()
log("原始数据解算完成")

# ---------- 指标计算 ----------

density = density_2h(gdf)
log("船舶密度计算完成")

conflict = conflict_2h(gdf)
log("航迹冲突计算完成")

speed = speed_2h(gdf)
log("平均航速计算完成")

teu = teu_2h(gdf)
log("运力分布计算完成")

ind = (
    density.merge(conflict, on='interval').merge(speed, on='interval').merge(teu, on='interval')
)

# ---------- 熵权评分 ----------

w = entropy_weight_2h(ind)
log("熵权法完成")

risk = risk_score_2h(ind, w)
log("评分完成")

# ---------- 保存结果 ----------

risk.to_csv(OUT_PUT / "risk.csv", index=False)
log(f"结果已保存至 {OUT_PUT}/risk.csv")

plot_2h_risk(risk, OUT_PUT / 'risk_plot.png')
log(f"绘制图表已保存至 {OUT_PUT}/risk_plot.png")

safe_exit(0)
