import requests
from bs4 import BeautifulSoup
import re
import json

url = "https://shadliq.az/az/neolit-hall-sadliq-sarayi"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("=" * 60)
print("HTML STRUCTURE ANALYSIS")
print("=" * 60)

# Find all sections/divs with specific data
print("\n1. PHONE NUMBERS:")
phone_links = soup.find_all('a', href=re.compile(r'tel:'))
for link in phone_links:
    print(f"  - {link.get('href')} -> Text: {link.get_text(strip=True)}")

print("\n2. EMAIL:")
email_links = soup.find_all('a', href=re.compile(r'mailto:'))
for link in email_links:
    print(f"  - {link.get('href')} -> Text: {link.get_text(strip=True)}")

print("\n3. ADDRESS:")
# Look for common address patterns
for tag in soup.find_all(['p', 'span', 'div', 'address']):
    text = tag.get_text(strip=True)
    if re.search(r'(mkr|km|prospekt|küçəsi|rayon)', text, re.I) and len(text) < 100:
        print(f"  - {text[:80]}")

print("\n4. VIEW COUNT:")
view_strong = soup.find('strong', text=re.compile(r'\d{4,}'))
if view_strong:
    print(f"  - Views: {view_strong.get_text(strip=True)}")
    print(f"  - Parent: {view_strong.parent}")

print("\n5. PRICE:")
for tag in soup.find_all(['span', 'div', 'p']):
    text = tag.get_text(strip=True)
    if re.search(r'\d+\s*(?:AZN|azn|₼)', text) and len(text) < 50:
        print(f"  - {text}")

print("\n6. JAVASCRIPT DATA (ae_globals):")
for script in soup.find_all('script'):
    if script.string and 'ae_globals' in script.string:
        # Extract latitude/longitude
        lat_match = re.search(r"'latitude':'([^']+)'", script.string)
        lon_match = re.search(r"'longitude':'([^']+)'", script.string)
        if lat_match and lon_match:
            print(f"  - Latitude: {lat_match.group(1)}")
            print(f"  - Longitude: {lon_match.group(1)}")

print("\n7. ALL UNIQUE CLASSES (first 30):")
classes = set()
for tag in soup.find_all(True):
    if tag.get('class'):
        for cls in tag.get('class'):
            classes.add(cls)

for i, cls in enumerate(sorted(classes)[:30]):
    print(f"  - {cls}")

print("\n8. MAIN CONTENT CONTAINERS:")
main_containers = soup.find_all(['div', 'section'], class_=re.compile(r'content|main|post|detail', re.I))
for container in main_containers[:5]:
    classes = ' '.join(container.get('class', []))
    print(f"  - Tag: {container.name}, Classes: {classes}")

print("\n9. TITLE/HEADING:")
h1 = soup.find('h1')
if h1:
    print(f"  - H1: {h1.get_text(strip=True)}")
title = soup.find('title')
if title:
    print(f"  - Title: {title.get_text(strip=True)}")

print("\n10. META DESCRIPTION:")
meta_desc = soup.find('meta', {'name': 'description'})
if meta_desc:
    print(f"  - {meta_desc.get('content', '')[:200]}")

print("\n" + "=" * 60)
