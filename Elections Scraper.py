"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Jakub Roman
email: jakubromans@gmail.com
"""

import requests
from bs4 import BeautifulSoup
import csv
import argparse
import urllib.parse

MAIN_URL = "https://volby.cz/pls/ps2017nss/"

def get_data_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = []
    
    table = soup.find('table', {'class': 'list'})
    if not table:
        return []
    
    rows = table.find_all('tr')[2:]
    
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 7:
            continue
            
        obce_code = cols[0].text.strip()
        obce_name = cols[1].text.strip()
        voters = int(cols[2].text.replace('\xa0', '').replace(' ', ''))
        ballots = int(cols[3].text.replace('\xa0', '').replace(' ', ''))
        valid_votes = int(cols[4].text.replace('\xa0', '').replace(' ', ''))
        
        parties_data = {}
        for party_col in cols[5:]:
            party_text = party_col.text.strip()
            if party_text:
                parts = party_text.split()
                party_name = ' '.join(parts[:-1])
                party_votes = int(parts[-1].replace('\xa0', '').replace(' ', ''))
                parties_data[party_name] = party_votes
        
        data.append({
            'Kód obce': obce_code,
            'Název obce': obce_name,
            'Voliči v seznamu': voters,
            'Vydané obálky': ballots,
            'Platné hlasy': valid_votes,
            'Strany': parties_data
        })
    return data

def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Kód obce', 'Název obce', 'Voliči v seznamu', 'Vydané obálky', 'Platné hlasy', 'Strany'])
        writer.writeheader()
        for row in data:
            row['Strany'] = str(row['Strany'])
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(description="Scraper pro výsledky voleb")
    parser.add_argument("relative_url", help="Relativní URL stránky územního celku")
    parser.add_argument("output", help="Název výstupního souboru")
    args = parser.parse_args()
    
    full_url = urllib.parse.urljoin(MAIN_URL, args.relative_url)
    
    try:
        html = get_data_from_url(full_url)
        results = parse_results(html)
        save_to_csv(results, args.output)
        print(f"Data byla úspěšně uložena do souboru {args.output}")
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování stránky: {e}")
    except Exception as e:
        print(f"Chyba při zpracování dat: {e}")

if __name__ == "__main__":
    main()
