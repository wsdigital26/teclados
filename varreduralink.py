from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
import time
import re
import json

# Configuração inicial
URL_LOGIN = "https://loja.hayamax.com.br/entrar-cliente?return_to=https%3A%2F%2Fhayamax.com.br%2F"
LOGIN = "1 1 5 5 8 3 9 1 0 0 0 1 8 0"
SENHA = "Adw@0412"

# Categorias a serem coletadas
CATEGORIAS = {
    "Teclados": "https://loja.hayamax.com.br/categoria/instrumentos-musicais-teclas",
    # Adicione outras categorias aqui
}

# Inicializa o Selenium
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def fazer_login():
    """Realiza login na plataforma"""
    driver.get(URL_LOGIN)
    wait.until(EC.presence_of_element_located((By.ID, "customer[stcd1]"))).send_keys(LOGIN)
    wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))).send_keys(SENHA)
    wait.until(EC.element_to_be_clickable((By.ID, "btn-login"))).click()
    print("✅ Login realizado com sucesso!")

def carregar_todos_produtos(url):
    """Carrega todos os produtos de uma categoria clicando no botão 'Ver mais' até que ele desapareça"""
    driver.get(url)
    time.sleep(5)  # Tempo extra para carregar a página inicial
    
    while True:
        try:
            produtos_atuais = len(driver.find_elements(By.CLASS_NAME, "search-product"))
            btn_ver_mais = wait.until(EC.element_to_be_clickable((By.ID, "btn-more")))
            btn_ver_mais.click()
            wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, "search-product")) > produtos_atuais)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Pequena pausa para carregamento
        except Exception as e:
            print(f"✅ Todos os produtos carregados para a categoria: {url}")
            break  

def coletar_produtos():
    """Coleta os produtos visíveis na página e aplica o reajuste de preço"""
    produtos = driver.find_elements(By.CLASS_NAME, "search-product")
    print(f"🔍 Total de produtos encontrados (antes do filtro): {len(produtos)}")

    dados = []
    todos_nomes = []  # Lista para debug

    for idx, p in enumerate(produtos):
        # Nome do Produto
        nome = p.find_element(By.CLASS_NAME, "search-product-title").text.strip() if p.find_elements(By.CLASS_NAME, "search-product-title") else None
        if nome:
            todos_nomes.append(nome)  # Adiciona para debug
        
        # Código do Produto
        codigo = p.find_element(By.CLASS_NAME, "search-product-matnr").text.strip() if p.find_elements(By.CLASS_NAME, "search-product-matnr") else None
        if codigo:
            codigo = re.sub(r"[^\d]", "", codigo)

        # Preço (tentando diferentes classes)
        preco_elementos = p.find_elements(By.CLASS_NAME, "search-product-price-sales") or p.find_elements(By.CLASS_NAME, "search-product-price")
        preco = preco_elementos[0].text.strip() if preco_elementos else None
        if preco and "R$" in preco:
            preco = re.sub(r"[^\d,]", "", preco)  # Remove caracteres não numéricos
            preco = float(preco.replace(",", "."))  # Converte o preço para número flutuante

            # Aplica o reajuste de preço
            preco = preco * 1.17
            preco = f"R$ {preco:,.2f}".replace(".", ",")  # Formata o preço com vírgula
        else:
            preco = None

        # Imagem do Produto
        imagem_element = p.find_element(By.CLASS_NAME, "search-product-image")
        imagem = imagem_element.get_attribute("src")

        if "data:image" in imagem:
            imagem = imagem_element.get_attribute("data-src")

        if not imagem or "data:image" in imagem or not imagem.startswith("http"):
            imagem = "Imagem não disponível"

        # Filtra produtos sem nome, código, preço ou imagem válida
        if nome and codigo and preco:
            dados.append((nome, codigo, preco, imagem))
        else:
            print(f"⚠️ Produto na posição {idx + 1} ignorado.")
            print(f"   Nome: {nome}")
            print(f"   Código: {codigo}")
            print(f"   Preço: {preco}")
            print(f"   Imagem: {imagem}\n")

    # Debug: Exibir todos os produtos coletados antes da filtragem
    print("\n📜 Lista de nomes antes da filtragem:")
    for nome in todos_nomes:
        print(f" - {nome}")

    print(f"\n✅ Total de produtos salvos após filtro: {len(dados)}")
    return dados

def salvar_json(dados_por_categoria, arquivo="produtos_hayamax.json"):
    """Salva os produtos de cada categoria em um arquivo JSON"""
    produtos_json = {}
    
    for categoria, dados in dados_por_categoria.items():
        produtos_json[categoria] = []
        for produto in dados:
            produto_dict = {
                "Nome": produto[0],
                "Código": produto[1],
                "Preço": produto[2],
                "Imagem (URL)": produto[3]
            }
            produtos_json[categoria].append(produto_dict)
    
    # Salva o arquivo JSON
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos_json, f, ensure_ascii=False, indent=4)
    print(f"\n✅ Arquivo JSON '{arquivo}' gerado com sucesso!")

# Executa o fluxo
fazer_login()

dados_por_categoria = {}

for nome_categoria, url_categoria in CATEGORIAS.items():
    print(f"\n🔄 Coletando produtos da categoria: {nome_categoria}")
    carregar_todos_produtos(url_categoria)
    produtos = coletar_produtos()
    
    if produtos:
        dados_por_categoria[nome_categoria] = produtos
    else:
        print(f"❌ Nenhum produto encontrado para a categoria: {nome_categoria}")

if dados_por_categoria:
    salvar_json(dados_por_categoria)  # Agora salva em formato JSON

driver.quit()
