import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
import json

class ShadliqScraperV2:
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

            venue_links = []

            # Find venue links from articles/cards
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                # Filter for venue detail pages
                if '/az/' in href and href.count('/') >= 3 and not any(x in href for x in ['/saray-restoranlar/', '/page/', '/category/', '?', '#']):
                    full_url = urljoin(self.base_url, href)
                    if full_url not in venue_links and full_url.startswith(self.base_url):
                        # Exclude non-venue pages
                        excluded_keywords = ['elaqe', 'videolar', 'meslehetler', 'gelinlikler', 'gozellik-salonlari', 'toy-masini', 'dekorasiya-dizayn', 'reqs-qruplari']
                        if not any(keyword in full_url for keyword in excluded_keywords):
                            venue_links.append(full_url)

            # Remove duplicates
            venue_links = list(dict.fromkeys(venue_links))

            print(f"  Found {len(venue_links)} venue links on page {page_num}")
            return venue_links

        except Exception as e:
            print(f"  Error scraping listing page {page_num}: {e}")
            return []

    def extract_text_safe(self, element, default=""):
        """Safely extract text from an element"""
        if element:
            return element.get_text(strip=True)
        return default

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
            'views': '',
            'description': '',
            'hall_names': '',
            'services': '',
            'event_types': '',
            'gallery_images': '',
            'meta_description': ''
        }

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # 1. Extract venue name from H1
            h1 = soup.find('h1')
            if h1:
                venue_data['name'] = self.extract_text_safe(h1)

            # 2. Extract phone - look specifically in address_info section
            phone_links = soup.find_all('a', href=re.compile(r'tel:'))
            phones = set()
            for link in phone_links:
                phone = link.get('href', '').replace('tel:', '').strip()
                if phone and len(phone) > 5:  # Valid phone number
                    phones.add(phone)
            venue_data['phone'] = ', '.join(sorted(phones))

            # 3. Extract email
            email_links = soup.find_all('a', href=re.compile(r'mailto:'))
            emails = set()
            for link in email_links:
                email = link.get('href', '').replace('mailto:', '').replace('/cdn-cgi/l/email-protection#', '').strip()
                if email and '@' in email:
                    emails.add(email)
            venue_data['email'] = ', '.join(sorted(emails))

            # 4. Extract address - look for map marker icon
            address_p = soup.find('i', class_='fa-map-marker')
            if address_p and address_p.parent:
                # Get parent paragraph and extract just the address text
                parent_text = address_p.parent.get_text(strip=True)
                # Remove the icon and clean up
                address = parent_text.strip()
                # Remove "Müştəri Baxış Sayı" and any numbers after it
                address = re.sub(r'Müştəri\s+Baxış\s+Sayı.*', '', address).strip()
                # Remove phone numbers
                address = re.sub(r'(\+?994|0)[-\s]?\d{2}[-\s]?\d{3}[-\s]?\d{2}[-\s]?\d{2}', '', address).strip()
                venue_data['address'] = address

            # 5. Extract coordinates from JavaScript ae_globals
            for script in soup.find_all('script'):
                if script.string and 'ae_globals' in script.string:
                    lat_match = re.search(r"'latitude'\s*:\s*'([^']+)'", script.string)
                    lon_match = re.search(r"'longitude'\s*:\s*'([^']+)'", script.string)
                    if lat_match:
                        venue_data['latitude'] = lat_match.group(1)
                    if lon_match:
                        venue_data['longitude'] = lon_match.group(1)
                    break

            # 6. Extract views - look for strong tag with number
            view_p = soup.find('p', text=re.compile(r'Müştəri\s+Baxış\s+Sayı', re.IGNORECASE))
            if view_p:
                strong = view_p.find('strong')
                if strong:
                    venue_data['views'] = self.extract_text_safe(strong)

            # 7. Extract price - look in specific price sections
            # Try to find the venue's actual price, not related venues
            price_found = False

            # First try: Look in address_info section (most reliable)
            address_info = soup.find('div', class_='address_info')
            if address_info:
                price_text = address_info.get_text()
                price_match = re.search(r'(\d+)\s*(?:AZN|azn|₼)', price_text)
                if price_match:
                    venue_data['price_per_person'] = price_match.group(1)
                    price_found = True

            # Second try: Look in title or meta
            if not price_found:
                title = soup.find('title')
                if title:
                    title_text = title.get_text()
                    # Look for price pattern in title
                    price_match = re.search(r'(\d+)\s*(?:AZN|azn|₼)', title_text)
                    if price_match:
                        venue_data['price_per_person'] = price_match.group(1)

            # 8. Extract hall names - look for text after "ZALLAR" or similar
            page_text = soup.get_text()
            hall_pattern = r'ZALLAR[:\s]*([^\n]+(?:\n[^\n]+){0,3})'
            hall_match = re.search(hall_pattern, page_text, re.MULTILINE)
            if hall_match:
                halls = hall_match.group(1).strip()
                # Clean up hall names
                halls = re.sub(r'TƏDBİRLƏR.*', '', halls).strip()
                halls = re.sub(r'\.+', ', ', halls).strip()
                venue_data['hall_names'] = halls[:200]

            # 9. Extract event types - look for specific keywords
            events = set()
            event_keywords = ['Toy', 'Nişan', 'Xına', 'Ad günü', 'wedding', 'engagement']
            for keyword in event_keywords:
                if re.search(keyword, page_text, re.IGNORECASE):
                    events.add(keyword)
            venue_data['event_types'] = ', '.join(sorted(events))

            # 10. Extract description from meta tag
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                venue_data['meta_description'] = meta_desc.get('content', '')[:500]

            # 11. Extract main description/content
            # Look for main content paragraphs that aren't navigation or footer
            content_div = soup.find('div', class_=re.compile('single-detail|content|description'))
            if content_div:
                # Get paragraphs with actual content
                paragraphs = content_div.find_all('p', limit=5)
                desc_parts = []
                for p in paragraphs:
                    text = self.extract_text_safe(p)
                    # Skip if it's address, phone, or views
                    if text and len(text) > 20 and not re.search(r'(Müştəri|Baxış|tel:|@)', text):
                        desc_parts.append(text)
                venue_data['description'] = ' | '.join(desc_parts[:3])[:500]

            # 12. Extract services/amenities - look for lists in content area
            services = []
            service_lists = soup.find_all('ul', class_=re.compile('service|amenity|feature'))
            for ul in service_lists[:2]:  # Limit to first 2 lists
                items = ul.find_all('li')
                for item in items[:10]:  # Limit items per list
                    text = self.extract_text_safe(item)
                    if text and len(text) < 100:  # Reasonable length for a service item
                        services.append(text)
            venue_data['services'] = '; '.join(services[:15])

            # 13. Extract gallery images
            images = []
            # Look for gallery or carousel images
            gallery = soup.find(['div', 'section'], class_=re.compile('gallery|carousel'))
            if gallery:
                imgs = gallery.find_all('img', src=True)
                for img in imgs[:15]:  # Limit to 15 images
                    src = img.get('src', '')
                    if src and 'upload' in src:
                        full_img_url = urljoin(self.base_url, src)
                        # Get high-res version if it's a thumbnail
                        full_img_url = full_img_url.replace('/thumbs/', '/').replace('-270.jpg', '-1200.jpg')
                        images.append(full_img_url)

            # Also check for featured images
            if not images:
                imgs = soup.find_all('img', src=re.compile('upload'))
                for img in imgs[:15]:
                    src = img.get('src', '')
                    full_img_url = urljoin(self.base_url, src)
                    full_img_url = full_img_url.replace('/thumbs/', '/').replace('-270.jpg', '-1200.jpg')
                    if full_img_url not in images:
                        images.append(full_img_url)

            venue_data['gallery_images'] = '; '.join(list(dict.fromkeys(images)))  # Remove duplicates

            time.sleep(1.5)  # Be polite to the server
            return venue_data

        except Exception as e:
            print(f"    Error scraping venue {url}: {e}")
            return venue_data

    def scrape_all(self):
        """Main method to scrape all pages and venues"""
        print("Starting improved scraper V2...")
        print("=" * 60)

        # Step 1: Scrape all listing pages (1-5)
        all_venue_urls = []
        for page_num in range(1, 6):
            venue_urls = self.scrape_listing_page(page_num)
            all_venue_urls.extend(venue_urls)
            time.sleep(2)

        # Remove duplicates
        all_venue_urls = list(dict.fromkeys(all_venue_urls))
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
                self.save_to_csv('shadliq_venues_v2_progress.csv')
                print(f"  Progress saved ({i} venues scraped)")

        print("\n" + "=" * 60)
        print(f"Scraping completed! Total venues scraped: {len(self.venues)}")
        print("=" * 60)

    def save_to_csv(self, filename='shadliq_venues_v2.csv'):
        """Save scraped data to CSV file"""
        if not self.venues:
            print("No data to save!")
            return

        print(f"\nSaving data to {filename}...")

        fieldnames = [
            'url', 'name', 'phone', 'email', 'address', 'latitude', 'longitude',
            'price_per_person', 'views', 'description', 'hall_names', 'services',
            'event_types', 'gallery_images', 'meta_description'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.venues)

        print(f"Data saved successfully! {len(self.venues)} venues written to {filename}")

        # Print summary statistics
        print("\nData Summary:")
        print(f"  - Total venues: {len(self.venues)}")
        print(f"  - Venues with name: {sum(1 for v in self.venues if v.get('name'))}")
        print(f"  - Venues with phone: {sum(1 for v in self.venues if v.get('phone'))}")
        print(f"  - Venues with email: {sum(1 for v in self.venues if v.get('email'))}")
        print(f"  - Venues with address: {sum(1 for v in self.venues if v.get('address'))}")
        print(f"  - Venues with coordinates: {sum(1 for v in self.venues if v.get('latitude'))}")
        print(f"  - Venues with price: {sum(1 for v in self.venues if v.get('price_per_person'))}")
        print(f"  - Venues with views: {sum(1 for v in self.venues if v.get('views'))}")
        print(f"  - Venues with gallery: {sum(1 for v in self.venues if v.get('gallery_images'))}")

if __name__ == "__main__":
    scraper = ShadliqScraperV2()
    scraper.scrape_all()
    scraper.save_to_csv('shadliq_venues_v2_final.csv')
