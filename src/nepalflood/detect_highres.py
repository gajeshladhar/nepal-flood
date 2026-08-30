import warnings,json,time,os,signal; warnings.filterwarnings('ignore')
import numpy as np, geopandas as gpd
from mapminer import miners
from ultralytics import YOLO
from shapely.geometry import Polygon, box
ROOT='/Users/gajesh/research/nepalflood'
S,R=2048,0.3
model=YOLO(f'{ROOT}/weights/building-miner-stable.pt'); model.eval()
def get_buildings(ds, conf=0.10, iou=0.70):
    ds=ds.transpose('y','x','band').sortby('x').sortby('y')
    imgsz=int(np.ceil(max(ds.shape[:2])/32)*32)
    r=model.predict(ds.data,conf=conf,iou=iou,device='mps',verbose=False,imgsz=imgsz,max_det=int(1e8))[0].cpu()
    rows=[]
    for obb in r.obb:
        c=obb.xyxyxyxy[0].cpu().numpy().astype('int32')
        c=np.stack([ds.x.isel(x=np.clip(c[:,0],0,len(ds.x)-1)),ds.y.isel(y=np.clip(c[:,1],0,len(ds.y)-1))],axis=1)
        rows.append({'confidence':float(obb.conf[0]),'geometry':Polygon(c)})
    if not rows: return gpd.GeoDataFrame(columns=['confidence','geometry'],geometry='geometry',crs=ds.rio.crs)
    df=gpd.GeoDataFrame(rows,crs=ds.rio.crs); df['geometry']=df.buffer(0); df['area']=df.geometry.area
    df=df.sort_values('area').reset_index(drop=True)
    for i in df.index[:-1]:
        if i not in df.index: continue
        f=df.loc[(i+1):].intersection(df.loc[i,'geometry']).area.max()/max(df.loc[i,'geometry'].area,1e-9)
        if f>0.75: df=df.drop(i)
    return df.reset_index(drop=True)

top=json.load(open('/tmp/top20.json'))
res=json.load(open(f'{ROOT}/reports/results.json'))
idx={x['tile']:x for x in res}
top=[x for x in top if idx.get(x[0],{}).get('res_m')!=R]
print(f'{len(top)} tiles to do',flush=True)
for k,(tag,la,lo) in enumerate(top):
    t=time.time()
    def _to(sig,frm): raise TimeoutError('tile exceeded 300s')
    signal.signal(signal.SIGALRM,_to); signal.alarm(300)
    try:
        g=miners.GoogleBaseMapMiner().fetch(lat=la,lon=lo,radius=S*R/2,resolution=R)
        g=g.isel(band=range(3)).isel(y=slice(0,S),x=slice(0,S)).compute()
        df=get_buildings(g)
        df=df[df.intersects(box(*g.rio.bounds()))].reset_index(drop=True)
        old=idx[tag].get('bldg_pre')
        if len(df): df.to_file(f'{ROOT}/outputs/buildings/{tag}_pre.gpkg',driver='GPKG')
        idx[tag]['bldg_pre']=len(df)
        idx[tag]['res_m']=R
        idx[tag].pop('bldg_post',None); idx[tag].pop('bldg_lost',None)
        json.dump(res,open(f'{ROOT}/reports/results.json','w'),indent=1)
        signal.alarm(0)
        print(f'[{k+1}/{len(top)}] {tag} {old} -> {len(df)}  ({time.time()-t:.0f}s)',flush=True)
    except BaseException as e:
        signal.alarm(0)
        print(f'[{k+1}/{len(top)}] {tag} ERROR {type(e).__name__}: {str(e)[:70]}',flush=True)
print('DONE')
