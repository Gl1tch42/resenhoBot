from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import pytz # Instale com: pip install pytz

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

                info_container = jogo.find_element(By.CLASS_NAME, 'jogo__informacoes')
            
                # Pega a data (ex: "01/04") e a hora (ex: "19:30")
                d_str = info_container.find_element(By.CLASS_NAME, 'jogo__informacoes--data').text.strip()
                h_str = info_container.find_element(By.CLASS_NAME, 'jogo__informacoes--hora').text.strip()
                
                # Chama a função de inteligência de tempo
                tipo_status, texto_status = definir_status_por_horario(d_str, h_str)
                
                # Se o site já tiver um placar mas nossa lógica diz "Futuro", 
                # vale o que o site diz (caso o jogo tenha começado atrasado)
                gols = jogo.find_elements(By.CLASS_NAME, 'placar-box__valor')
                tem_gols = any(g.text.strip() for g in gols)
                
                if tem_gols and tipo_status == "FUTURO":
                    tipo_status = "AO_VIVO"

                lista_resultados.append({
                    "mandante": mandante,
                    "visitante": visitante,
                    "placar": placar_str,
                    "status": status_info,
                    "tipo_status": tipo_status,
                })
            except Exception as e:
                continue
    finally:
        if driver:
            print("Cleaning up Chrome instance...")
            driver.close() # Fecha a aba
            driver.quit()  # Fecha o processo do browser e do chromedriver
        
    return lista_resultados




def definir_status_por_horario(data_str, hora_str):
    fuso_br = pytz.timezone('America/Sao_Paulo')
    agora = datetime.now(fuso_br)
    
    # --- TRATAMENTO DO "HOJE" E "ONTEM" ---
    if "Hoje" in data_str:
        data_processada = agora.strftime("%d/%m/%Y")
    elif "Ontem" in data_str:
        ontem = agora - timedelta(days=1)
        data_processada = ontem.strftime("%d/%m/%Y")
    else:
        # Se for uma data normal tipo "01/04", adicionamos o ano atual
        data_processada = f"{data_str}/{agora.year}"

    # Monta a string final: "dd/mm/aaaa hh:mm"
    data_jogo_str = f"{data_processada} {hora_str}"
    
    try:
        # Converte para datetime
        data_inicio = datetime.strptime(data_jogo_str, "%d/%m/%Y %H:%M")
        data_inicio = fuso_br.localize(data_inicio)
        
        # Janela de jogo (2 horas e 15 minutos para garantir)
        data_fim = data_inicio + timedelta(hours=2, minutes=15)

        if agora < data_inicio:
            return "FUTURO", f"{hora_str}"
        
        elif data_inicio <= agora <= data_fim:
            # Se quiser mostrar os minutos decorridos:
            minutos = int((agora - data_inicio).total_seconds() / 60)
            return "AO_VIVO", f"{minutos}'"
        
        else:
            return "ENCERRADO", "Encerrado"
            
    except Exception as e:
        print(f"Erro ao converter data: {e}")
        return "FUTURO", f"{hora_str}" # Fallback seguro