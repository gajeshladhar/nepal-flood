"""Runs analysis.ipynb verbatim per tile. No reimplemented logic."""
import os, sys, json, time, re, signal, warnings, traceback
warnings.filterwarnings('ignore')
os.environ.update(GDAL_DISABLE_READDIR_ON_OPEN='EMPTY_DIR', GDAL_HTTP_MULTIPLEX='YES',
                  GDAL_HTTP_VERSION='2', VSI_CACHE='TRUE', VSI_CACHE_SIZE='100000000',
                  GDAL_HTTP_TIMEOUT='60', GDAL_HTTP_CONNECTTIMEOUT='20',
                  GDAL_HTTP_MAX_RETRY='3', GDAL_HTTP_RETRY_DELAY='2',
                  CPL_VSIL_CURL_CHUNK_SIZE='1048576')
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly

ROOT = '/Users/gajesh/research/nepalflood'
NB   = f'{ROOT}/notebooks/analysis.ipynb'
os.chdir(f'{ROOT}/notebooks')

cells = [c for c in json.load(open(NB))['cells'] if c['cell_type'] == 'code']
SRC   = [''.join(c['source']) for c in cells]

def run_tile(lat, lon, tag, G):
    for i, src in enumerate(SRC):
        if not src.strip(): continue
        if 'import' not in src and re.search(r'\.hvplot', src): continue   # display-only cells
        if src.lstrip().startswith('#lat') or 'lat, lon =' in src or 'lat,lon =' in src:
            src = f"lat, lon = {lat}, {lon}\nsize = 1024\nres = 0.6\nradius = size*res/2\n" \
                  f"flood_date = '2026-08-26'\n" \
                  f"event = 'https://vantor-opendata.s3.amazonaws.com/events/Nepal-Flooding-Aug-2026'"
        exec(compile(src, f'<cell{i}>', 'exec'), G)
    return G

def figure(G, tag, lat, lon):
    ds_pre, ds_comp = G['ds_pre'], G['ds_comp']
    wpre, wpost = G.get('ds_water_dino_pre'), G.get('ds_water_dino')
    bpre, bpost = G.get('df_pre'), G.get('df_post')
    S = ds_pre.shape[-1]
    ph, pw = G['patch']
    up = lambda a: np.kron(a.values.astype(bool), np.ones((ph, pw), bool))[:S, :S]
    pre_rgb  = np.transpose(ds_pre.values, (1, 2, 0))
    post_rgb = np.transpose(ds_comp.values, (1, 2, 0))
    fig, ax = plt.subplots(2, 3, figsize=(21, 14))
    ax[0,0].imshow(pre_rgb);  ax[0,0].set_title('PRE  Google basemap')
    ax[1,0].imshow(post_rgb); ax[1,0].set_title('POST Vantor composite')
    ax[0,1].imshow(pre_rgb)
    if wpre is not None:
        ax[0,1].imshow(np.ma.masked_where(~up(wpre), np.ones((S,S))), cmap='cool', alpha=.45)
        ax[0,1].set_title(f'PRE  water')
    ax[1,1].imshow(post_rgb)
    if wpost is not None:
        ax[1,1].imshow(np.ma.masked_where(~up(wpost), np.ones((S,S))), cmap='autumn', alpha=.45)
        ax[1,1].set_title(f'POST water')
    inv = ~ds_pre.rio.transform()
    cat20 = plt.get_cmap('tab20')
    def draw(a, df, title):
        n = 0 if df is None else len(df)
        a.set_title(f'{title} : {n} Buildings')
        if not n: return
        for k, (g, conf) in enumerate(zip(df.geometry, df.get('confidence', [0.5]*n))):
            if g.is_empty: continue
            xs, ys = g.exterior.xy
            pix = [inv*(x, y) for x, y in zip(xs, ys)]
            a.add_patch(MplPoly(pix, closed=True, facecolor=cat20(k % 20), alpha=0.5,
                                edgecolor='black', linewidth=2))
    ax[0,2].imshow(pre_rgb);  draw(ax[0,2], bpre,  'Pre Flood')
    ax[1,2].imshow(post_rgb); draw(ax[1,2], bpost, 'Post Flood')
    for a in ax.ravel(): a.axis('off')
    fig.suptitle(f'{tag}   {lat:.4f}, {lon:.4f}', fontsize=14)
    plt.tight_layout(); fig.savefig(f'{ROOT}/outputs/maps/{tag}.png', dpi=70, bbox_inches='tight')
    plt.close(fig)

def collect(G, tag, lat, lon):
    r = {'tile': tag, 'lat': lat, 'lon': lon}
    for k, key in [('n_scenes','df_items'), ('bldg_pre','df_pre'), ('bldg_post','df_post')]:
        if key in G: r[k] = len(G[key])
    for k in ('km_tot','km_imp','n_br','n_br_imp','n_hydro','n_power','n_health','n_shelter','n_air','n_settl'):
        if k in G: r[k] = float(G[k]) if isinstance(G[k], float) else int(G[k])
    if 'ds_water_dino' in G and 'sim' in G:
        px = abs(float(G['sim'].x[1]-G['sim'].x[0])) * abs(float(G['sim'].y[1]-G['sim'].y[0]))
        r['water_pre_km2']  = round(float(G['ds_water_dino_pre'].sum())*px/1e6, 4)
        r['water_post_km2'] = round(float(G['ds_water_dino'].sum())*px/1e6, 4)
        r['expansion']      = round(float(G['ds_water_dino'].sum())/max(float(G['ds_water_dino_pre'].sum()),1), 2)
    if 'df_pre' in G and 'df_post' in G: r['bldg_lost'] = len(G['df_pre']) - len(G['df_post'])
    return r

def save(G, tag):
    for var, name in [('ds_water_dino_pre','water_pre'), ('ds_water_dino','water_post')]:
        if var in G: G[var].rio.to_raster(f'{ROOT}/outputs/extent/{tag}_{name}.tif')
    for var, name in [('df_pre','pre'), ('df_post','post')]:
        if var in G and len(G[var]): G[var].to_file(f'{ROOT}/outputs/buildings/{tag}_{name}.gpkg', driver='GPKG')
    for var, sub in [('df_road','roads'), ('df_infra','roads')]:
        if var in G and len(G[var]): G[var].to_file(f'{ROOT}/outputs/{sub}/{tag}_{var[3:]}.gpkg', driver='GPKG')

if __name__ == '__main__':
    tiles = json.load(open(f'{ROOT}/src/tiles.json'))
    rp = f'{ROOT}/reports/results.json'
    done = json.load(open(rp)) if os.path.exists(rp) else []
    seen = {r['tile'] for r in done}
    G = {'__name__': '__main__'}
    for i, (lat, lon) in enumerate(tiles):
        tag = f't{i:03d}'
        if tag in seen: continue
        t0 = time.time()
        def _to(sig, frm): raise TimeoutError('tile exceeded 420s')
        signal.signal(signal.SIGALRM, _to); signal.alarm(420)
        try:
            run_tile(lat, lon, tag, G)
            res = collect(G, tag, lat, lon); res['status'] = 'ok'
            figure(G, tag, lat, lon); save(G, tag)
        except Exception as e:
            res = {'tile': tag, 'lat': lat, 'lon': lon, 'status': f'ERROR {type(e).__name__}: {str(e)[:120]}'}
            traceback.print_exc()
        signal.alarm(0)
        res['secs'] = round(time.time()-t0, 1)
        done.append(res); json.dump(done, open(rp, 'w'), indent=1)
        try:
            os.system(f'{sys.executable} {ROOT}/src/report.py >/dev/null 2>&1')
        except Exception: pass
        print(f"[{tag}] {res.get('status')} {res.get('secs')}s "
              f"water {res.get('water_pre_km2')}->{res.get('water_post_km2')} ({res.get('expansion')}x) "
              f"bldg {res.get('bldg_pre')}->{res.get('bldg_post')} road {res.get('km_imp')}", flush=True)
    print('BATCH COMPLETE', flush=True)
