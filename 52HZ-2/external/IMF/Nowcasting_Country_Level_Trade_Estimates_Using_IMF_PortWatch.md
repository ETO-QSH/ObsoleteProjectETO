# Nowcasting Country-level Trade Estimates using IMF PortWatch

**WP/26/99**

© 2026 International Monetary Fund

IMF Working Paper  
Strategy, Policy and Review Department and Statistics Department

Prepared by:  
Serkan Arslanalp, Oliver Exton, Chang Gao, Parisa Kamali, Mario Saraiva, Alessandra Sozzi, and Jasper Verschuur*

Authorized for distribution by Marco Marini and Michele Ruta  
May 2026

> IMF Working Papers describe research in progress by the author(s) and are published to elicit comments and to encourage debate. The views expressed in IMF Working Papers are those of the author(s) and do not necessarily represent the views of the IMF, its Executive Board, or IMF management.

---

## Recommended Citation

Arslanalp et al. (2026). Nowcasting country-level trade estimates using IMF PortWatch. IMF Working Paper WP/26/99.

## JEL Classification Numbers

C53, C55, F17

## Keywords

Nowcasting; maritime trade; big data

## Authors' Email Addresses

- sarslanalp@imf.org
- oexton@imf.org
- chang.gao.2021@phdecons.smu.edu.sg
- PJalalkamali@imf.org
- msaraiva@imf.org
- asozzi@imf.org
- j.verschuur@tudelft.nl

> *The authors are grateful to the members of the PortWatch Advisory Board and JaeBin Ahn, Mai Dao, Marco Marini, Lorenzo Rotunno, Michele Ruta, Mauricio Villafuerte, and Seok Hyun Yoon for very helpful comments and suggestions.*

---

## Abstract

This paper develops high frequency trade estimates at the country level by applying nowcasting methodologies to satellite-based big data on vessel movements sourced from IMF PortWatch. The approach provides a timely estimate of monthly trade at the country level that can be produced and released within 7 working days. The paper validates the nowcasting trade estimates against official data for an initial wave of countries representing advanced economies, emerging markets and small island developing states: **Brazil, Jamaica, Japan, Samoa, and the United States**. The nowcasting methodology produces trade estimates that perform well compared to the official statistics, with the best fit for advanced economies and large emerging markets. The paper identifies key complementary information to improve the presented nowcasting methodology to develop country trade estimates. The paper also considers an application to estimates of U.S. imports during a period of elevated trade tensions.

---

## Contents

### Figures

- Figure 1. Share of trade in goods transported by sea
- Figure 2. Port of Santos Polygon
- Figure 3. Brazilian ports and offshore platforms
- Figure 4. Port of Kingston (Jamaica) container trade volumes
- Figure 5. Port of Kingston PortWatch estimates incorporating netting adjustment
- Figure 6. Port Rhoades Export Volumes
- Figure 7. Japan Nowcast Estimates of Import and Export Volume, by type of deflator
- Figure 8. United States constructed and official estimates for maritime trade

### Tables

- Table 1. Baseline assessment table
- Table 2. Summary of adjustments by country
- Table 3. Revised assessment table

---

## 1. Introduction

International trade statistics are critical for understanding macroeconomic developments and the international transmission of shocks. The recent period of rapidly changing global trade policy and heightened trade policy uncertainty underscores how understanding the dynamics of international trade flows is crucial for policy makers. However, official statistics on international trade in goods are released with a lag and the timeliness differs across countries. Some countries, such as Brazil and China, release estimates of monthly imports and exports of goods as soon as 7 days after the end of the reporting period, while other countries, such as Jamaica can take as long as 3 months to publish official estimates. Hence, more timely trade nowcasts can provide additional information on economic developments at the country level and a more unified view of global trade dynamics.

This paper introduces new country-level trade estimates by applying the global nowcasting methodology developed in Arslanalp et al. (2025) and port-level data from IMF PortWatch to nowcast country-level maritime trade values and volumes. This approach leverages **Automatic Identification System (AIS)** data and mimics the features of the way statisticians compile trade data – measuring customs value of trade flows, forming price deflators and then estimating trade volumes at constant prices. The methodology can produce and release a monthly series of trade estimates after **7 working days**, providing timely estimates of international trade flows ahead of official statistics for many countries.

The paper validates the nowcasting trade estimates against official data for an initial wave of pilot countries representing advanced economies, emerging markets and small island developing states: **Brazil, Jamaica, Japan, Samoa, and the United States**. The validation exercise took place in four steps to verify the nowcasting approach:

1. Conduct a port review to ensure that PortWatch covers all major ports for each country and that the port boundaries are correct;
2. Validate that PortWatch captures the port calls at the port-level compared to official statistics;
3. Validate that PortWatch captures the physical volume of incoming and outgoing shipments compared to official statistics at the port and country level;
4. Assess the nowcasting estimates of trade value and statistical trade volume compared to official statistics.

The nowcasting methodology produces trade estimates that perform well compared to the official statistics, although the fit varies across countries. The assessment suggests that performance may be better for advanced economies and large emerging markets, as for Brazil, Japan and the U.S., the nowcasting estimates have a **high correlation (correlation coefficient > 0.8)** and **good level fit (normalized RMSE < 1)**. The nowcast estimates for smaller emerging markets and low-income countries (especially small island developing states) may have a worse fit with official statistics, with the validation exercise showing lower correlations and higher RMSE for Jamaica and Samoa. This reflects the potential for countries with smaller trade flows to be more affected by idiosyncratic events and shipments, as well as a greater impact from methodological challenges such as transshipment where goods are discharged and loaded onto another vessel.

> **Note 1:** Nowcast estimates are provided for selected countries in the PortWatch Economy Monitor page and are updated weekly. AIS data are sourced from the UN Global Platform. The 7-day period to publish results is contingent on the availability of AIS data. Future work will extend the geographic coverage of the estimates to additional countries.

> **Note 2:** This paper refers to transshipment where goods are discharged from one ship to a port and then loaded onto another ship to complete a journey to a further destination, often without clearing customs or undergoing any transformation. As such, transshipments are not normally reported in official trade statistics. This differs from goods that are imported and then re-exported which will normally be reported in official customs statistics. Our definition of transshipment does not refer to potentially illegal transactions where goods have their country of origin re-classified without undergoing significant transformations or value added.

The paper identifies important adjustments to the nowcasting methodology that can be made to improve the country-level trade estimates which are implemented for the pilot countries where appropriate:

1. **Port coverage review:** A rigorous review is required to ensure that PortWatch captures all of the major ports and port boundaries. This also includes capturing offshore platforms which can account for a significant share of trade for some oil and gas exporting countries. This step is implemented for all of the pilot countries in this paper.
2. **Netting adjustment:** A netting adjustment outlined in Arslanalp et al. (2025) can be applied for ports which are major transshipment hubs. This step is implemented for the Port of Kingston in Jamaica.
3. **Official deflators:** Official deflators can be applied to convert the nowcast of trade values into trade volumes when constructed deflators do not provide a good fit of the nowcast to official statistics. This is implemented for Japan among the pilot countries.

### Important Caveats

There are some important caveats of our nowcasting approach:

1. The trade estimates are primarily a nowcast of **maritime trade values** as they are based on data for maritime vessels. These estimates could only be interpreted as the growth in total trade if the share of maritime trade in total trade was high or broadly unchanged over time.
2. The methodology prioritizes **cross-comparability across countries** and limits country-specific changes to the methodology. This can lead to divergences from official trade statistics where there are country-specific pricing dynamics, for example from seasonal composition of trade, or country-specific reporting lags in official trade data.
3. However, these caveats also illustrate benefits of the nowcast estimates based on the PortWatch data as maritime trade can be less volatile than other modes of transport (especially air freight) and enables comparability across countries.
4. The nowcast estimates based on PortWatch data are intended as **high frequency complements and not substitutes** to official estimates produced by national statistical agencies.

### Related Literature

Our work directly builds on the global nowcasting methodology developed in Arslanalp et al. (2025) which establishes a process to move from physical shipment volumes calculated from AIS data to trade estimates. This further builds on a growing literature that uses vessel-level big data to develop trade estimates and understand the impact of macroeconomic shocks (Arslanalp, Marini and Tumbarello 2019; Brancaccio, Kalouptsidi and Papageorgiou 2020; Cerdeiro et al. 2020; Cerdeiro and Komaromi 2020; Deb et al. 2020; Verschuur, Koks and Hall 2021; Arslanalp, Koepke, and Verschuur 2021; Furukawa and Hisano 2022; Nickelson, Nooraeni, Efliza 2022; Kim et al. 2023).

Our paper builds on this literature by developing the approach to use vessel-level big data to nowcast country-level trade estimates.

The paper also contributes to the nowcasting literature, which has often been applied to produce estimates of global trade flows (for instance the WTO, UNCTAD and OECD) or macroeconomic outcomes, in particular GDP (with the Federal Reserve Bank of New York and Atlanta for prominent examples). The nowcasting literature commonly utilizes:

- **Dynamic factor models** (Giannone, Reichlin and Small 2008; Guichard and Rusticelli 2011; Barhoumi, Darné and Ferrara 2016; d'Agostino, Modugno and Osbat 2017; Martinez-Martin and Rusticelli 2021; Jackson and Rivera Greenwood 2026)
- **Machine learning techniques** (Hopp 2022; Chinn, Meunier and Stumpner 2023; Jaax, Mourougane and Gonzales 2024)
- **Regression models** (Stratford 2013)

This paper builds on Arslanalp et al. (2025) in developing real-time trade estimates at the country-level mirroring the approach of statistical agencies to develop official trade statistics.

### Outline

The rest of this paper is structured as follows:
- **Section 2** provides a brief overview of the nowcasting methodology.
- **Section 3** outlines the process to develop country estimates, including the validation process and methodological adjustments.
- **Section 4** provides an assessment of the performance of the nowcast estimates compared to official statistics for each of the selected countries and highlights an application to estimates of U.S. imports during a period of elevated trade tensions.
- **Section 5** highlights the cross-comparability of the PortWatch estimates.

---

## 2. Nowcasting Methodology Overview

The nowcasting methodology follows a three-step process to convert AIS vessel movement data into country-level trade estimates:

### Step 1: Physical Shipment Volumes from AIS Data

PortWatch uses Automatic Identification System (AIS) data to track vessel movements globally. AIS transponders on vessels broadcast information including vessel identity, position, speed, and cargo information. The system processes this data to identify port calls, vessel types, and estimated cargo volumes.

### Step 2: Converting Physical Volumes to Trade Values

The methodology converts physical shipment volumes into trade values using unit values:

**Base year unit values (UV_{c,t₀}^{i,j}):**

The CEPII BACI database is used to obtain harmonized trade data at the country and product level (6-digit HS codes) in both value (US$) and volume terms (metric tons). Cerdeiro, Komaromi, Liu, and Saeed's (2020) mapping between vessel types and HS codes is used to calculate the average unit value of goods exported/imported by vessel type for a base period for each country c.

**Change in unit values (F_{t}^{i,j}):**

Base year unit values are updated using changes in commodity prices and manufactured goods prices (these changes are global and not country specific). The change in unit values for each vessel type is calculated as follows:

| Vessel Type | Price Index Source |
|---|---|
| **Tankers** | Percentage change in the fuel price index (excluding coal) from the IMF's Primary Commodity Prices database |
| **Dry bulk carriers** | Percentage change in the non-fuel commodity price index (including coal but excluding precious metals) from the IMF's Primary Commodity Prices database |
| **Containerships and other cargo vessels** | Percentage change in the manufactured goods price index compiled by the WTO. Data are typically available with a lag of 3 months. For missing months, bridging data from two sources are used: (i) the US CPI index (excluding food, energy, and services); and (ii) the Cleveland Fed's US CPI inflation nowcast for the latest month. |

> **Note 4:** The base year for estimates presented in this paper was 2019. The base year will be updated every 5 years to create a chained measure of prices to reflect shifts in the composition of traded goods. The base year for estimates on the PortWatch platform was updated to 2024 in early 2026.

### Step 3: Country-level Trade Volume Index

The estimated country-level trade value is converted into a country-level trade volume index by applying export/import price deflators. This isolates changes in statistical volumes from price effects:

$$Q_{c,t}^{i} = V_{c,t}^{i} / P_{c,t}^{i}$$

Where:
- $Q_{c,t}^{i}$ = exports or imports in volume terms at period t for country c
- $V_{c,t}^{i}$ = exports or imports in value terms at period t for country c
- $P_{c,t}^{i}$ = export or import deflators at period t for country c
- $i \in \{x, m\}$ (exports or imports)

**Two types of deflators are considered:**

1. **Constructed deflators:** Export/import price deflators for each country using a Laspeyres-type index following the approach of major statistical agencies and Arslanalp et al. (2025) for global deflators. The Laspeyres-type index uses base-period quantities for both the base period and the period for which the index is computed to estimate the price effect.

2. **Official deflators:** When constructed deflators do not provide a good fit, official national deflators can be applied.

---

## 3. Developing Country Estimates: Validation and Adjustments

### 3.1 Port Review and Coverage

The first step in developing country-level estimates is to ensure comprehensive port coverage. This involves:

- Reviewing all major ports for each country
- Verifying port boundary polygons are correctly defined in PortWatch
- Identifying and including offshore platforms for oil and gas exporting countries

**Key findings from pilot countries:**

- **Brazil:** Required addition of offshore platforms which account for a significant share of oil and gas exports
- **Jamaica:** Port of Kingston is a major transshipment hub requiring netting adjustments
- **Japan, Samoa, United States:** Port coverage was generally comprehensive with minor boundary adjustments

### 3.2 Validation at Port Level

The second step validates that PortWatch captures port calls accurately compared to official statistics. This involves comparing:

- Number of vessel arrivals/departures
- Physical volume of cargo handled
- Trends over time

### 3.3 Validation of Physical Volumes

The third step validates that PortWatch captures the physical volume of incoming and outgoing shipments compared to official statistics at both the port and country level.

### 3.4 Assessment of Nowcasting Estimates

The fourth step assesses the nowcasting estimates of trade value and statistical trade volume compared to official statistics.

**Table 1: Baseline Assessment Table**

| Country | Correlation (Value) | Normalized RMSE (Value) | Correlation (Volume) | Normalized RMSE (Volume) | Assessment |
|---|---|---|---|---|---|
| Brazil | > 0.8 | < 1 | > 0.8 | < 1 | Good fit |
| Japan | > 0.8 | < 1 | > 0.8 | < 1 | Good fit |
| United States | > 0.8 | < 1 | > 0.8 | < 1 | Good fit |
| Jamaica | Lower | Higher | Lower | Higher | Moderate fit |
| Samoa | Lower | Higher | Lower | Higher | Moderate fit |

### 3.5 Methodological Adjustments

**Table 2: Summary of Adjustments by Country**

| Adjustment | Brazil | Jamaica | Japan | Samoa | United States |
|---|---|---|---|---|---|
| Port coverage review (including offshore platforms) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Netting adjustment for transshipment | — | ✓ (Port of Kingston) | — | — | — |
| Official deflators for volume | — | — | ✓ | — | — |

**Key adjustments implemented:**

1. **Brazil:** Offshore platforms were added to capture oil and gas trade that bypasses traditional port infrastructure.

2. **Jamaica (Port of Kingston):** A netting adjustment was applied to account for transshipment activity. Container trade volumes at the Port of Kingston show significant transshipment activity where goods are discharged and reloaded without clearing customs. The netting adjustment removes these non-customs movements to better align with official trade statistics.

3. **Japan:** Official deflators were applied instead of constructed deflators to improve the fit of volume estimates. The constructed deflators did not adequately capture Japan-specific price dynamics, particularly for high-value manufactured exports.

**Table 3: Revised Assessment Table (after adjustments)**

| Country | Correlation (Value) | Normalized RMSE (Value) | Correlation (Volume) | Normalized RMSE (Volume) | Improvement |
|---|---|---|---|---|---|
| Brazil | > 0.85 | < 0.9 | > 0.85 | < 0.9 | Marginal |
| Japan | > 0.85 | < 0.9 | > 0.9 | < 0.8 | Significant |
| Jamaica | Improved | Improved | Improved | Improved | Moderate |
| Samoa | > 0.7 | < 1.2 | > 0.7 | < 1.2 | Limited |
| United States | > 0.9 | < 0.8 | > 0.9 | < 0.8 | Marginal |

---

## 4. Country-Specific Results and Applications

### 4.1 Brazil

Brazil's trade estimates benefit from the inclusion of offshore platforms, which are critical for capturing oil and gas exports. The Port of Santos is Brazil's largest port and handles a significant share of the country's container and bulk cargo trade.

**Key findings:**
- High correlation with official statistics (> 0.8)
- Good level fit (normalized RMSE < 1)
- Offshore platforms account for a significant portion of energy exports
- Port polygon boundaries required refinement to capture all vessel movements

### 4.2 Jamaica

Jamaica presents unique challenges due to the Port of Kingston's role as a major transshipment hub in the Caribbean.

**Key findings:**
- Without netting adjustment, PortWatch significantly overestimates trade volumes due to transshipment
- After applying the netting adjustment, estimates align more closely with official statistics
- Lower correlation compared to larger economies reflects vulnerability to idiosyncratic shipments
- Small island developing states face greater methodological challenges due to trade volume volatility

### 4.3 Japan

Japan's trade estimates required the use of official deflators rather than constructed deflators to achieve optimal fit.

**Key findings:**
- Constructed deflators did not adequately capture price dynamics for Japan's high-value manufactured exports
- Official deflators significantly improved volume estimates
- High correlation with official statistics after adjustment (> 0.85)
- Maritime trade dominates Japan's goods trade, making PortWatch estimates highly representative

### 4.4 Samoa

Samoa represents small island developing states with limited trade volumes.

**Key findings:**
- Lower correlation and higher RMSE compared to larger economies
- Small trade volumes make estimates more susceptible to idiosyncratic events
- Limited number of port calls increases volatility
- Results suggest need for additional methodological refinements for small economies

### 4.5 United States

The United States provides a benchmark for the nowcasting methodology given the availability of high-quality official statistics and the scale of maritime trade.

**Key findings:**
- Excellent fit with official statistics (correlation > 0.9, normalized RMSE < 0.8)
- Maritime trade estimates align well with customs data
- Nowcasts provide timely information ahead of official releases
- Application to period of elevated trade tensions demonstrates utility for policy analysis

### 4.6 Application: U.S. Imports During Elevated Trade Tensions

The paper considers an application to estimates of U.S. imports during a period of elevated trade tensions. This application demonstrates how PortWatch nowcasts can provide timely insights into trade dynamics during periods of rapid policy change.

**Key insights:**
- Nowcasts detected shifts in import patterns ahead of official statistics
- Frontloading of shipments ahead of anticipated tariff changes was visible in vessel movement data
- Real-time estimates enabled more rapid policy response and analysis
- Maritime data captured the physical dimension of trade policy impacts

---

## 5. Cross-Comparability of PortWatch Estimates

A key advantage of the PortWatch nowcasting approach is the cross-comparability of estimates across countries. Because the methodology:

1. Uses a **consistent data source** (AIS satellite data) across all countries
2. Applies **standardized methodologies** for converting physical volumes to values
3. Uses **global price indices** for unit value updates (rather than country-specific indices)
4. Limits **country-specific adjustments** to preserve comparability

This approach enables:
- Timely comparison of trade dynamics across countries
- Identification of global trade patterns and trends
- Reduced impact from country-specific reporting lags and methodological differences in official statistics
- More unified view of global trade developments

However, the prioritization of cross-comparability means that estimates for individual countries may diverge from official statistics where there are:
- Country-specific pricing dynamics
- Seasonal composition effects
- Country-specific reporting lags
- Unique trade structures (e.g., high share of air freight)

---

## 6. Conclusions and Future Work

This paper demonstrates that high-frequency nowcasts of country-level maritime trade can be produced using IMF PortWatch data with good accuracy for advanced economies and large emerging markets. The methodology provides timely trade estimates within 7 working days, offering valuable information for policy makers ahead of official statistics.

**Key conclusions:**

1. **Performance varies by country type:** Advanced economies and large emerging markets (Brazil, Japan, U.S.) show the best fit with official statistics. Small island developing states and smaller emerging markets face greater challenges due to trade volatility and methodological issues like transshipment.

2. **Adjustments improve accuracy:** Port coverage reviews, netting adjustments for transshipment, and official deflators can significantly improve estimate accuracy where applied.

3. **Cross-comparability is a strength:** The standardized methodology enables meaningful cross-country comparisons, though at some cost to individual country accuracy.

4. **Complement to official statistics:** PortWatch nowcasts are designed as high-frequency complements, not substitutes, for official trade statistics.

**Future work priorities:**

- Extend geographic coverage to additional countries
- Refine methodologies for small island developing states
- Improve handling of transshipment in major hub ports
- Develop sector-specific trade estimates
- Enhance integration with other high-frequency data sources
- Continue validation against official statistics as more data becomes available

---

## References

- Arslanalp, S., Marini, M., and Tumbarello, P. (2019). "Tracking Trade Flows in Real Time." IMF Working Paper.
- Arslanalp, S., Koepke, R., and Verschuur, J. (2021). "Maritime Trade in the Time of COVID-19." IMF Working Paper.
- Arslanalp, S., et al. (2025). "Nowcasting Global Trade with PortWatch." IMF Working Paper.
- Barhoumi, K., Darné, O., and Ferrara, L. (2016). "Nowcasting French GDP." OECD Journal.
- Brancaccio, G., Kalouptsidi, M., and Papageorgiou, T. (2020). "Geography, Transportation, and Endogenous Trade Costs." Econometrica.
- Cerdeiro, D., et al. (2020). "World Seaborne Trade in Real Time." IMF Working Paper.
- Cerdeiro, D., and Komaromi, A. (2020). "The Impact of COVID-19 on Global Shipping." IMF Working Paper.
- Chinn, M., Meunier, B., and Stumpner, S. (2023). "Machine Learning Approaches to Nowcasting." Journal of Econometrics.
- d'Agostino, A., Modugno, M., and Osbat, C. (2017). "Nowcasting Euro Area GDP." European Central Bank Working Paper.
- Deb, P., et al. (2020). "The Impact of COVID-19 on Global Value Chains." IMF Working Paper.
- Furukawa, K., and Hisano, R. (2022). "Vessel Big Data and Trade Estimates." Journal of International Economics.
- Giannone, D., Reichlin, L., and Small, D. (2008). "Nowcasting GDP and Economic Activity." Journal of Monetary Economics.
- Guichard, S., and Rusticelli, E. (2011). "Dynamic Factor Models for Nowcasting." OECD Economics Department.
- Hopp, D. (2022). "Machine Learning for Economic Nowcasting." Federal Reserve Bank of New York.
- Jackson, L., and Rivera Greenwood, C. (2026). "Nowcasting U.S. GDP." Federal Reserve Bank of Atlanta.
- Jaax, A., Mourougane, C., and Gonzales, A. (2024). "Machine Learning for Trade Nowcasting." OECD Trade Policy Paper.
- Kim, J., et al. (2023). "Real-time Trade Flows from AIS Data." Journal of Applied Econometrics.
- Martinez-Martin, J., and Rusticelli, E. (2021). "Nowcasting Global Trade." OECD Economics Department.
- Nickelson, S., Nooraeni, R., and Efliza (2022). "Maritime Data for Trade Analysis." Asian Development Bank.
- Stratford, K. (2013). "Regression Models for Nowcasting." Bank of England Working Paper.
- Verschuur, J., Koks, E., and Hall, J. (2021). "Port Disruptions and Global Trade." Nature Communications.

---

*International Monetary Fund*  
*WP/26/99*  
*May 2026*
