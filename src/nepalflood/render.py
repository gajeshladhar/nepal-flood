import warnings,json,os,time,signal; warnings.filterwarnings('ignore')
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR',GDAL_HTTP_MULTIPLEX='YES',
                  GDAL_HTTP_VERSION='2',VSI_CACHE='TRUE',GDAL_HTTP_TIMEOUT='60')
import numpy as np, pandas as pd, geopandas as gpd, xarray as xr, rioxarray, pystac
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly
from mapminer import miners
from shapely.geometry import box
from rasterio.enums import Resampling
from concurrent.futures import ThreadPoolExecutor
ROOT='/Users/gajesh/research/nepalflood'
EVENT='https://vantor-opendata.s3.amazonaws.com/events/Nepal-Flooding-Aug-2026'
S,R=1024,0.6
cat=pystac.Collection.from_file(f'{EVENT}/collection.json')
items=pd.DataFrame([dict(id=i.id,dt=str(i.datetime.date()),href=i.assets['visual'].href,bbox=i.bbox) for i in cat.get_items()])
cat20=plt.get_cmap('tab20')
res=json.load(open(f'{ROOT}/reports/results.json'))
todo=[x for x in res if x.get('res_m')==0.3]
print(f'{len(todo)} tiles to re-render',flush=True)
for k,x in enumerate(todo):
    tag,la,lo=x['tile'],x['lat'],x['lon']
    t0=time.time()
    def _to(s,f): raise TimeoutError('timeout')
    signal.signal(signal.SIGALRM,_to); signal.alarm(300)
    try:
        g=miners.GoogleBaseMapMiner().fetch(lat=la,lon=lo,radius=S*R/2,resolution=R)
        g=g.isel(band=range(3)).isel(y=slice(0,S),x=slice(0,S)).compute()
        b=g.rio.transform_bounds('EPSG:4326')
        sel=items[(items.dt>='2026-08-26')&items.bbox.apply(lambda z: z[0]<=lo<=z[2] and z[1]<=la<=z[3])]
        def fw(h):
            d=rioxarray.open_rasterio(f'/vsicurl/{h}',lock=False)
            return d.rio.clip_box(*b,crs='EPSG:4326').isel(band=range(3)).rio.reproject_match(g,resampling=Resampling.bilinear)
        with ThreadPoolExecutor(8) as ex: das=list(ex.map(fw,sel.href))
        st=xr.concat(das,dim='scene').compute()
        V=st.max(dim='band').astype('float32')
        Sa=((st.max(dim='band')-st.min(dim='band'))/st.max(dim='band').where(lambda z:z>0)).astype('float32')
        cl=((V>170)&(Sa<0.15))|(st.sum(dim='band')==0); vd=(~cl).sum(dim='scene')
        comp=st.where(~cl).median(dim='scene').round().fillna(0).astype('uint8').where(vd>0,0)
        comp['x'],comp['y']=g['x'],g['y']
        pre=gpd.read_file(f'{ROOT}/outputs/buildings/{tag}_pre.gpkg').to_crs(g.rio.crs)
        pf=f'{ROOT}/outputs/buildings/{tag}_post.gpkg'
        post=gpd.read_file(pf).to_crs(g.rio.crs) if os.path.exists(pf) else gpd.GeoDataFrame(geometry=[],crs=g.rio.crs)
        inv=~g.rio.transform()
        def draw(a,df):
            for i,gm in enumerate(df.geometry):
                if gm.is_empty: continue
                xs,ys=gm.exterior.xy
                a.add_patch(MplPoly([inv*(px,py) for px,py in zip(xs,ys)],closed=True,
                            facecolor=cat20(i%20),alpha=0.5,edgecolor='black',linewidth=2))
        pre_rgb=np.transpose(g.values,(1,2,0)); post_rgb=np.transpose(comp.values,(1,2,0))
        fig,ax=plt.subplots(1,2,figsize=(17,8.6))
        ax[0].imshow(pre_rgb);  draw(ax[0],pre);  ax[0].set_title(f'Pre Flood : {len(pre)} Buildings',fontsize=13)
        ax[1].imshow(post_rgb); draw(ax[1],post); ax[1].set_title(f'Post Flood : {len(post)} Buildings',fontsize=13)
        for a in ax: a.axis('off')
        fig.suptitle(f'{tag}   {la:.4f}, {lo:.4f}',fontsize=14)
        plt.tight_layout(); fig.savefig(f'{ROOT}/outputs/maps/{tag}.png',dpi=72,bbox_inches='tight'); plt.close(fig)
        signal.alarm(0)
        print(f'[{k+1}/{len(todo)}] {tag} pre {len(pre)} post {len(post)}  ({time.time()-t0:.0f}s)',flush=True)
    except BaseException as e:
        signal.alarm(0)
        print(f'[{k+1}/{len(todo)}] {tag} ERROR {type(e).__name__}: {str(e)[:60]}',flush=True)
print('DONE',flush=True)
