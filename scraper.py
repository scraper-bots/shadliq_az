import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
import json

class ShadliqScraper:
    def __init__(self):
        self.base_url = "https://shadliq.az"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.venues = []

    def scrape_listing_page(self, page_num):
        """Scrape a single listing page to get venue URLs and basic info"""
        url = f"{self.base_url}/az/saray-restoranlar/{page_num}/"
        print(f"Scraping listing page {page_num}: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all venue cards/listings
            # Looking for venue links - they typically have patterns like /az/venue-name
            venue_links = []

            # Try multiple selectors to find venue links
            # Check for article links, card links, or venue-specific patterns
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                # Filter for venue detail pages (exclude category, filter, and pagination links)
                if '/az/' in href and href.count('/') >= 3 and not any(x in href for x in ['/saray-restoranlar/', '/page/', '/category/', '?']):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in venue_links and full_url.startswith(self.base_url):
                        venue_links.append(full_url)

            # Alternative: look for specific card containers
            cards = soup.find_all(['article', 'div'], class_=re.compile(r'(card|venue|item|listing|post)', re.I))
            for card in cards:
                link = card.find('a', href=True)
                if link:
                    href = link.get('href', '')
                    if '/az/' in href and href.count('/') >= 3:
                        full_url = urljoin(self.base_url, href)
                        if full_url not in venue_links and full_url.startswith(self.base_url):
                            venue_links.append(full_url)

            print(f"  Found {len(venue_links)} venue links on page {page_num}")
            return venue_links

        except Exception as e:
            print(f"  Error scraping listing page {page_num}: {e}")
            return []

    def extract_text(self, element, default=""):
        """Safely extract text from an element"""
        if element:
            return element.get_text(strip=True)
        return default

    def extract_coordinate(self, soup, coord_type):
        """Extract latitude or longitude from script or meta tags"""
        try:
            # Look in script tags for coordinate data
            for script in soup.find_all('script'):
                if script.string and coord_type in script.string:
                    # Try to find coordinate value
                    pattern = f'{coord_type}["\']?\s*:\s*([0-9.]+)'
                    match = re.search(pattern, script.string)
                    if match:
                        return match.group(1)
        except:
            pass
        return ""

    def scrape_venue_detail(self, url):
        """Scrape detailed information from a venue page"""
        print(f"  Scraping venue: {url}")

        venue_data = {
            'url': url,
            'name': '',
            'phone': '',
            'email': '',
            'address': '',
            'latitude': '',
            'longitude': '',
            'price_per_person': '',
            'capacity_min': '',
            'capacity_max': '',
            'views': '',
            'description': '',
            'services': '',
            'event_types': '',
            'gallery_images': '',
            'working_hours': '',
            'website': '',
            'social_media': '',
            'menu_types': '',
            'parking': '',
            'indoor_outdoor': '',
            'additional_info': ''
        }

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract venue name from title or h1
            title = soup.find('h1')
            if title:
                venue_data['name'] = self.extract_text(title)
            else:
                # Fallback to page title
                page_title = soup.find('title')
                if page_title:
                    venue_data['name'] = self.extract_text(page_title).split('|')[0].strip()

            # Extract phone numbers
            phone_links = soup.find_all('a', href=re.compile(r'tel:'))
            phones = [link.get('href').replace('tel:', '') for link in phone_links]
            venue_data['phone'] = ', '.join(phones) if phones else ''

            # Also look for phone patterns in text
            if not venue_data['phone']:
                phone_pattern = r'(\+?994|0)[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}'
                phone_matches = re.findall(phone_pattern, soup.get_text())
                if phone_matches:
                    venue_data['phone'] = ', '.join(set(phone_matches))

            # Extract email
            email_links = soup.find_all('a', href=re.compile(r'mailto:'))
            emails = [link.get('href').replace('mailto:', '') for link in email_links]
            venue_data['email'] = ', '.join(emails) if emails else ''

            # Also look for email patterns in text
            if not venue_data['email']:
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                email_matches = re.findall(email_pattern, soup.get_text())
                if email_matches:
                    venue_data['email'] = ', '.join(set(email_matches))

            # Extract address
            address_elem = soup.find(['span', 'div', 'p'], class_=re.compile(r'address|location', re.I))
            if address_elem:
                venue_data['address'] = self.extract_text(address_elem)

            # Look for address in schema.org markup
            if not venue_data['address']:
                schema_address = soup.find(['span', 'div'], itemprop='address')
                if schema_address:
                    venue_data['address'] = self.extract_text(schema_address)

            # Extract coordinates from Yandex Maps or other map services
            venue_data['latitude'] = self.extract_coordinate(soup, 'latitude')
            venue_data['longitude'] = self.extract_coordinate(soup, 'longitude')

            # Alternative coordinate extraction from ymaps or map containers
            if not venue_data['latitude']:
                for script in soup.find_all('script'):
                    if script.string and 'ymaps' in script.string:
                        coord_pattern = r'\[([0-9.]+),\s*([0-9.]+)\]'
                        matches = re.findall(coord_pattern, script.string)
                        if matches:
                            venue_data['latitude'] = matches[0][0]
                            venue_data['longitude'] = matches[0][1]
                            break

            # Extract price per person
            price_pattern = r'(\d+)\s*(?:AZN|₼|manat)'
            price_elems = soup.find_all(text=re.compile(price_pattern, re.I))
            for elem in price_elems:
                match = re.search(price_pattern, elem, re.I)
                if match:
                    venue_data['price_per_person'] = match.group(1)
                    break

            # Extract capacity
            capacity_pattern = r'(\d+)\s*[-–]\s*(\d+)\s*(?:nəfər|person|guest)'
            capacity_text = soup.get_text()
            capacity_match = re.search(capacity_pattern, capacity_text, re.I)
            if capacity_match:
                venue_data['capacity_min'] = capacity_match.group(1)
                venue_data['capacity_max'] = capacity_match.group(2)

            # Extract views/visitor count
            views_elem = soup.find(text=re.compile(r'\d+\s*(?:baxış|views|customer)', re.I))
            if views_elem:
                views_match = re.search(r'(\d+)', views_elem)
                if views_match:
                    venue_data['views'] = views_match.group(1)

            # Extract description
            desc_elem = soup.find(['div', 'section'], class_=re.compile(r'description|content|about', re.I))
            if desc_elem:
                venue_data['description'] = self.extract_text(desc_elem)[:500]  # Limit length

            # Extract services/amenities
            services = []
            service_lists = soup.find_all(['ul', 'div'], class_=re.compile(r'service|amenity|feature', re.I))
            for service_list in service_lists:
                items = service_list.find_all(['li', 'span', 'div'])
                services.extend([self.extract_text(item) for item in items if self.extract_text(item)])
            venue_data['services'] = '; '.join(services[:20])  # Limit to 20 services

            # Extract event types
            events = []
            event_elems = soup.find_all(text=re.compile(r'toy|nişan|ad günü|wedding|engagement', re.I))
            for elem in event_elems[:10]:
                text = elem.strip()
                if text and len(text) < 50:
                    events.append(text)
            venue_data['event_types'] = '; '.join(set(events))

            # Extract gallery images
            images = []
            for img in soup.find_all('img', src=True):
                src = img.get('src', '')
                if src and ('upload' in src or 'gallery' in src or 'wp-content' in src):
                    full_img_url = urljoin(self.base_url, src)
                    images.append(full_img_url)
            venue_data['gallery_images'] = '; '.join(images[:10])  # Limit to 10 images

            # Extract working hours
            hours_elem = soup.find(text=re.compile(r'iş saatı|working hour|açıq', re.I))
            if hours_elem:
                venue_data['working_hours'] = hours_elem.strip()[:100]

            # Extract website if different from main URL
            website_links = soup.find_all('a', href=re.compile(r'http'))
            for link in website_links:
                href = link.get('href', '')
                if href and self.base_url not in href and any(x in href.lower() for x in ['www', 'http']):
                    venue_data['website'] = href
                    break

            # Extract social media
            social = []
            social_patterns = ['facebook', 'instagram', 'twitter', 'youtube', 'linkedin']
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                for pattern in social_patterns:
                    if pattern in href.lower():
                        social.append(href)
                        break
            venue_data['social_media'] = '; '.join(social[:5])

            # Extract additional structured data
            for meta in soup.find_all('meta'):
                property_val = meta.get('property', '')
                if 'og:' in property_val or 'article:' in property_val:
                    content = meta.get('content', '')
                    if content and not venue_data['description']:
                        venue_data['description'] = content[:500]

            time.sleep(1)  # Be polite to the server
            return venue_data

        except Exception as e:
            print(f"    Error scraping venue {url}: {e}")
            return venue_data

    def scrape_all(self):
        """Main method to scrape all pages and venues"""
        print("Starting scraper...")
        print("=" * 60)

        # Step 1: Scrape all listing pages (1-5)
        all_venue_urls = []
        for page_num in range(1, 6):
            venue_urls = self.scrape_listing_page(page_num)
            all_venue_urls.extend(venue_urls)
            time.sleep(2)  # Be polite between pages

        # Remove duplicates
        all_venue_urls = list(set(all_venue_urls))
        print("\n" + "=" * 60)
        print(f"Total unique venues found: {len(all_venue_urls)}")
        print("=" * 60 + "\n")

        # Step 2: Scrape each venue detail page
        for i, url in enumerate(all_venue_urls, 1):
            print(f"[{i}/{len(all_venue_urls)}]", end=" ")
            venue_data = self.scrape_venue_detail(url)
            self.venues.append(venue_data)

            # Save progress every 10 venues
            if i % 10 == 0:
                self.save_to_csv('shadliq_venues_progress.csv')
                print(f"  Progress saved ({i} venues scraped)")

        print("\n" + "=" * 60)
        print(f"Scraping completed! Total venues scraped: {len(self.venues)}")
        print("=" * 60)

    def save_to_csv(self, filename='shadliq_venues.csv'):
        """Save scraped data to CSV file"""
        if not self.venues:
            print("No data to save!")
            return

        print(f"\nSaving data to {filename}...")

        # Get all unique keys from all venues
        all_keys = set()
        for venue in self.venues:
            all_keys.update(venue.keys())

        fieldnames = sorted(list(all_keys))

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.venues)

        print(f"Data saved successfully! {len(self.venues)} venues written to {filename}")

        # Print summary statistics
        print("\nData Summary:")
        print(f"  - Total venues: {len(self.venues)}")
        print(f"  - Venues with phone: {sum(1 for v in self.venues if v.get('phone'))}")
        print(f"  - Venues with email: {sum(1 for v in self.venues if v.get('email'))}")
        print(f"  - Venues with address: {sum(1 for v in self.venues if v.get('address'))}")
        print(f"  - Venues with coordinates: {sum(1 for v in self.venues if v.get('latitude'))}")
        print(f"  - Venues with price: {sum(1 for v in self.venues if v.get('price_per_person'))}")

if __name__ == "__main__":
    scraper = ShadliqScraper()
    scraper.scrape_all()
    scraper.save_to_csv('shadliq_venues_final.csv')
