"""四艘候选船轨迹图 — 复赛热力图风格"""
import pandas as pd, numpy as np, math
from pathlib import Path
import cartopy.crs as crs
import matplotlib.pyplot as plt
import cartopy.feature as feature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import warnings; warnings.filterwarnings('ignore')

ROOT=Path(r'D:\Desktop\Desktop\海事')
CSV_DIR=ROOT/'output_final'/'case_study'
OUT_DIR=ROOT/'output_final'/'charts'
OUT_DIR.mkdir(parents=True,exist_ok=True)

plt.rcParams['font.sans-serif']=['Microsoft YaHei']
plt.rcParams['axes.unicode_minus']=False
DPI=150

ships={
    'Ligovsky_Prospect.csv':'Ligovsky Prospect\nIMO 9256066 | Russia | Sovcomflot',
    'Kousai.csv':'Kousai\nIMO 9285835 | Sierra Leone',
    'Aqua_Titan.csv':'Aqua Titan\nIMO 9332781 | Cameroon',
    'Nasledie.csv':'Nasledie\nIMO 9293002 | Russia',
}

def draw_ship_trajectory(ax,df,title):
    lon,lat=df['longitude'].values,df['latitude'].values
    times=pd.to_datetime(df['acqtime'])
    t_val=times.values.astype('int64')
    t_norm=(t_val-t_val.min())/(t_val.max()-t_val.min()+1e-9)
    
    pad=2
    ax.set_extent([lon.min()-pad,lon.max()+pad,lat.min()-pad,lat.max()+pad],crs=crs.PlateCarree())
    
    ax.add_feature(feature.LAND.with_scale('10m'),facecolor='#EAE7D6')
    ax.add_feature(feature.COASTLINE.with_scale('10m'),linewidth=0.5)
    ax.add_feature(feature.BORDERS.with_scale('10m'),linestyle=':',linewidth=0.3)
    
    # 分段画线，颜色随时间变化
    n=len(lon)
    chunk=max(1,n//500)
    for i in range(0,n-chunk,chunk):
        j=i+chunk
        c=plt.cm.YlOrRd(0.15+0.7*t_norm[i:i+1].mean())
        ax.plot(lon[i:j+1],lat[i:j+1],color=c,linewidth=0.5,alpha=0.8,transform=crs.PlateCarree())
    
    # 起终点标注
    ax.scatter(lon[0],lat[0],c='green',s=40,zorder=5,edgecolors='white',linewidth=0.5,transform=crs.PlateCarree())
    ax.scatter(lon[-1],lat[-1],c='red',s=40,zorder=5,edgecolors='white',linewidth=0.5,transform=crs.PlateCarree())
    
    # 刻度
    xstep=(lon.max()-lon.min())/4
    ystep=(lat.max()-lat.min())/4
    xticks=np.round(np.arange(np.round(lon.min(),1),np.round(lon.max(),1)+xstep/2,xstep),1)
    yticks=np.round(np.arange(np.round(lat.min(),1),np.round(lat.max(),1)+ystep/2,ystep),1)
    ax.set_xticks(xticks,crs=crs.PlateCarree())
    ax.set_yticks(yticks,crs=crs.PlateCarree())
    ax.xaxis.set_major_formatter(LongitudeFormatter(number_format='.1f'))
    ax.yaxis.set_major_formatter(LatitudeFormatter(number_format='.1f'))
    ax.tick_params(labelsize=7)
    
    ax.set_title(title,fontsize=9,fontweight='bold',pad=5)

fig=plt.figure(figsize=(17,13),dpi=DPI)

for idx,(fn,title) in enumerate(ships.items()):
    df=pd.read_csv(CSV_DIR/fn)
    ax=fig.add_subplot(2,2,idx+1,projection=crs.PlateCarree())
    draw_ship_trajectory(ax,df,title)

plt.suptitle('Case Study Candidates — Full AIS Trajectories (Jan–Jun 2026)',fontsize=14,fontweight='bold',y=1.01)
plt.tight_layout()
plt.savefig(OUT_DIR/'case_trajectories.png',dpi=DPI,bbox_inches='tight')
plt.close()
print('Done: case_trajectories.png')
