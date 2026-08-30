<div align="center">

<br>

<h1>Flood Damage Mapping with DINOv3</h1>
<h3>The 2026 Nepal Glacial Outburst Flood</h3>

<p>
  <b>Gajesh Ladhar</b><br>
  <sub>Bhote Koshi–Trishuli corridor · Rasuwa & Nuwakot, Nepal · 26 August 2026</sub>
</p>

<p>
  <a href="https://vantor.com/company/open-data-program/"><img src="https://img.shields.io/badge/imagery-Vantor_Open_Data-1a5c8a?style=flat-square&labelColor=2b2b2b"></a>
  <a href="https://creativecommons.org/licenses/by-nc/4.0/"><img src="https://img.shields.io/badge/imagery-CC--BY--NC--4.0-8b2318?style=flat-square&labelColor=2b2b2b"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-MIT-2d6a4f?style=flat-square&labelColor=2b2b2b"></a>
  <img src="https://img.shields.io/badge/GSD-35–58_cm-6f6559?style=flat-square&labelColor=2b2b2b">
  <img src="https://img.shields.io/badge/tiles-75_%2F_187-3d6b7d?style=flat-square&labelColor=2b2b2b">
</p>

<br>

<img src="assets/origin.gif" width="760">

<p><sub><b>Figure 1.</b> Onset. A glacier collapse on the Nepal–China border sends ice and rock 1,200 m into the<br>
Lhende basin, generating the debris avalanche that travelled 72 km down the Trishuli.<br>
Reconstruction © <a href="https://www.youtube.com/watch?v=ORPDEvHJZpA">FRANCE 24</a></sub></p>

</div>

<br>

## Abstract

On 26 August 2026 a glacier collapse on the Nepal–China border triggered a debris avalanche and
glacial lake outburst flood that swept 72 km of the Bhote Koshi–Trishuli corridor, killing **626**
people and leaving **1,924** missing. This work reconstructs the physical damage from openly
licensed satellite imagery acquired 27–28 August, one to two days after the event.

Cloud cover exceeded 71 % on every post-event scene. We recover usable ground by compositing nine
overlapping collections, then measure two quantities along the corridor: **debris and water extent**
from self-supervised DINOv3 features seeded on the mapped river channel, and **building loss** from
an oriented-bounding-box detector matched between pre- and post-event imagery. Results are reported
per 614 m tile and validated against the Copernicus EMS rapid-mapping product for the same event.

<br>

<div align="center">
<img src="assets/hero.jpg" width="900">
<p><sub><b>Figure 2.</b> Damage distribution across 75 analysed tiles. Marker area scales with pre-event<br>
building count; colour encodes the fraction destroyed.</sub></p>
</div>

<br>

## Results

<div align="center">

| | pre-event | post-event | change |
|:--|--:|--:|:--|
| Buildings | 1,167 | 473 | **− 694 · 59 %** |
| Debris / water extent | 6.18 km² | 12.68 km² | **2.05 ×** |
| Road inundated | — | — | **5.01 km** |
| Corridor coverage | — | — | **75 / 187 tiles** |

</div>

> [!NOTE]
> **External validation.** Copernicus EMS activation
> [EMSR927](https://mapping.emergency.copernicus.eu/activations/EMSR927/) reports *"more than 240
> buildings destroyed, 32 damaged"* around Syapru Besi from 27 August imagery. Our pipeline returns
> **214 destroyed** for the same settlement at matched 0.6 m resolution — an independent
> corroboration from different imagery and a different method.

<br>

### Per-tile detail

<div align="center">

| tile | centre | pre | post | destroyed | extent |
|:--|:--|--:|--:|--:|--:|
| `t045` | 28.1617, 85.3375 | 251 | 100 | **151** | 2.86 × |
| `t043` | 28.2510, 85.3647 | 97 | 4 | **93** | 2.68 × |
| `t044` | 28.1644, 85.3413 | 113 | 22 | **91** | 1.86 × |
| `t046` | 28.1638, 85.3428 | 87 | 19 | **68** | 2.11 × |
| `t042` | 28.2556, 85.3653 | 79 | 15 | **64** | 2.30 × |
| `t059` | 28.1904, 85.2979 | 66 | 14 | **52** | 1.07 × |

</div>

<br>

### Qualitative comparison

<div align="center">

<table>
<tr>
<td align="center"><img src="assets/syabrubesi_swipe.gif" width="360"></td>
<td align="center"><img src="assets/timure_swipe.gif" width="360"></td>
</tr>
<tr>
<td align="center"><sub><b>Syabrubesi</b> · 251 → 100 standing</sub></td>
<td align="center"><sub><b>Timure</b> · 97 → 4 standing</sub></td>
</tr>
</table>

<p><sub><b>Figure 3.</b> Pre-event basemap alternating with the 28 August composite. The pale fan filling<br>
each valley floor is the debris deposit; settlements on the channel margin are absent afterwards.</sub></p>

<br>

<table>
<tr>
<th align="center"><sub>&nbsp;</sub></th>
<th align="center"><sub>PRE-EVENT</sub></th>
<th align="center"><sub>POST-EVENT</sub></th>
</tr>
<tr>
<td align="right"><sub><b>Syabrubesi</b></sub></td>
<td><img src="assets/syabrubesi_pre_poly.jpg" width="290"></td>
<td><img src="assets/syabrubesi_post_poly.jpg" width="290"></td>
</tr>
<tr>
<td align="right"><sub><b>Timure</b></sub></td>
<td><img src="assets/timure_pre_poly.jpg" width="290"></td>
<td><img src="assets/timure_post_poly.jpg" width="290"></td>
</tr>
</table>

<p><sub><b>Figure 4.</b> Detected building footprints. Each colour is one oriented bounding box from the<br>
YOLOv11-OBB detector; counts are reported in the tables above.</sub></p>

</div>

<br>

## Method

```
  Google basemap ─────── pre-event RGB · 0.3 / 0.6 m ──────┐
                                                            ├──▶  YOLOv11-OBB  ──▶  footprints
  Vantor Open Data ───── post-event RGB · 9 scenes ─────────┤      pre ↔ post matched ≤ 10 m
  27–28 Aug 2026         per-pixel cloud mask → median      │
                                                            └──▶  DINOv3 vit-l-sat  ──▶  extent
  OpenStreetMap ──────── river · highways · bridges ────────────── prototype seed · cosine sim
```

**Cloud compositing.** Every post-event scene carries 71–81 % cloud, but the nine collections cloud
independently. A per-pixel brightness-and-saturation test masks each scene; a median across the
unmasked stack recovers **100 % clear ground** over Syabrubesi from scenes individually
three-quarters obscured.

**Label-free extent.** DINOv3 `vit-l-sat` patch embeddings are reduced to a single prototype vector
sampled from the OpenStreetMap river channel, then thresholded on cosine similarity. No training
data, no annotation, no fine-tuning.

**Conservative building loss.** A structure is counted as destroyed only when a pre-event footprint
has no post-event detection within 10 m. Anchoring to the pre-event inventory means the surviving
count can never exceed what existed before.

<br>

## Reproducing

```bash
pip install -r requirements.txt

jupyter lab notebooks/analysis.ipynb    # single tile, interactive
python -m nepalflood.batch              # full corridor sweep, resumable
python -m nepalflood.report             # generate the HTML report
```

Detector weights: [`building-miner-stable.pt`](https://huggingface.co/datasets/gajeshladhar/artifacts) → `weights/`

```
src/nepalflood/
├── batch.py             corridor sweep · executes the notebook per tile · resumable
├── detect_highres.py    0.3 m building detection pass
├── render.py            per-tile figure rendering
├── report.py            HTML damage report
└── report_compare.py    Google Open Buildings vs YOLOv11-OBB
configs/tiles.json       187 tile centres · 522 m spacing along the river
notebooks/               analysis.ipynb — reference implementation
outputs/                 building footprints · extent rasters · road vectors
results.json             per-tile metrics
```

<br>

## Data

| source | role | licence |
|:--|:--|:--|
| [Vantor Open Data](https://vantor-opendata.s3.amazonaws.com/events/Nepal-Flooding-Aug-2026/collection.json) | post-event RGB · 35–58 cm · 9 scenes | CC-BY-NC-4.0 |
| Google basemap | pre-event reference | — |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | river · highways · bridges | ODbL |
| ESRI LULC 2024 | water fallback seed | — |
| Sentinel-1 RTC | verified · orbit 85 · 16 → 28 Aug pair | open |
| FRANCE 24 | onset reconstruction (Figure 1) | © FRANCE 24 |

<br>

## Limitations

> [!IMPORTANT]
> These are remote-sensing estimates, not verified ground counts. Figures should be read alongside
> official assessments, not in place of them.

**Acquisition timing.** The event was an outburst surge, not a standing flood. By 28 August the
water had largely drained; what the imagery records is the **debris deposit**. Reported extent
describes the affected corridor rather than peak inundation.

**Detector granularity.** The oriented-box detector merges adjacent structures into single
predictions. Benchmarked against Google Open Buildings over Timure it recovers 4.6 × fewer objects
but approximately 90 % of the same built *area* — it counts compounds where Google counts
structures.

**Resolution sensitivity.** Counts are not stable across image sharpness. Pre- and post-event
imagery must be compared at matched resolution; mixed-resolution pairs inflate apparent loss.

**Tile overlap.** Tiles are spaced 522 m with 614 m footprints to guarantee gap-free coverage of a
meandering channel. Summed per-tile counts therefore double-count approximately 14 % of buildings;
deduplicate spatially before quoting a corridor total.

**Partial coverage.** 75 of 187 tiles are complete. The upper Rasuwa corridor is well covered;
Nuwakot and Bidur are not.

<br>

## Citation

```bibtex
@software{ladhar2026nepalflood,
  author = {Ladhar, Gajesh},
  title  = {Flood Damage Mapping with DINOv3: The 2026 Nepal Glacial Outburst Flood},
  year   = {2026},
  url    = {https://github.com/gajeshladhar/nepal-flood}
}
```

<br>

<div align="center">
<sub>
Imagery © Vantor · CC-BY-NC-4.0 &nbsp;·&nbsp; Map data © OpenStreetMap contributors &nbsp;·&nbsp; Onset footage © FRANCE 24<br>
<b>Built for humanitarian response · not for commercial use</b>
</sub>
</div>
