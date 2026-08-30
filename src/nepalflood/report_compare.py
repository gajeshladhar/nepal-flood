import base64, io, os, datetime
from PIL import Image
ROOT='/Users/gajesh/research/nepalflood'
rows=[
 dict(tile='t042',lat=28.2556,lon=85.3653,google=219,ours=48,g_mean=71.6,o_mean=423.5,g_med=42.6,o_med=339.9,g_area=15687,o_area=20327),
 dict(tile='t043',lat=28.2510,lon=85.3647,google=157,ours=33,g_mean=87.8,o_mean=398.2,g_med=47.6,o_med=376.2,g_area=13788,o_area=13142),
]
rows=[r for r in rows if os.path.exists(f"{ROOT}/outputs/maps/cmp_{r['tile']}.png")]
def b64(p,w=1600):
    im=Image.open(p).convert('RGB')
    if im.width>w: im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS)
    b=io.BytesIO(); im.save(b,'JPEG',quality=76,optimize=True)
    return base64.b64encode(b.getvalue()).decode()
G=sum(r['google'] for r in rows); O=sum(r['ours'] for r in rows)
GA=sum(r['g_area'] for r in rows); OA=sum(r['o_area'] for r in rows)
trs='\n'.join(
 f"<tr><td class=m>{r['tile']}</td><td class=m>{r['lat']:.4f}, {r['lon']:.4f}</td>"
 f"<td class=g>{r['google']}</td><td class=o>{r['ours']}</td><td>{r['google']/r['ours']:.1f}&times;</td>"
 f"<td>{r['g_med']:.0f}</td><td>{r['o_med']:.0f}</td>"
 f"<td>{r['g_area']:,}</td><td>{r['o_area']:,}</td></tr>" for r in rows)
cards=''
for r in rows:
    cards+=f"""<section class="tile">
  <div class="th"><h3>{r['tile']}<span class="coord">{r['lat']:.4f}, {r['lon']:.4f}</span></h3>
  <div class="chips"><span class="chip g"><b>{r['google']}</b> Google</span>
  <span class="chip o"><b>{r['ours']}</b> ours</span>
  <span class="chip"><b>{r['google']/r['ours']:.1f}&times;</b> ratio</span></div></div>
  <img src="data:image/jpeg;base64,{b64(f"{ROOT}/outputs/maps/cmp_{r['tile']}.png")}" alt="{r['tile']}"></section>"""
html=f"""<title>Building Detector Comparison</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--paper:#f7f5f1;--ink:#12100e;--mut:#6f6559;--line:#ddd7cd;--card:#fffdfa;--goog:#2f6fb0;--ours:#c2512c;
--disp:"Instrument Serif",Georgia,serif;--body:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",monospace}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--paper:#14120f;--ink:#ece7df;--mut:#9c9285;--line:#2e2a24;--card:#1b1815;--goog:#6ba8dd;--ours:#e0734d}}}}
:root[data-theme=dark]{{--paper:#14120f;--ink:#ece7df;--mut:#9c9285;--line:#2e2a24;--card:#1b1815;--goog:#6ba8dd;--ours:#e0734d}}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);font:16px/1.65 var(--body);margin:0;padding:0 24px 90px}}
.wrap{{max-width:1180px;margin:0 auto}}
header{{padding:66px 0 26px}}
.eyebrow{{font:500 11.5px/1 var(--mono);letter-spacing:.16em;text-transform:uppercase;color:var(--ours);margin-bottom:18px}}
h1{{font:400 clamp(34px,5.4vw,54px)/1.06 var(--disp);margin:0 0 14px;letter-spacing:-.015em;max-width:18ch;text-wrap:balance}}
.sub{{color:var(--mut);margin:0;max-width:64ch}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin:34px 0 0}}
.stat{{padding:24px 20px;border-right:1px solid var(--line)}}
.stat:last-child{{border-right:none}}
.stat .v{{font:400 38px/1 var(--disp);font-variant-numeric:tabular-nums}}
.stat .l{{font:500 10.5px/1.4 var(--mono);letter-spacing:.1em;text-transform:uppercase;color:var(--mut);margin-top:6px}}
.stat.g .v{{color:var(--goog)}} .stat.o .v{{color:var(--ours)}}
h2{{font:400 26px/1.2 var(--disp);margin:48px 0 14px}}
table{{width:100%;border-collapse:collapse;font-size:13.5px}}
th{{text-align:left;padding:10px 12px;font:500 10.5px/1.4 var(--mono);letter-spacing:.07em;text-transform:uppercase;color:var(--mut);border-bottom:1px solid var(--ink)}}
td{{padding:11px 12px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}}
td.m{{font-family:var(--mono);font-size:12.5px}} td.g{{color:var(--goog);font-weight:600}} td.o{{color:var(--ours);font-weight:600}}
.scroll{{overflow-x:auto}}
.tile{{border:1px solid var(--line);border-radius:3px;margin:22px 0;overflow:hidden;background:var(--card)}}
.th{{display:flex;justify-content:space-between;align-items:baseline;gap:16px;padding:16px 18px;border-bottom:1px solid var(--line);flex-wrap:wrap}}
.th h3{{margin:0;font:500 15px/1 var(--mono)}}
.coord{{color:var(--mut);font:400 12.5px/1 var(--mono);margin-left:12px}}
.chips{{display:flex;gap:10px;flex-wrap:wrap}}
.chip{{font:400 12px/1 var(--body);color:var(--mut);border-left:1px solid var(--line);padding-left:10px}}
.chip b{{font:500 13.5px/1 var(--mono);color:var(--ink)}}
.chip.g b{{color:var(--goog)}} .chip.o b{{color:var(--ours)}}
.tile img{{width:100%;display:block}}
.note{{border-left:2px solid var(--ours);padding:15px 0 15px 20px;margin:24px 0;color:var(--mut);max-width:74ch;font-size:14.5px}}
.note b{{color:var(--ink)}}
footer{{margin-top:44px;padding-top:20px;border-top:1px solid var(--line);color:var(--mut);font:400 12.5px/1.7 var(--mono)}}
</style>
<div class="wrap">
<header>
 <div class="eyebrow">Timure &middot; Rasuwa &middot; pre-flood imagery</div>
 <h1>Google Open Buildings vs. YOLOv11&#8209;OBB</h1>
 <p class="sub">Two building detectors over the same pre-event basemap tiles. They disagree on count
 by roughly 4&times; &mdash; but agree on total built footprint, because they are not counting the same unit.</p>
 <div class="grid">
  <div class="stat g"><div class="v">{G}</div><div class="l">Google buildings</div></div>
  <div class="stat o"><div class="v">{O}</div><div class="l">Our detections</div></div>
  <div class="stat"><div class="v">{G/O:.1f}&times;</div><div class="l">Count ratio</div></div>
  <div class="stat g"><div class="v">{GA/1000:.1f}k</div><div class="l">m&sup2; Google</div></div>
  <div class="stat o"><div class="v">{OA/1000:.1f}k</div><div class="l">m&sup2; ours</div></div>
 </div>
</header>

<div class="note"><b>What the gap means.</b> Google's median footprint is {rows[0]['g_med']:.0f}&nbsp;m&sup2;;
ours is {rows[0]['o_med']:.0f}&nbsp;m&sup2;. Google resolves individual structures &mdash; sheds, outbuildings,
animal shelters &mdash; while the YOLO detector merges an adjacent cluster into one oriented box. Total
built area lands within {abs(GA-OA)/max(GA,OA)*100:.0f}% of each other, so both find the same ground.
For a damage count, Google approximates <b>structures</b> and ours approximates <b>compounds or households</b>.</div>

<h2>Per-tile</h2>
<div class="scroll"><table>
<tr><th>Tile</th><th>Centre</th><th>Google</th><th>Ours</th><th>Ratio</th>
<th>Google med m&sup2;</th><th>Ours med m&sup2;</th><th>Google total m&sup2;</th><th>Ours total m&sup2;</th></tr>
{trs}
</table></div>

<h2>Detections on basemap</h2>
{cards}

<footer>Generated {datetime.datetime.now():%Y-%m-%d %H:%M} &middot; Google Open Buildings &middot;
building-miner YOLOv11-OBB &middot; Google basemap (pre-event)</footer>
</div>"""
open(f'{ROOT}/reports/report_compare.html','w').write(html)
print(f"report_compare.html {len(html)/1024:.0f} KB  {len(rows)} tiles  {G} vs {O}")
