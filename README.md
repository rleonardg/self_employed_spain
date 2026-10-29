# Analysis_self_employed_Spain
Which sectors create and which destroy self-employed businesses (*autónomos*) in Spain?

| Requirements | Skills |
|--------------|--------|
| - `python3.10+`<br> - `Pandas`<br> - `Numpy`<br> - `Matplotlib`<br> - `scikit-learn`<br> - `SciPy`<br> - `excel`<br> - `Jupyter`<br> | - `Data extracting`<br> - `Data cleaning and transformation`<br> - `Data wrangling`<br> - `Data visualization`<br> - `Linear regression`<br> - `Data Analysis` |

## Introduction

### Report objective
The objective of the analysis is to identify which economic sectors gain and which lose self-employed businesses in Spain between 2019 and 2022, and to check whether the sectors where more people start a business are also the ones where more people close it.

### Indicators
For every CNAE 2009 division and year:

- **Birth rate** = births / active businesses × 100
- **Death rate** = deaths / active businesses × 100
- **Net rate** = birth rate − death rate. Positive: the sector gains self-employed businesses; negative: it loses them.

## General Analysis

### National trend
1. Self-employment alternates between net creation and net destruction: **+2.39 %** in 2019, **−0.98 %** in 2020, **+1.50 %** in 2021 and **−1.05 %** in 2022.
2. The 2020 drop came from a collapse in births (birth rate from 12.5 % to 9.3 %, lower in 49 of the 50 sectors analysed) while deaths barely moved (10.1 % → 10.3 %). The 2022 drop is the opposite: the death rate rose from 9.2 % to 11.1 % and went up in 48 of the 50 sectors.

### Net rate by sector
1. Creative, digital and business services gained self-employed businesses **every year**: film, video, TV and music (59), advertising (73), employment activities (78), IT programming and consulting (62), management consulting (70), publishing (58), plus building construction (41, 43) and personal services (96).
2. Traditional manufacturing and trade lost them **every year**: leather and footwear (15), wood (16), furniture (31), metal products (25), non-metallic minerals (23), wholesale (46) and retail (47). So did veterinary activities (75) and gambling (92).
3. The pandemic hit tourism and leisure hardest in 2020: travel agencies −9.4 %, renting −5.0 %, food and beverage service −3.9 % and accommodation −3.2 %. 33 of the 50 sectors were negative that year, against 9 in 2019.

<img src="assets/heatmap_tasa_neta.png">

### Do sectors with more births also have more deaths? Linear regression
<img src="assets/regresion_lineal.png">

## Resources
- [INE - Demografía armonizada de empresas: stock, nacimientos y muertes de empresas](https://ine.es/dynt3/inebase/es/index.htm?padre=6103)
- [Ley Rider - Real Decreto-ley 9/2021 (Garrigues)](https://www.garrigues.com/es_ES/noticia/entra-vigor-ley-rider-nuevas-exigencias-laborales-plataformas-digitales-reparto)
