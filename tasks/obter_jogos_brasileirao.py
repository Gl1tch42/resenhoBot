from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def obter_jogos_brasileirao():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false") # NÃO carrega imagens
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--no-proxy-server")
    chrome_options.add_argument("--log-level=3")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    url = "https://ge.globo.com/futebol/brasileirao-serie-a/"
    lista_resultados = []

    try:
        driver.get(url)
        driver.implicitly_wait(10) # Espera até 10s para os elementos aparecerem

        jogos = driver.find_elements(By.CLASS_NAME, 'lista-jogos__jogo')

        for jogo in jogos:
            try:
                
                siglas = jogo.find_elements(By.CLASS_NAME, 'equipes__sigla')
                mandante = siglas[0].get_attribute('title')
                visitante = siglas[1].get_attribute('title')

                gols = jogo.find_elements(By.CLASS_NAME, 'placar-box__valor')
                gols_m = gols[0].text.strip() if gols else ""
                gols_v = gols[-1].text.strip() if gols else ""

                
                info_container = jogo.find_element(By.CLASS_NAME, 'jogo__informacoes')
                
                spans = info_container.find_elements(By.TAG_NAME, 'span')
                
                detalhes = [s.text.strip() for s in spans if s.text.strip()]
                status_info = " — ".join(detalhes) 

                if gols_m != "":
                    placar_str = f"{gols_m} x {gols_v}"
                else:
                    placar_str = "x"

                lista_resultados.append({
                    "mandante": mandante,
                    "visitante": visitante,
                    "placar": placar_str,
                    "status": status_info
                })
            except Exception as e:
                continue
    finally:
        driver.quit()
        
    return lista_resultados