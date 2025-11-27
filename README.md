# Shadliq.az Web Scraper

## Overview
This project scrapes event venue data from https://shadliq.az, a comprehensive directory of wedding halls and restaurants in Baku, Azerbaijan.

## Data Collected

Successfully scraped **99 venues** from all 5 listing pages with the following data fields:

### Field Completeness

| Field | Completeness | Notes |
|-------|--------------|-------|
| URL | 100% (99/99) | ✓ Complete |
| Name | 100% (99/99) | ✓ Complete |
| Phone | 98% (98/99) | ✓ Nearly complete |
| Email | 0% (0/99) | Most venues don't publish email |
| Address | 98% (98/99) | ✓ Nearly complete |
| Location Short | 69% (69/99) | District/area reference |
| Latitude | 100% (99/99) | ✓ Complete from JS data |
| Longitude | 100% (99/99) | ✓ Complete from JS data |
| Price per Person | 68% (68/99) | Many venues don't list prices |
| Views | 100% (99/99) | ✓ Complete |
| Description | 81% (81/99) | Good coverage |
| Hall Names | 67% (67/99) | Available when venues list their halls |
| Services | 100% (99/99) | ✓ Complete |
| Event Types | 100% (99/99) | ✓ Complete |
| Gallery Images | 100% (99/99) | ✓ Complete |
| Meta Description | 100% (99/99) | ✓ Complete |

## Files

- `scraper_final.py` - Main scraper script (recommended)
- `shadliq_venues_complete.csv` - Final output with all 99 venues
- `requirements.txt` - Python dependencies
- `README.md` - This file

## How to Use

### Installation

```bash
pip install -r requirements.txt
```

### Running the Scraper

```bash
python scraper_final.py
```

The scraper will:
1. Scrape all 5 listing pages to collect venue URLs and prices
2. Visit each venue detail page to extract comprehensive information
3. Save progress every 10 venues
4. Output final data to `shadliq_venues_complete.csv`

### Scraping Strategy

The scraper uses a two-phase approach:

**Phase 1: Listing Pages**
- Scrapes pages 1-5 of venue listings
- Extracts: venue URL, price per person, short location
- Stores this data for later merging

**Phase 2: Detail Pages**
- Visits each venue's detail page
- Extracts: name, phone, email, full address, coordinates, views, description, halls, services, event types, gallery images
- Merges with listing page data
- Outputs complete venue profile

### Data Extraction Details

- **Coordinates**: Extracted from JavaScript `ae_globals` variable
- **Views**: From "Müştəri Baxış Sayı" (customer view count)
- **Price**: Extracted from listing page cards (many venues don't publish prices)
- **Address**: From map marker `<i class="fa-map-marker">` element
- **Gallery**: High-resolution images (converted from thumbnails)

## Sample Data

```
Venue: Altun Restoran
URL: https://shadliq.az/az/altun-sadliq-sarayi
Phone: 055-270-06-00
Address: 8 km, M. Əliyev küç. 9B
Price: 50 AZN
Location: 8 km
Coordinates: (40.4092616, 49.8670924)
Views: 172,889
Event types: Ad günü, Nişan, Toy, Xına
```

## Notes

- The scraper includes 1.5-2 second delays between requests to be polite to the server
- Progress is saved every 10 venues to prevent data loss
- Some venues don't publish prices or emails - this is expected
- Email addresses are rarely published (0/99 venues)
- All coordinates are successfully extracted from JavaScript

## Analysis Ready

The data is now ready for analysis including:
- Price analysis by location
- Venue capacity studies
- Geographic distribution mapping
- Popularity analysis (views)
- Event type categorization
- Image collection for ML/computer vision tasks

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml
