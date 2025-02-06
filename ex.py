from tbselenium.tbdriver import TorBrowserDriver
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time 
import seaborn as sns
from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages
import os
import matplotlib.pyplot as plt

# Chemin vers le répertoire Tor Browser
TOR_BROWSER_PATH = '/home/amine/Downloads/tor-browser-linux-x86_64-13.5.2/tor-browser'

# URL cible
url = 'http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/'

# Configuration de la base de données MongoDB
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = 'PWN'
COLLECTION_NAME = 'Forums'

def insert_data(data_list):
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    # Récupérer les titres des documents existants
    existing_data = {item['title']: item for item in collection.find({}, {'title': 1})}
    
    new_data = []
    for data in data_list:
        title = data.get('title')
        if title not in existing_data:
            # Si le titre n'existe pas, ajouter les nouvelles données
            new_data.append(data)
        else:
            # Comparer les données existantes avec les nouvelles données
            existing_item = existing_data[title]
            update_fields = {}
            
            if existing_item.get('status') != data.get('status'):
                update_fields['status'] = data.get('status')
            if existing_item.get('visits') != data.get('visits'):
                update_fields['visits'] = data.get('visits')
            if existing_item.get('pub') != data.get('pub'):
                update_fields['pub'] = data.get('pub')
            
            if update_fields:
                # Mettre à jour seulement les champs modifiés
                collection.update_one({'title': title}, {'$set': update_fields})
    
    # Insérer les nouvelles données
    if new_data:
        collection.insert_many(new_data)
    
    client.close()


def generate_charts():
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    
    # Récupérer les données depuis MongoDB
    data = list(collection.find())
    
    titles = []
    visits = []
    pub_dates = []
    statuses = []
    
    for item in data:
        titles.append(item.get('title', 'N/A'))
        visit_str = item.get('visits', '0')
        try:
            visits.append(int(visit_str))
        except ValueError:
            visits.append(0)
        
        pub_str = item.get('pub', '1970-01-01 00:00:00')
        try:
            pub_dates.append(datetime.strptime(pub_str, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            pub_dates.append(datetime(1970, 1, 1))
        
        statuses.append(item.get('status', 'NOT PUBLISHED'))
    
    # Créer des tuples (visits, title) et (pub_date, title) pour trier les forums
    sorted_by_visits = sorted(zip(visits, titles), reverse=True)
    sorted_by_pub = sorted(zip(pub_dates, titles), reverse=True)
    
    # Séparer les données en deux groupes
    top_10_visits = sorted_by_visits[:10]
    last_5_pub = sorted_by_pub[:5]
    
    # Extraire les données pour les graphiques
    top_visits, top_titles_visits = zip(*top_10_visits)
   
    last_dates, last_titles_pub = zip(*last_5_pub)
  
    
    # Formatage des dates pour l'affichage
    last_dates_str = [date.strftime('%Y-%m-%d') for date in last_dates]
    
    # Style Seaborn pour des graphiques plus élégants
    sns.set(style="whitegrid")
    with PdfPages('charts.pdf') as pdf_pages:

        # Créer la première figure pour les 10 forums les plus visités
        fig1, ax1 = plt.subplots(figsize=(14, 8))
        bars_top_visits = ax1.bar(top_titles_visits, top_visits, color=sns.color_palette("Blues", 8))
        ax1.set_xlabel('Visits', fontsize=12)
        ax1.set_ylabel('Number of Visits', fontsize=12)
        ax1.set_title('Top 10 Forums with Most Visits', fontsize=14)
        ax1.set_xticks(top_titles_visits)
        ax1.set_xticklabels(top_titles_visits, rotation=10, ha='right', fontsize=10)
        pdf_pages.savefig(fig1)  # Sauvegarder la figure dans le PDF
        
        # Créer la deuxième figure avec des barres verticales pour les 5 forums les plus récemment publiés
        fig2, ax2 = plt.subplots(figsize=(14, 8))
        bars_last_pub = ax2.barh(last_titles_pub, range(len(last_dates)), color=sns.color_palette("Greens", 5))
        ax2.set_xlabel('Publication Date', fontsize=12)
        ax2.set_ylabel('Victim Title', fontsize=12)
        ax2.set_title('5 Most Recently Published Victims', fontsize=14)
        ax2.set_xticks(range(len(last_dates)))
        ax2.set_xticklabels(last_dates_str, rotation=45, ha='right', fontsize=10)
        pdf_pages.savefig(fig2)  # Sauvegarder la figure dans le PDF
        
        # Créer la troisième figure pour le pie chart des statuts
        status_counts = {status: statuses.count(status) for status in set(statuses)}
        
        fig3, ax3 = plt.subplots(figsize=(10, 10))
        wedges, texts, autotexts = ax3.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%', colors=sns.color_palette("Set2", 2))
        ax3.set_title('Forum Status Distribution', fontsize=14)
        
        # Personnaliser l'apparence des textes
        for text in texts:
            text.set_fontsize(12)
        for autotext in autotexts:
            autotext.set_fontsize(12)
        pdf_pages.savefig(fig3)  # Sauvegarder la figure dans le PDF
        # Ajuster les marges pour éviter le découpage du texte
        plt.tight_layout()
        
        # Afficher les graphiques dans des fenêtres séparées
def handle_extension(extension):
    country_extensions = {
    'dz': 'Algeria',
    'ao': 'Angola',
    'bj': 'Benin',
    'bw': 'Botswana',
    'bf': 'Burkina Faso',
    'bi': 'Burundi',
    'cm': 'Cameroon',
    'cv': 'Cape Verde',
    'cf': 'Central African Republic',
    'km': 'Comoros',
    'cg': 'Republic of the Congo',
    'cd': 'Democratic Republic of the Congo',
    'ci': 'Ivory Coast',
    'dj': 'Djibouti',
    'eg': 'Egypt',
    'er': 'Eritrea',
    'sz': 'Eswatini',
    'et': 'Ethiopia',
    'ga': 'Gabon',
    'gm': 'Gambia',
    'gh': 'Ghana',
    'gn': 'Guinea',
    'gw': 'Guinea-Bissau',
    'ke': 'Kenya',
    'ls': 'Lesotho',
    'lr': 'Liberia',
    'ly': 'Libya',
    'mg': 'Madagascar',
    'mw': 'Malawi',
    'ml': 'Mali',
    'mu': 'Mauritius',
    'mr': 'Mauritania',
    'ma': 'Morocco',
    'mz': 'Mozambique',
    'na': 'Namibia',
    'ne': 'Niger',
    'ng': 'Nigeria',
    'rw': 'Rwanda',
    'st': 'Sao Tome and Principe',
    'sn': 'Senegal',
    'sc': 'Seychelles',
    'sl': 'Sierra Leone',
    'so': 'Somalia',
    'sd': 'Sudan',
    'ss': 'South Sudan',
    'tz': 'Tanzania',
    'tg': 'Togo',
    'tn': 'Tunisia',
    'ug': 'Uganda',
    'zm': 'Zambia',
    'zw': 'Zimbabwe',
    'ag': 'Antigua and Barbuda',
    'ar': 'Argentina',
    'bs': 'Bahamas',
    'bb': 'Barbados',
    'bz': 'Belize',
    'bo': 'Bolivia',
    'br': 'Brazil',
    'ca': 'Canada',
    'cl': 'Chile',
    'co': 'Colombia',
    'cr': 'Costa Rica',
    'cu': 'Cuba',
    'dm': 'Dominica',
    'ec': 'Ecuador',
    'sv': 'El Salvador',
    'gd': 'Grenada',
    'gp': 'Guadeloupe',
    'gt': 'Guatemala',
    'gy': 'Guyana',
    'ht': 'Haiti',
    'hn': 'Honduras',
    'jm': 'Jamaica',
    'mx': 'Mexico',
    'ni': 'Nicaragua',
    'pa': 'Panama',
    'py': 'Paraguay',
    'pe': 'Peru',
    'do': 'Dominican Republic',
    'kn': 'Saint Kitts and Nevis',
    'lc': 'Saint Lucia',
    'vc': 'Saint Vincent and the Grenadines',
    'sr': 'Suriname',
    'tt': 'Trinidad and Tobago',
    'uy': 'Uruguay',
    've': 'Venezuela',
    'af': 'Afghanistan',
    'sa': 'Saudi Arabia',
    'am': 'Armenia',
    'az': 'Azerbaijan',
    'bh': 'Bahrain',
    'bd': 'Bangladesh',
    'bt': 'Bhutan',
    'bn': 'Brunei',
    'kh': 'Cambodia',
    'cn': 'China',
    'cy': 'Cyprus',
    'ge': 'Georgia',
    'in': 'India',
    'id': 'Indonesia',
    'iq': 'Iraq',
    'ir': 'Iran',
    'il': 'Israel',
    'jp': 'Japan',
    'jo': 'Jordan',
    'kz': 'Kazakhstan',
    'kw': 'Kuwait',
    'kg': 'Kyrgyzstan',
    'la': 'Laos',
    'lb': 'Lebanon',
    'my': 'Malaysia',
    'mv': 'Maldives',
    'mn': 'Mongolia',
    'mm': 'Myanmar',
    'np': 'Nepal',
    'om': 'Oman',
    'pk': 'Pakistan',
    'ps': 'Palestine',
    'ph': 'Philippines',
    'qa': 'Qatar',
    'sg': 'Singapore',
    'lk': 'Sri Lanka',
    'sy': 'Syria',
    'tj': 'Tajikistan',
    'th': 'Thailand',
    'tl': 'Timor-Leste',
    'tm': 'Turkmenistan',
    'ae': 'United Arab Emirates',
    'ye': 'Yemen',
    'al': 'Albania',
    'de': 'Germany',
    'ad': 'Andorra',
    'at': 'Austria',
    'be': 'Belgium',
    'ba': 'Bosnia and Herzegovina',
    'bg': 'Bulgaria',
    'hr': 'Croatia',
    'dk': 'Denmark',
    'es': 'Spain',
    'ee': 'Estonia',
    'fi': 'Finland',
    'fr': 'France',
    'gr': 'Greece',
    'hu': 'Hungary',
    'is': 'Iceland',
    'ie': 'Ireland',
    'it': 'Italy',
    'xk': 'Kosovo',
    'lv': 'Latvia',
    'li': 'Liechtenstein',
    'lt': 'Lithuania',
    'lu': 'Luxembourg',
    'mt': 'Malta',
    'md': 'Moldova',
    'mc': 'Monaco',
    'me': 'Montenegro',
    'no': 'Norway',
    'nl': 'Netherlands',
    'pl': 'Poland',
    'pt': 'Portugal',
    'ro': 'Romania',
    'uk': 'United Kingdom',
    'ru': 'Russia',
    'sm': 'San Marino',
    'rs': 'Serbia',
    'sk': 'Slovakia',
    'si': 'Slovenia',
    'se': 'Sweden',
    'ch': 'Switzerland',
    'tr': 'Turkey',
    'ua': 'Ukraine',
    'va': 'Vatican City',
    'au': 'Australia',
    'fj': 'Fiji',
    'ki': 'Kiribati',
    'mh': 'Marshall Islands',
    'nr': 'Nauru',
    'nc': 'New Caledonia',
    'nz': 'New Zealand',
    'pw': 'Palau',
    'pg': 'Papua New Guinea',
    'ws': 'Samoa',
    'sb': 'Solomon Islands',
    'to': 'Tonga',
    'tv': 'Tuvalu',
    'vu': 'Vanuatu'
}

    country = country_extensions.get(get_extension(extension))
    return country
def generate_country_list(title):
    countries_extensions = [
	{ "code3": "ABW", "name": "Aruba" },
	{ "code3": "AFG", "name": "Afghanistan" },
	{ "code3": "AGO", "name": "Angola" },
    { "code3": "TUV", "name": "Tuvalu" },
    { "code3": "NOR", "name": "Norway" },
    { "code3": "SRB", "name": "Serbia" },
    { "code3": "SLV", "name": "El Salvador" },
    { "code3": "SWE", "name": "Sweden" },
    { "code3": "ROU", "name": "Romania" },
    { "code3": "LBY", "name": "Libya" },
    { "code3": "POL", "name": "Poland" },
    { "code3": "NLD", "name": "Netherlands" },
    { "code3": "NZL", "name": "New Zealand" },
    { "code3": "SK", "name": "Slovakia" },
    { "code3": "THA", "name": "Thailand" },
    { "code3": "MYS", "name": "Malaysia" },
	{ "code3": "ALB", "name": "Albania" },
	{ "code3": "AND", "name": "Andorra" },
	{ "code3": "ARE", "name": "United Arab Emirates" },
	{ "code3": "ARG", "name": "Argentina" },
	{ "code3": "ARM", "name": "Armenia" },
	{ "code3": "ASM", "name": "American Samoa" },
	{ "code3": "ATG", "name": "Antigua and Barbuda" },
	{ "code3": "AUS", "name": "Australia" },
	{ "code3": "AUT", "name": "Austria" },
	{ "code3": "AZE", "name": "Azerbaijan" },
	{ "code3": "BDI", "name": "Burundi" },
	{ "code3": "BEL", "name": "Belgium" },
	{ "code3": "BEN", "name": "Benin" },
	{ "code3": "BFA", "name": "Burkina Faso" },
	{ "code3": "BGD", "name": "Bangladesh" },
	{ "code3": "BGR", "name": "Bulgaria" },
	{ "code3": "BHR", "name": "Bahrain" },
	{ "code3": "BHS", "name": "Bahamas, The" },
	{ "code3": "BIH", "name": "Bosnia and Herzegovina" },
	{ "code3": "BLR", "name": "Belarus" },
	{ "code3": "BLZ", "name": "Belize" },
	{ "code3": "BMU", "name": "Bermuda" },
	{ "code3": "BOL", "name": "Bolivia" },
	{ "code3": "BRA", "name": "Brazil" },
	{ "code3": "BRB", "name": "Barbados" },
	{ "code3": "BRN", "name": "Brunei Darussalam" },
	{ "code3": "BTN", "name": "Bhutan" },
	{ "code3": "BWA", "name": "Botswana" },
	{ "code3": "CAF", "name": "Central African Republic" },
	{ "code3": "CAN", "name": "Canada" },
	{ "code3": "CHE", "name": "Switzerland" },
	{ "code3": "CHL", "name": "Chile" },
	{ "code3": "CHN", "name": "China" },
	{ "code3": "CIV", "name": "Cote d'Ivoire" },
	{ "code3": "CMR", "name": "Cameroon" },
	{ "code3": "COD", "name": "Congo, Dem. Rep." },
	{ "code3": "COG", "name": "Congo, Rep." },
	{ "code3": "COL", "name": "Colombia" },
	{ "code3": "COM", "name": "Comoros" },
	{ "code3": "CPV", "name": "Cabo Verde" },
	{ "code3": "CRI", "name": "Costa Rica" },
	{ "code3": "CUB", "name": "Cuba" },
	{ "code3": "CUW", "name": "Curacao" },
	{ "code3": "CYM", "name": "Cayman Islands" },
	{ "code3": "CYP", "name": "Cyprus" },
	{ "code3": "CZE", "name": "Czech Republic" },
	{ "code3": "DEU", "name": "Germany" },
	{ "code3": "DJI", "name": "Djibouti" },
	{ "code3": "DMA", "name": "Dominica" },
	{ "code3": "DNK", "name": "Denmark" },
	{ "code3": "DOM", "name": "Dominican Republic" },
	{ "code3": "DZA", "name": "Algeria" },
	{ "code3": "ECU", "name": "Ecuador" },
	{ "code3": "EGY", "name": "Egypt, Arab Rep." },
	{ "code3": "ESP", "name": "Spain" },
	{ "code3": "EST", "name": "Estonia" },
	{ "code3": "ETH", "name": "Ethiopia" },
	{ "code3": "FIN", "name": "Finland" },
	{ "code3": "FJI", "name": "Fiji" },
	{ "code3": "FRA", "name": "France" },
	{ "code3": "FRO", "name": "Faroe Islands" },
	{ "code3": "FSM", "name": "Micronesia, Fed. Sts." },
	{ "code3": "GAB", "name": "Gabon" },
	{ "code3": "GBR", "name": "United Kingdom" },
	{ "code3": "GEO", "name": "Georgia" },
	{ "code3": "GHA", "name": "Ghana" },
	{ "code3": "GIB", "name": "Gibraltar" },
	{ "code3": "GIN", "name": "Guinea" },
	{ "code3": "GMB", "name": "Gambia, The" },
	{ "code3": "GNB", "name": "Guinea-Bissau" },
	{ "code3": "GNQ", "name": "Equatorial Guinea" },
	{ "code3": "GRC", "name": "Greece" },
	{ "code3": "GRD", "name": "Grenada" },
	{ "code3": "GRL", "name": "Greenland" },
	{ "code3": "GTM", "name": "Guatemala" },
	{ "code3": "GUM", "name": "Guam" },
	{ "code3": "GUY", "name": "Guyana" },
	{ "code3": "HKG", "name": "Hong Kong SAR, China" },
	{ "code3": "HND", "name": "Honduras" },
	{ "code3": "HRV", "name": "Croatia" },
	{ "code3": "HTI", "name": "Haiti" },
	{ "code3": "HUN", "name": "Hungary" },
	{ "code3": "IDN", "name": "Indonesia" },
	{ "code3": "IMN", "name": "Isle of Man" },
	{ "code3": "IND", "name": "India" },
	{ "code3": "IRL", "name": "Ireland" },
	{ "code3": "IRN", "name": "Iran, Islamic Rep." },
	{ "code3": "IRQ", "name": "Iraq" },
	{ "code3": "ISL", "name": "Iceland" },
	{ "code3": "ISR", "name": "Israel" },
	{ "code3": "ITA", "name": "Italy" },
	{ "code3": "JAM", "name": "Jamaica" },
	{ "code3": "JOR", "name": "Jordan" },
	{ "code3": "JPN", "name": "Japan" },
	{ "code3": "KAZ", "name": "Kazakhstan" },
	{ "code3": "KEN", "name": "Kenya" },
	{ "code3": "KGZ", "name": "Kyrgyz Republic" },
	{ "code3": "KHM", "name": "Cambodia" }
    ]
    countries = [country for country in countries_extensions if country['name'] == title]
    
    if not countries:
        print(f"No country found with the name: {title}")
    else:
        return countries[0]['code3']


   
def get_extension(title):
    # Supposer que le titre est du type 'example.com' ou 'example.co.uk'
    if '.' in title:
        return title.split('.')[-1]
    return None

def main():
    with TorBrowserDriver(TOR_BROWSER_PATH) as driver:
        driver.get(url)
        page_source = driver.page_source

        soup = BeautifulSoup(page_source, 'html.parser')

        elements = soup.find_all('div', class_='col-12 col-md-6 col-lg-4')

        data_list = []

        for element in elements:
            # Extraire le titre
            title_div = element.find('div', class_='card-title text-center')
            title = title_div.get_text(strip=True) if title_div else 'N/A'

            # Extraire le statut
            status_p = element.find('p', class_='text-center')
            if status_p and status_p.find('strong'):
                status_text = status_p.find('strong').get_text(strip=True)
                status = 'PUBLISHED' if 'PUBLISHED' in status_text else 'NOT PUBLISHED'
            else:
                status = 'NOT PUBLISHED'

            # Extraire les détails
            details_p = element.find_all('p')
            if len(details_p) >= 2:
                visits = details_p[1].get_text(strip=True).split(': ')[1][:-9] if 'Visits' in details_p[1].get_text() else 'N/A'
                data_size = details_p[1].get_text(strip=True).split(': ')[2][:-8] if 'Data Size' in details_p[1].get_text() else 'N/A'
                last_view = details_p[1].get_text(strip=True).split(': ')[3] if 'Last View' in details_p[1].get_text() else 'N/A'
            else:
                visits = data_size = last_view = 'N/A'

            # Extraire le contenu de card-footer
            footer_div = element.find('div', class_='card-footer')
            pub = footer_div.get_text(strip=True) if footer_div else 'N/A'
            index_anchor = element.find('a', class_='index-anchor')
            if index_anchor and 'href' in index_anchor.attrs:
                href = index_anchor['href']
                full_url = f"http://ransomxifxwc5eteopdobynonjctkxxvap77yqifu2emfbecgbqdw6qd.onion/{href.lstrip('/')}"
            
            x = handle_extension(title)
            code3=generate_country_list(x)

                    
                # Préparer les données pour MongoDB
            data = {
                    'title': title,
                    'status': status,
                    'visits': visits,
                    'data_size': data_size,
                    'last_view': last_view,
                    'pub': pub,
                    'full_url': full_url,
                    'country':x,
                    'code3':code3
                }
                
            

            data_list.append(data)

        # Insérer les données dans MongoDB
        insert_data(data_list)
        print("Données insérées dans MongoDB.")
    os.chdir('/home/amine/pwn6')
    generate_charts()

if __name__ == "__main__":
    main()