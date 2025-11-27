# Charts & Analysis

This directory contains comprehensive visual analysis of 99 wedding venues in Baku, Azerbaijan.

## 📂 Contents

### Visualizations (10 Charts)

1. **01_price_distribution.png** - Price distribution histogram showing market segments
2. **02_price_categories.png** - Venues grouped by price categories (Budget to Luxury)
3. **03_top_venues_by_views.png** - Top 20 most viewed venues with price color-coding
4. **04_geographic_distribution.png** - Spatial map of venue locations with price/popularity
5. **05_price_vs_views.png** - Correlation analysis between price and popularity
6. **06_location_distribution.png** - Top 15 locations by number of venues
7. **07_event_types.png** - Distribution of event types offered
8. **08_data_completeness.png** - Data quality assessment by field
9. **09_price_by_location.png** - Box plot showing price variation by location
10. **10_popularity_distribution.png** - Venue distribution by view count tiers

### Analysis Document

- **ANALYSIS.md** - Comprehensive 520-line analysis with detailed insights for each chart

## 🎯 Quick Insights

### Market Overview
- **99 venues** analyzed from shadliq.az
- **Average price**: 50.2 AZN per person
- **Median price**: 40 AZN per person
- **View range**: 8,153 - 608,742 views

### Key Findings

1. **Price ≠ Popularity** (r=0.022)
   - No correlation between price and views
   - Success depends on marketing, not pricing

2. **Budget Market Dominance**
   - Most venues price at ≤40 AZN
   - Reflects price-sensitive customer base

3. **Geographic Clustering**
   - "8 km" area is the venue hub
   - Location impacts pricing and competition

4. **Digital-First Market**
   - 98% phone contact completeness
   - 0% email (messaging apps preferred)
   - 100% have gallery images

5. **Multi-Event Strategy**
   - Venues don't rely on weddings alone
   - Birthdays, engagements, corporate events

## 📊 How to Use This Analysis

### For Business Owners:
- Review Chart 3 (Top Venues) for competitive benchmarking
- Study Chart 5 (Price vs Views) to understand that marketing > pricing
- Check Chart 6 (Location) to assess your area's competitiveness

### For Investors:
- Analyze Chart 2 (Price Categories) for market segmentation
- Review Chart 9 (Price by Location) for geographic arbitrage opportunities
- Study Chart 8 (Data Completeness) to understand data quality

### For Researchers:
- Read **ANALYSIS.md** for comprehensive insights
- All charts are 300 DPI, suitable for presentations/reports
- Raw data available in `../shadliq_venues_complete.csv`

## 🔧 Regenerating Charts

To regenerate charts with updated data:

```bash
cd ..
python create_charts.py
```

Requirements:
- Python 3.7+
- pandas, matplotlib, seaborn, numpy

## 📈 Chart Specifications

- **Format**: PNG
- **Resolution**: 300 DPI (print quality)
- **Style**: Seaborn dark grid
- **Color Palette**: HUSL (visually distinct colors)
- **Size**: Various (optimized per chart type)

## 🎨 Color Coding

Throughout the charts, consistent color schemes are used:

- 🟢 **Green**: Budget/Affordable options (≤50 AZN)
- 🟠 **Orange**: Mid-range options (51-80 AZN)
- 🔴 **Red**: Premium/Luxury options (>80 AZN)

## 📝 Citation

If using this analysis in research or reports:

```
Wedding Venue Market Analysis - Baku, Azerbaijan
Data Source: shadliq.az
Sample Size: 99 venues
Collection Date: November 2024
```

## 🔗 Related Files

- `../shadliq_venues_complete.csv` - Raw scraped data
- `../scraper_final.py` - Data collection script
- `../create_charts.py` - Chart generation script
- `../README.md` - Project documentation

---

*For detailed insights and strategic recommendations, see ANALYSIS.md*
