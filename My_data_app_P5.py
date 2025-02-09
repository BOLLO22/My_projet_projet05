from selenium import webdriver
from selenium.webdriver.chrome.service import Service # 
from selenium.webdriver.common.by import By # for locating elements
from selenium.webdriver.support.ui import WebDriverWait # for waiting for elements to load
from selenium.webdriver.support import expected_conditions as EC # for specifying the conditions to wait for
from webdriver_manager.chrome import ChromeDriverManager # for managing the chrome driver
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import streamlit as st
import time
import random



# Titre principal de l'application
st.markdown("<h1 style='text-align: center; color: white;'>Projet Numéro 05 Data Expat-Dakar</h1>", unsafe_allow_html=True)
st.markdown("""
This app allows you to scrape and analyze data on properties from Expat-Dakar
* **Python libraries:** base64, pandas, streamlit, beautifulsoup
* **Data source:** [Expat-Dakar](https://www.expat-dakar.com/).
""")

# Fonction pour scraper les données avec Selenium
def scrape_data(url, pages):
    all_data = []

    # Configuration Selenium
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled") # Contourner le blocage de Chrome
    options.add_argument("--disable-infobars") # Désactiver les infobars
    options.add_argument("--disable-extensions") # Désactiver les extensions
    options.add_argument("--start-maximized") # Démarrer en mode maximisé
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.60 Safari/537.36") # Changer l'user-agentper
    options.add_argument("--no-sandbox") # Bypass OS security model
    options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems
    options.add_argument("--disable-gpu") # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

    
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.expat-dakar.com/")  # Charger la page une première fois

    # Ajouter les cookies Cloudflare 
    cookies = [
        {"name": "cf_clearance", "value": "bbPCuf7nBpa5DtWYITvft1ujBlo86PxJTvovV21U7Yk-1739042335-1.2.1.1-vBd5Lg5koMnujMIk9N.rlzWfm1NlsAS_QOciUuakNYwHyVO1hl_yswY_N9AzwU9AWL0fyv._0jwCBKlnIun8WYZVkzKajYQVdMWxxhVQb41S77BGcyq65Lx52.vCVfkltLjfPR9Ki7MOjHYwAB.XGtx.4d.9gFLt1bnjdh7CXGPSL3.PDDoOarsYbV_sgpfXeqRN.1UiMP7BLRfuKxiTgp2ddWHbA8vH_XGBjB8pAxFBaElj7YqHAapxNrw4xU2Mbzw7GTBklURliAVIXypjOtXCAbSWRa_KXe90qPcTKLULANIL_jyZivriHASN4P4gSTMamlC24JbDdAlTEVZUwg"},
        
    ]

    for cookie in cookies:
        driver.add_cookie(cookie)

    # Recharger la page avec les cookies
    driver.get("https://www.expat-dakar.com/")
    time.sleep(5)

    # 🚀 Étape 4 : Scraper les annonces
    for page in range(1, pages + 1):
        print(f"Scraping page {page}...")

        page_url = f"{url}?page={page}"
        driver.get(page_url)
        time.sleep(random.uniform(5, 10))  

        # Récupérer les annonces
        containers = driver.find_elements(By.CLASS_NAME, "listings-cards__list-item")
        for container in  containers:
            try:
                # Récupérer le lien de l'annonce
                url_container = container.find_element(By.CLASS_NAME, "listing-card__inner").get_attribute("href")
                full_url = f"https://www.expat-dakar.com{url_container}"

                driver.get(full_url)
                time.sleep(random.uniform(3, 6))

                # Extraire les informations avec WebDriverWait pour s'assurer que les éléments sont présents
                try:
                    details = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "listing-item__header"))
                    ).text.strip()
                except:
                    details = "N/A"

                try:
                    adresse = driver.find_element(By.CLASS_NAME, "listing-item__address-location").text.strip()
                except:
                    adresse = "N/A"

                try:
                    prix = driver.find_element(By.CLASS_NAME, "listing-card__price__value 1").text.strip().replace(" F cfa", "")
                except:
                    prix = "N/A"

                try:
                    img_link = driver.find_element(By.CLASS_NAME, "gallery__image__resource vh-img").find_element(By.TAG_NAME, "img").get_attribute("src")
                except:
                    img_link = "N/A"

                # Récupérer nombre de chambres, salles de bain et superficie
                try:
                    info_list = driver.find_elements(By.CLASS_NAME, "listing-item__properties__description")
                    time.sleep(random.uniform(3, 6))
                    nombre_chambre = info_list[0].text.strip() if len(info_list) > 0 else "N/A"
                    nombre_salle_bain = info_list[1].text.strip() if len(info_list) > 1 else "N/A"
                    superficie = info_list[2].text.strip() if len(info_list) > 2 else "N/A"
                except:
                    nombre_chambre, nombre_salle_bain, superficie = "N/A", "N/A", "N/A"

                # Ajouter aux résultats
                all_data.append({
                    'Détails': details,
                    'Nombre de chambres': nombre_chambre,
                    'Nombre de salles de bain': nombre_salle_bain,
                    'Superficie': superficie,
                    'Adresse': adresse,
                    'Prix (F CFA)': prix,
                    'Image': img_link
                })

                print(f"Scrapé: {details}, {adresse}, {prix} F CFA, {nombre_chambre}, {nombre_salle_bain}, {superficie}, {img_link}")

            except Exception as e:
                print(f"Erreur lors du scraping d'une annonce : {e}")

            # Retour à la liste des annonces
            driver.get(page_url)
            time.sleep(random.uniform(2, 4))

        # Actualisation de la page toutes les 5 secondes
        print("Actualisation de la page...")
        driver.refresh()
        time.sleep(5)

    driver.quit()
    return pd.DataFrame(all_data)

# Interface utilisateur Streamlit
st.sidebar.title("Menu")

# Entrée utilisateur pour le nombre de pages
numero = st.sidebar.text_input("Entrez le nombre de pages à scraper :", "")
if numero.isdigit():
    numero = int(numero)
    st.sidebar.success(f"Vous avez entré : {numero} pages")
else:
    st.sidebar.warning("Veuillez entrer un nombre valide.")
    numero = None
# Sélection d'action
option = st.sidebar.selectbox("Choisissez une action", [
    "Scraper les données en utilisant BeautifulSoup",
    "Télécharger les données locales",
    "Tableau de bord des données",
    "Formulaire d'évaluation"
])

# Si l'utilisateur choisit de scraper
if option == "Scraper les données en utilisant BeautifulSoup" and numero is not None:
    # Définir les URLs
    urls = {
        "Appartements à louer": "https://www.expat-dakar.com/appartements-a-louer",
        "Appartements meublés": "https://www.expat-dakar.com/appartements-meubles",
        "Terrains à vendre": "https://www.expat-dakar.com/terrains-a-vendre"
    }
    # Scraper les données pour chaque URL
    with st.spinner("Veuillez patienter pendant le scraping..."):
        for title, url in urls.items():
            with st.status(f"📌 Scraping en cours pour {title}..."):
                #st.write(f"📌 **Scraping des données pour {title}...**")
                data = scrape_data(url, numero)
                
                if not data.empty:
                    st.success(f"✅ Scraping terminé pour {title} avec succès !")
                    st.dataframe(data)  # Affichage sous forme de tableau
                    # Sauvegarde CSV
                    csv_filename = f"{title.replace(' ', '_')}.csv"
                    data.to_csv(csv_filename, index=False)
                    st.download_button(label=f"📥 Télécharger {title}", data=open(csv_filename, "rb"), file_name=csv_filename, mime="text/csv")
                else:
                    st.warning(f"⚠ Aucune donnée trouvée pour {title}.")

elif option == "Télécharger les données locales":
        try:
           # Fonction de loading des données
                def load_(dataframe, title, key) :
                    st.markdown("""
                    <style>
                    div.stButton {text-align:center}
                    </style>""", unsafe_allow_html=True)

                    if st.button(title,key):
                    
                        st.subheader('Display data dimension')
                        st.write('Data dimension: ' + str(dataframe.shape[0]) + ' rows and ' + str(dataframe.shape[1]) + ' columns.')
                        st.dataframe(dataframe)

                # définir quelques styles liés aux box
                st.markdown('''<style> .stButton>button {
                    font-size: 12px;
                    height: 3em;
                    width: 25em;
                }</style>''', unsafe_allow_html=True)        
                # Charger les données 
                load_(pd.read_csv('data/appartement_louer.csv'), 'appartement à louer', '1')
                load_(pd.read_csv('data/appartements_meubles.csv'), 'appartements meublés', '2')
                load_(pd.read_csv('data/Terrain_vendre.csv'), 'Terrain à vendre', '3')
        except FileNotFoundError as e:
            st.error(f"Fichier introuvable : {e}")

elif option == "Tableau de bord des données":
        def distribution_superficie_prix(data, superficie_col, prix_col):
            # Sélectionner les 5 premiers éléments
            data_subset = data[[superficie_col, prix_col]].head(5)
            
            fig, axes = plt.subplots(1, 2, figsize=(12, 4))  # Augmenter la taille des graphiques

            # Boxplot : Distribution des prix par adresse
            sns.barplot(x=data_subset[prix_col], y=data_subset[superficie_col], ax=axes[0], palette="Set2")
            axes[0].set_title(f"diagramme en bande de {prix_col} par {prix_col} (Top 5)", fontsize=16)  # Augmenter la taille du titre
            axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha="right", fontsize=14)  # Augmenter la taille des étiquettes
            axes[0].set_yticklabels(axes[0].get_yticklabels(), fontsize=14)  # Augmenter la taille des ticks

            # Stripplot : Affichage des prix sans les regrouper
            sns.stripplot(x=data_subset[prix_col], y=data_subset[superficie_col], ax=axes[1], palette="coolwarm", size=12, jitter=True, dodge=False)
            axes[1].set_title(f"Distribution des {prix_col} par {superficie_col} (Top 5)", fontsize=16)  # Augmenter la taille du titre
            axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right", fontsize=14)  # Augmenter la taille des étiquettes
            axes[1].set_yticklabels(axes[1].get_yticklabels(), fontsize=14)  # Augmenter la taille des ticks

            plt.tight_layout()
            return fig
        
        def distribution_adresse_prix(data, Adresse_col, prix_col):
            # Sélectionner les 5 premiers éléments
            data_subset = data[[Adresse_col, prix_col]].head(5)
            
            fig1, axes = plt.subplots(1, 2, figsize=(12, 4))  # Augmenter la taille des graphiques

            # Barplot : Distribution des prix par nombre de chambres
            sns.barplot(x=data_subset[Adresse_col], y=data_subset[prix_col], ax=axes[0], palette="Set2")
            axes[0].set_title(f"Histogramme de {prix_col} par {Adresse_col} (Top 5)", fontsize=16)  # Augmenter la taille du titre
            axes[0].set_xticklabels(axes[0].get_xticklabels(), rotation=45, ha="right", fontsize=14)  # Augmenter la taille des étiquettes
            axes[0].set_yticklabels(axes[0].get_yticklabels(), fontsize=14)  # Augmenter la taille des ticks

            # Stripplot : Affichage des prix sans les regrouper
            sns.stripplot(x=data_subset[Adresse_col], y=data_subset[prix_col], ax=axes[1], palette="coolwarm", size=12, jitter=True, dodge=False)
            axes[1].set_title(f"Distribution des {prix_col} par {Adresse_col} (Top 5)", fontsize=16)  # Augmenter la taille du titre
            axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right", fontsize=14)  # Augmenter la taille des étiquettes
            axes[1].set_yticklabels(axes[1].get_yticklabels(), fontsize=14)  # Augmenter la taille des ticks

            plt.tight_layout()
            return fig1
        
        # Afficher le tableau de bord des données
        data1 = pd.read_csv('data/appartement_louer_traiter.csv')
        data2 = pd.read_csv('data/appartements_meubles_traiter.csv')
        data3 = pd.read_csv('data/Terrain_vendre_traiter.csv')
        
        st.title("Tableaux de bord des données")

        if st.button("Tableau de bord des données d'appartement à louer"):
            st.subheader("Tableau de bord appartement à louer")
            fig = distribution_superficie_prix(data1, "Superficie", "Prix")
            fig1 = distribution_adresse_prix(data1, "Adresse", "Prix")
            st.pyplot(fig)
            st.pyplot(fig1)

        if st.button("Tableau de bord des données d'appartements meublés"):
            st.subheader("Tableau de bord appartements meublés")
            fig = distribution_superficie_prix(data2, "Superficie", "Prix")
            fig1 = distribution_adresse_prix(data2, "Adresse", "Prix")
            st.pyplot(fig)
            st.pyplot(fig1)

        if st.button("Tableau de bord des données de Terrain à vendre"):
            st.subheader("Tableau de bord Terrain à vendre")
            fig = distribution_superficie_prix(data3, "Superficie", "Prix")
            st.pyplot(fig)
            
        

elif option == "Formulaire d'évaluation":
    st.markdown("### Formulaire d'évaluation")
    st.markdown("""
        <iframe src="https://ee.kobotoolbox.org/i/mwNqU5YH" width="800" height="600" style="border:none;"></iframe>
    """, unsafe_allow_html=True)

