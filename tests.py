import requests, os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Configuração do ChromeDriver
artist = 'ferrugem'
music_name = 'o som do tambor'
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
        title = result.text  # Pega o título e o nome do artista
        music, artist, discard = title.split(' - ')
        # Navega até a página da música
        driver.get(link)
        # Aguarde o carregamento da letra
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'lyric-original')))
        result = driver.find_element(By.CLASS_NAME, 'lyric-original')
        # Use BeautifulSoup para processar o HTML e extrair a letra
        soup = BeautifulSoup(result.get_attribute('outerHTML'), 'html.parser')
        lyric = soup.get_text(separator=" | ").strip()
        return lyric
    except Exception as e:
        return f"Error:{str(e)}"
        # return f"Error:{str(e)}"