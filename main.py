import requests, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm

api_key_vagalume = os.getenv("KEY_VAGALUME")

def get_lyric_by_scraping(artist, music_name):
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
                    id_list.write(f"{music_name}; {artist}; ID não encontrado; {lyric}\n")
            else:
                with open("lista_com_id.csv", "a") as id_list:
                    id_list.write(f"{music_name}; {artist}; ID não encontrado; Não encontrado no letras.mus\n")
        except Exception as e:
            return f"Error:{str(e)}"

def get_playlist():
    with open('musicas.csv', "r") as file:
        playlist = []
        for music in file:
            music = music.strip("\n")
            music_name, artist_name = music.split(", ")
            playlist.append((music_name, artist_name))
        return playlist

def find_lyrics_on_vagalume(playlist):
    for music in tqdm(playlist, desc="Processando músicas", ncols=100):
        url = f"https://api.vagalume.com.br/search.php?art={music[1]}&mus={music[0]}&apikey={api_key_vagalume}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # print(data)
            if 'mus' in data:
                music_id = data['mus'][0]['id']
                lyric = data['mus'][0]['text']
                formated_lyric = lyric.replace('\n', ' | ')
                with open("lista_com_id.csv", "r") as lista_id:
                    content = lista_id.read()
                if music_id not in content:
                    with open("lista_com_id.csv", "a") as id_list:
                        id_list.write(f"{music[0]}; {music[1]}; {music_id}; {formated_lyric}\n")
            else:
                #TODO: validação para não adicionar de novo se já tiver música e artista cadastrados
                get_lyric_by_scraping(music[1], music[0])
        else:
            print("Erro ao fazer requisição.")


if __name__ == '__main__':
    playlist = get_playlist()
    find_lyrics_on_vagalume(playlist)

