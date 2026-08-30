"""Builds an HTML damage-assessment report from completed tiles."""
import json, os, base64, datetime

ROOT = '/Users/gajesh/research/nepalflood'
NTILES = len(json.load(open(f'{ROOT}/src/tiles.json')))
res  = [r for r in json.load(open(f'{ROOT}/reports/results.json')) if r.get('status') == 'ok']
res.sort(key=lambda r: -r.get('bldg_lost', 0))

from PIL import Image
import io
def b64(p, w=1400):
    if not os.path.exists(p): return None
    im = Image.open(p).convert('RGB')
    if im.width > w: im = im.resize((w, int(im.height*w/im.width)), Image.LANCZOS)
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=72, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()

T = dict(
    tiles=len(res),
    bldg_pre=sum(r.get('bldg_pre',0) for r in res),
    bldg_post=sum(r.get('bldg_post',0) for r in res),
    bldg_lost=sum(r.get('bldg_lost',0) for r in res),
    w_pre=sum(r.get('water_pre_km2',0) for r in res),
    w_post=sum(r.get('water_post_km2',0) for r in res),
    km_tot=sum(r.get('km_tot',0) for r in res),
    km_imp=sum(r.get('km_imp',0) for r in res),
    br=sum(r.get('n_br',0) for r in res),
    br_imp=sum(r.get('n_br_imp',0) for r in res),
    settl=sum(r.get('n_settl',0) for r in res),
)
T['pct'] = round(T['bldg_lost']/max(T['bldg_pre'],1)*100)
T['area_km2'] = round(T['tiles']*(1024*0.6/1000)**2, 2)

rows = '\n'.join(
    f"<tr><td class=m>{r['tile']}</td><td class=m>{r['lat']:.4f}, {r['lon']:.4f}</td>"
    f"<td>{r.get('n_scenes','-')}</td><td>{r.get('bldg_pre',0)}</td><td>{r.get('bldg_post',0)}</td>"
    f"<td class='{'bad' if r.get('bldg_lost',0)>0 else ''}'>{r.get('bldg_lost',0)}</td>"
    f"<td>{r.get('water_pre_km2',0):.4f}</td><td>{r.get('water_post_km2',0):.4f}</td>"
    f"<td>{r.get('km_imp',0):.2f}</td><td>{r.get('n_br_imp',0)}/{r.get('n_br',0)}</td></tr>"
    for r in res)

MAXIMG = 24
shown = [r for r in res if r.get('bldg_lost',0) > 0][:MAXIMG]
if len(shown) < MAXIMG:
    shown += [r for r in sorted(res, key=lambda z: -z.get('expansion',0)) if r not in shown][:MAXIMG-len(shown)]
cards = ''
for r in shown:
    img = b64(f"{ROOT}/outputs/maps/{r['tile']}.png")
    if not img: continue
    lost = r.get('bldg_lost',0)
    cards += f"""
    <section class="tile">
      <div class="th">
        <div><h3>{r['tile']}</h3><span class="coord">{r['lat']:.4f}, {r['lon']:.4f}</span></div>
        <div class="chips">
          <span class="chip"><b>{r.get('bldg_pre',0)}</b> before</span>
          <span class="chip"><b>{r.get('bldg_post',0)}</b> after</span>
          <span class="chip {'danger' if lost>0 else ''}"><b>{lost}</b> lost</span>
          <span class="chip"><b>{r.get('water_post_km2',0):.3f}</b> km² water</span>
          <span class="chip"><b>{r.get('n_scenes','-')}</b> scenes</span>
        </div>
      </div>
      <img src="data:image/jpeg;base64,{img}" alt="{r['tile']}">
    </section>"""

html = f"""<title>Rasuwa Flood Damage Assessment</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#f7f5f1; --ink:#12100e; --mut:#6f6559; --line:#ddd7cd; --card:#fffdfa;
  --silt:#8b2318; --glacial:#3d6b7d; --warm:#a89a86;
  --disp:"Instrument Serif",Georgia,serif;
  --body:"IBM Plex Sans",-apple-system,BlinkMacSystemFont,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,monospace;
}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{
  --paper:#14120f; --ink:#ece7df; --mut:#9c9285; --line:#2e2a24; --card:#1b1815;
  --silt:#d9584a; --glacial:#7fb3c8; --warm:#6f6559;
}}}}
:root[data-theme=dark]{{
  --paper:#14120f; --ink:#ece7df; --mut:#9c9285; --line:#2e2a24; --card:#1b1815;
  --silt:#d9584a; --glacial:#7fb3c8; --warm:#6f6559;
}}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);font:16px/1.65 var(--body);margin:0;padding:0 24px 96px}}
.wrap{{max-width:1140px;margin:0 auto}}
header{{padding:72px 0 28px}}
.eyebrow{{font:500 11.5px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--silt);margin-bottom:20px}}
h1{{font:400 clamp(38px,6vw,62px)/1.04 var(--disp);margin:0 0 14px;letter-spacing:-.015em;text-wrap:balance;max-width:16ch}}
.sub{{color:var(--mut);font-size:16px;margin:0;max-width:62ch}}
.rule{{height:1px;background:var(--line);margin:36px 0 0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(152px,1fr));gap:0;margin:0 0 8px;border-bottom:1px solid var(--line)}}
.stat{{padding:26px 22px 24px;border-right:1px solid var(--line)}}
.stat:last-child{{border-right:none}}
.stat .v{{font:400 40px/1 var(--disp);letter-spacing:-.02em;font-variant-numeric:tabular-nums}}
.stat .l{{font:500 10.5px/1.4 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mut);margin-top:9px}}
.stat.hero .v{{color:var(--silt)}}
.stat.water .v{{color:var(--glacial)}}
h2{{font:400 27px/1.2 var(--disp);margin:56px 0 16px;letter-spacing:-.01em}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:left;padding:10px 13px;font:500 10.5px/1.4 var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--mut);border-bottom:1px solid var(--ink)}}
td{{padding:11px 13px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}}
td.m{{font-family:var(--mono);font-size:12.5px}}
td.bad{{color:var(--silt);font-weight:600}}
tbody tr:hover{{background:var(--card)}}
.scroll{{overflow-x:auto}}
.tile{{border:1px solid var(--line);border-radius:3px;margin:26px 0;overflow:hidden;background:var(--card)}}
.th{{display:flex;justify-content:space-between;align-items:baseline;gap:18px;padding:18px 20px;border-bottom:1px solid var(--line);flex-wrap:wrap}}
.th h3{{margin:0;font:500 15px/1 var(--mono)}}
.coord{{color:var(--mut);font:400 12.5px/1 var(--mono);margin-left:12px}}
.chips{{display:flex;gap:9px;flex-wrap:wrap}}
.chip{{font:400 12px/1 var(--body);color:var(--mut);border-left:1px solid var(--line);padding-left:9px}}
.chip b{{font:500 13.5px/1 var(--mono);color:var(--ink);font-variant-numeric:tabular-nums}}
.chip.danger b{{color:var(--silt)}}
.tile img{{width:100%;display:block}}
.note{{border-left:2px solid var(--silt);padding:16px 0 16px 20px;margin:26px 0;font-size:14.5px;color:var(--mut);max-width:74ch}}
.note b{{color:var(--ink);font-weight:600}}
code{{font:400 13px var(--mono);color:var(--ink)}}
footer{{margin-top:56px;padding-top:22px;border-top:1px solid var(--line);color:var(--mut);font:400 12.5px/1.7 var(--mono)}}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Rasuwa District &middot; Nepal &middot; 26 August 2026</div>
  <h1>Glacial flood damage along the Bhote Koshi</h1>
  <p class="sub">A debris avalanche and outburst flood swept 72&nbsp;km of the Bhote Koshi&ndash;Trishuli
  corridor. This assessment compares pre-event basemap imagery against 35&ndash;58&nbsp;cm satellite
  scenes captured 27&ndash;28 August.</p>
  <div class="rule"></div>
</header>

<div class="grid">
  <div class="stat hero"><div class="v">{T['bldg_lost']}</div><div class="l">Buildings lost</div></div>
  <div class="stat"><div class="v">{T['bldg_pre']}</div><div class="l">Buildings before</div></div>
  <div class="stat"><div class="v">{T['pct']}%</div><div class="l">Loss rate</div></div>
  <div class="stat water"><div class="v">{T['w_post']:.2f}</div><div class="l">km&sup2; water after</div></div>
  <div class="stat"><div class="v">{T['tiles']}</div><div class="l">Tiles analysed</div></div>
  <div class="stat"><div class="v">{T['area_km2']}</div><div class="l">km&sup2; surveyed</div></div>
</div>

<div class="note">
  <b>Method.</b> Pre-event Google basemap vs. a cloud-free median composite of Vantor Open Data
  scenes (27–28 Aug, 35–58 cm). Water and debris extent from DINOv3 <code>vit-l-sat</code> patch
  embeddings, prototype-seeded from the OSM river channel. Buildings from a YOLOv11-OBB detector,
  filtered to those with a pre-event counterpart within 10 m.
  <b>These are remote-sensing estimates, not verified ground counts.</b>
</div>

<h2>Results by tile</h2>
<div class="scroll">
<table>
<tr><th>Tile</th><th>Centre</th><th>Scenes</th><th>Bldg before</th><th>Bldg after</th><th>Lost</th>
    <th>Water pre km²</th><th>Water post km²</th><th>Road km cut</th><th>Bridges</th></tr>
{rows}
</table>
</div>

<h2>Imagery</h2>
<p class="sub" style="margin:-6px 0 18px">Showing the {len(shown)} most-affected tiles of {T["tiles"]} analysed.</p>
{cards}

<footer>
  Generated {datetime.datetime.now():%Y-%m-%d %H:%M} · Vantor Open Data (CC-BY-NC-4.0) ·
  Google basemap · OpenStreetMap contributors · {T['tiles']} of {NTILES} corridor tiles complete
</footer>
</div>"""

open(f'{ROOT}/reports/report.html','w').write(html)
print(f"report.html  {len(html)/1024:.0f} KB  {T['tiles']} tiles  {T['bldg_lost']} buildings lost")
