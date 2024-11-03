import requests, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

api_key_vagalume = os.getenv("KEY_VAGALUME")

def get_lyrics():
    lyrics_list = []
    with open('musicas.csv', 'r') as input_musics:
        for line in input_musics.readlines():
            music, artist_uf = line.split(';')
            artist = artist_uf.replace('\n', '')
            local_lyric = get_lyric_local(music, artist)
            if local_lyric:
                lyrics_list.append(local_lyric)
            else:
                api_lyric = get_lyrics_on_vagalume_api(music, artist)
                if api_lyric:
                    lyrics_list.append(api_lyric)
                else:
                    scrapping_lyric = get_lyric_by_scraping(music, artist)
                    if scrapping_lyric:
                        lyrics_list.append(scrapping_lyric)
                    else:
                        lyrics_list.append(f'Música {music} do artista {artist} não encontrada')
    return lyrics_list

def get_lyric_local(music, artist):
    with open('lista_com_id.csv', 'r') as local_list:
        for line in local_list.readlines():
            music_name, artist_name, lyric = line.split(';')
            if music == music_name and artist == artist_name:
                return lyric

def get_lyrics_on_vagalume_api(music, artist):
    url = f"https://api.vagalume.com.br/search.php?art={artist}&mus={music}&apikey={api_key_vagalume}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print(data)
        if 'mus' in data:
            lyric = data['mus'][0]['text']
            formated_lyric = lyric.replace('\n', ' | ')
            with open("lista_com_id.csv", "a") as local_list:
                    local_list.write(f"{music[0]};{music[1]};{formated_lyric}\n")
            return formated_lyric
    else:
        print("Erro ao fazer requisição.")

def get_lyric_by_scraping(music_name, artist):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Executa o Chrome em modo invisível (sem interface gráfica)
    service = Service(executable_path='/usr/local/bin/chromedriver')
    # Use with block para gerenciar o driver
    with webdriver.Chrome(service=service, options=chrome_options) as driver:
        # Define a query de pesquisa
        search_query = f"{artist} {music_name}"
        url = f"https://www.letras.mus.br/?q={search_query.replace(' ', '%20')}"
        # Navega até a URL
        driver.get(url)
        try:
            # Aguarde até que a classe `gs-title` seja carregada
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.gs-title > a')))
            # Encontre o primeiro elemento `a` dentro da `div.gs-title`
            result = driver.find_element(By.CSS_SELECTOR, 'div.gs-title > a')
            link = result.get_attribute('href')  # Pega o link da música
            # Navega até a página da música
            driver.get(link)
            # Aguarde o carregamento da letra
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'lyric-original')))
            result = driver.find_element(By.CLASS_NAME, 'lyric-original')
            # Use BeautifulSoup para processar o HTML e extrair a letra
            soup = BeautifulSoup(result.get_attribute('outerHTML'), 'html.parser')
            lyric = soup.get_text(separator=" | ").strip()
            if lyric:
                with open("lista_com_id.csv", "a") as id_list:
                    id_list.write(f"{music_name};{artist};{lyric}\n")
                    return lyric
            else:
                with open("lista_com_id.csv", "a") as id_list:
                    id_list.write(f"{music_name};{artist};Letra não encontrada no letras.mus\n")
        except Exception as e:
            return f"Error:{str(e)}"

print(get_lyrics())