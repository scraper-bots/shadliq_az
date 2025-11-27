import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import re

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read the data
df = pd.read_csv('shadliq_venues_complete.csv')

# Data preprocessing
df['price_numeric'] = pd.to_numeric(df['price_per_person'], errors='coerce')
df['views_numeric'] = pd.to_numeric(df['views'], errors='coerce')
df['latitude_numeric'] = pd.to_numeric(df['latitude'], errors='coerce')
df['longitude_numeric'] = pd.to_numeric(df['longitude'], errors='coerce')

print("Creating charts...")
print(f"Total venues: {len(df)}")
print(f"Venues with price: {df['price_numeric'].notna().sum()}")
print(f"Venues with views: {df['views_numeric'].notna().sum()}")

# ============================================================================
# Chart 1: Price Distribution
# ============================================================================
print("\n1. Creating price distribution chart...")
fig, ax = plt.subplots(figsize=(12, 6))

prices = df['price_numeric'].dropna()
bins = [0, 40, 60, 80, 100, 120, 150]
ax.hist(prices, bins=bins, edgecolor='black', alpha=0.7, color='#3498db')

ax.set_xlabel('Price per Person (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Venues', fontsize=12, fontweight='bold')
ax.set_title('Price Distribution of Wedding Venues in Baku', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add statistics text
mean_price = prices.mean()
median_price = prices.median()
stats_text = f'Mean: {mean_price:.1f} AZN\nMedian: {median_price:.1f} AZN\nTotal venues: {len(prices)}'
ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
        verticalalignment='top', horizontalalignment='right',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10)

plt.tight_layout()
plt.savefig('charts/01_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Mean price: {mean_price:.1f} AZN, Median: {median_price:.1f} AZN")

# ============================================================================
# Chart 2: Price Range Categories
# ============================================================================
print("\n2. Creating price range categories chart...")
fig, ax = plt.subplots(figsize=(10, 6))

price_ranges = []
for price in prices:
    if price <= 40:
        price_ranges.append('Budget (≤40)')
    elif price <= 60:
        price_ranges.append('Affordable (41-60)')
    elif price <= 80:
        price_ranges.append('Mid-range (61-80)')
    elif price <= 100:
        price_ranges.append('Premium (81-100)')
    else:
        price_ranges.append('Luxury (>100)')

range_counts = pd.Series(price_ranges).value_counts()
colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c', '#9b59b6']
bars = ax.bar(range(len(range_counts)), range_counts.values, color=colors, edgecolor='black', alpha=0.8)

ax.set_xticks(range(len(range_counts)))
ax.set_xticklabels(range_counts.index, rotation=45, ha='right')
ax.set_ylabel('Number of Venues', fontsize=12, fontweight='bold')
ax.set_title('Venues by Price Category', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_price_categories.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 3: Views Distribution (Top 20)
# ============================================================================
print("\n3. Creating views distribution chart...")
fig, ax = plt.subplots(figsize=(14, 8))

top_venues = df.nlargest(20, 'views_numeric')[['name', 'views_numeric', 'price_numeric']].copy()
top_venues = top_venues.sort_values('views_numeric', ascending=True)

bars = ax.barh(range(len(top_venues)), top_venues['views_numeric'], color='#e74c3c', edgecolor='black', alpha=0.7)

# Color bars by price if available
for i, (idx, row) in enumerate(top_venues.iterrows()):
    if pd.notna(row['price_numeric']):
        if row['price_numeric'] <= 50:
            bars[i].set_color('#2ecc71')
        elif row['price_numeric'] <= 80:
            bars[i].set_color('#f39c12')
        else:
            bars[i].set_color('#e74c3c')

ax.set_yticks(range(len(top_venues)))
ax.set_yticklabels(top_venues['name'], fontsize=9)
ax.set_xlabel('Number of Views', fontsize=12, fontweight='bold')
ax.set_title('Top 20 Most Viewed Venues', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#2ecc71', label='Budget (≤50 AZN)'),
                   Patch(facecolor='#f39c12', label='Mid-range (51-80 AZN)'),
                   Patch(facecolor='#e74c3c', label='Premium (>80 AZN)')]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig('charts/03_top_venues_by_views.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 4: Geographic Distribution (Scatter Map)
# ============================================================================
print("\n4. Creating geographic distribution map...")
fig, ax = plt.subplots(figsize=(12, 10))

# Filter valid coordinates
geo_df = df[df['latitude_numeric'].notna() & df['longitude_numeric'].notna()].copy()

# Create scatter plot colored by price
scatter = ax.scatter(geo_df['longitude_numeric'], geo_df['latitude_numeric'],
                     c=geo_df['price_numeric'], s=geo_df['views_numeric']/500,
                     cmap='RdYlGn_r', alpha=0.6, edgecolors='black', linewidth=0.5)

ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
ax.set_title('Geographic Distribution of Venues in Baku', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Price (AZN)', fontsize=10, fontweight='bold')

# Add legend for size
sizes = [10000, 50000, 100000]
labels = ['10K views', '50K views', '100K views']
for size, label in zip(sizes, labels):
    ax.scatter([], [], s=size/500, c='gray', alpha=0.6, edgecolors='black', label=label)
ax.legend(scatterpoints=1, frameon=True, labelspacing=2, title='Popularity', loc='upper left')

plt.tight_layout()
plt.savefig('charts/04_geographic_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 5: Price vs Views Correlation
# ============================================================================
print("\n5. Creating price vs views correlation chart...")
fig, ax = plt.subplots(figsize=(10, 6))

# Filter data with both price and views
corr_df = df[(df['price_numeric'].notna()) & (df['views_numeric'].notna())].copy()

ax.scatter(corr_df['price_numeric'], corr_df['views_numeric'],
           alpha=0.6, s=100, edgecolors='black', linewidth=0.5, color='#3498db')

# Add trend line
if len(corr_df) > 1:
    z = np.polyfit(corr_df['price_numeric'], corr_df['views_numeric'], 1)
    p = np.poly1d(z)
    ax.plot(corr_df['price_numeric'].sort_values(), p(corr_df['price_numeric'].sort_values()),
            "r--", alpha=0.8, linewidth=2, label=f'Trend line')

ax.set_xlabel('Price per Person (AZN)', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Views', fontsize=12, fontweight='bold')
ax.set_title('Price vs Popularity (Views)', fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Calculate correlation
correlation = corr_df['price_numeric'].corr(corr_df['views_numeric'])
ax.text(0.05, 0.95, f'Correlation: {correlation:.3f}', transform=ax.transAxes,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        fontsize=10)

ax.legend()
plt.tight_layout()
plt.savefig('charts/05_price_vs_views.png', dpi=300, bbox_inches='tight')
plt.close()
print(f"   Correlation coefficient: {correlation:.3f}")

# ============================================================================
# Chart 6: Location Distribution
# ============================================================================
print("\n6. Creating location distribution chart...")
fig, ax = plt.subplots(figsize=(12, 8))

# Extract locations from location_short field
locations = df['location_short'].dropna()
location_counts = locations.value_counts().head(15)

bars = ax.barh(range(len(location_counts)), location_counts.values,
               color='#9b59b6', edgecolor='black', alpha=0.7)

ax.set_yticks(range(len(location_counts)))
ax.set_yticklabels(location_counts.index)
ax.set_xlabel('Number of Venues', fontsize=12, fontweight='bold')
ax.set_title('Top 15 Locations by Number of Venues', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add value labels
for i, (bar, value) in enumerate(zip(bars, location_counts.values)):
    ax.text(value, i, f' {value}', va='center', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/06_location_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 7: Event Types Distribution
# ============================================================================
print("\n7. Creating event types distribution chart...")
fig, ax = plt.subplots(figsize=(10, 6))

# Parse event types
all_events = []
for events in df['event_types'].dropna():
    event_list = [e.strip() for e in events.split(',')]
    all_events.extend(event_list)

event_counts = pd.Series(all_events).value_counts().head(8)

bars = ax.bar(range(len(event_counts)), event_counts.values,
              color='#e67e22', edgecolor='black', alpha=0.7)

ax.set_xticks(range(len(event_counts)))
ax.set_xticklabels(event_counts.index, rotation=45, ha='right')
ax.set_ylabel('Number of Venues', fontsize=12, fontweight='bold')
ax.set_title('Event Types Offered by Venues', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/07_event_types.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 8: Data Completeness Overview
# ============================================================================
print("\n8. Creating data completeness chart...")
fig, ax = plt.subplots(figsize=(12, 8))

completeness = {}
for col in ['name', 'phone', 'email', 'address', 'price_per_person', 'views',
            'latitude', 'longitude', 'description', 'hall_names', 'gallery_images']:
    if col in df.columns:
        non_empty = df[col].notna().sum()
        completeness[col.replace('_', ' ').title()] = (non_empty / len(df)) * 100

completeness_df = pd.Series(completeness).sort_values(ascending=True)

colors_map = ['#e74c3c' if x < 50 else '#f39c12' if x < 80 else '#2ecc71' for x in completeness_df.values]
bars = ax.barh(range(len(completeness_df)), completeness_df.values, color=colors_map,
               edgecolor='black', alpha=0.7)

ax.set_yticks(range(len(completeness_df)))
ax.set_yticklabels(completeness_df.index)
ax.set_xlabel('Completeness (%)', fontsize=12, fontweight='bold')
ax.set_xlim(0, 105)
ax.set_title('Data Completeness by Field', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3)

# Add percentage labels
for i, (bar, value) in enumerate(zip(bars, completeness_df.values)):
    ax.text(value + 1, i, f'{value:.1f}%', va='center', fontweight='bold')

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#e74c3c', label='<50% (Poor)'),
                   Patch(facecolor='#f39c12', label='50-80% (Fair)'),
                   Patch(facecolor='#2ecc71', label='>80% (Good)')]
ax.legend(handles=legend_elements, loc='lower right')

plt.tight_layout()
plt.savefig('charts/08_data_completeness.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# Chart 9: Price by Location (Box Plot)
# ============================================================================
print("\n9. Creating price by location box plot...")

# Get locations with at least 3 venues
location_price_df = df[df['price_numeric'].notna() & df['location_short'].notna()].copy()
location_counts = location_price_df['location_short'].value_counts()
top_locations = location_counts[location_counts >= 3].index[:8]

filtered_df = location_price_df[location_price_df['location_short'].isin(top_locations)]

if len(filtered_df) > 0:
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create box plot
    positions = []
    data_to_plot = []
    labels = []

    for i, loc in enumerate(top_locations):
        loc_data = filtered_df[filtered_df['location_short'] == loc]['price_numeric']
        if len(loc_data) > 0:
            data_to_plot.append(loc_data)
            positions.append(i)
            labels.append(f"{loc}\n(n={len(loc_data)})")

    bp = ax.boxplot(data_to_plot, positions=positions, patch_artist=True,
                    boxprops=dict(facecolor='#3498db', alpha=0.7),
                    medianprops=dict(color='red', linewidth=2),
                    whiskerprops=dict(linewidth=1.5),
                    capprops=dict(linewidth=1.5))

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Price per Person (AZN)', fontsize=12, fontweight='bold')
    ax.set_title('Price Distribution by Location', fontsize=14, fontweight='bold', pad=20)
    ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig('charts/09_price_by_location.png', dpi=300, bbox_inches='tight')
    plt.close()
else:
    print("   Insufficient data for location-based price analysis")

# ============================================================================
# Chart 10: Popularity Distribution (Views)
# ============================================================================
print("\n10. Creating popularity distribution chart...")
fig, ax = plt.subplots(figsize=(10, 6))

views = df['views_numeric'].dropna()
bins = [0, 10000, 25000, 50000, 100000, 200000]
labels_views = ['<10K', '10K-25K', '25K-50K', '50K-100K', '>100K']

hist_data = pd.cut(views, bins=bins, labels=labels_views).value_counts().sort_index()

colors_views = ['#ecf0f1', '#bdc3c7', '#95a5a6', '#7f8c8d', '#34495e']
bars = ax.bar(range(len(hist_data)), hist_data.values, color=colors_views,
              edgecolor='black', alpha=0.8)

ax.set_xticks(range(len(hist_data)))
ax.set_xticklabels(hist_data.index, rotation=45, ha='right')
ax.set_ylabel('Number of Venues', fontsize=12, fontweight='bold')
ax.set_title('Venue Popularity Distribution', fontsize=14, fontweight='bold', pad=20)
ax.grid(axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_popularity_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*60)
print("All charts created successfully!")
print("Charts saved in 'charts/' directory")
print("="*60)

# Generate summary statistics for README
print("\nSUMMARY STATISTICS:")
print(f"Total venues analyzed: {len(df)}")
print(f"Price range: {prices.min():.0f} - {prices.max():.0f} AZN")
print(f"Average price: {mean_price:.1f} AZN")
print(f"Most common price range: {range_counts.index[0]}")
print(f"Views range: {views.min():.0f} - {views.max():.0f}")
print(f"Average views: {views.mean():.0f}")
print(f"Most popular location: {location_counts.index[0]}")
