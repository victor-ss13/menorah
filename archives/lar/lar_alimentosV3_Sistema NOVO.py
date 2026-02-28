import re
import time
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

# --- CONFIGURAÇÕES GLOBAIS ---
URL_LOGIN = "http://fv.lar.ind.br:8180/piloto/login.form.ws"
URL_PEDIDO = "http://fv.lar.ind.br:8180/piloto/pedido/cadastro.novo.ws"
USUARIO = "6795681"
SENHA = "6795681"
FILIAL_NOME = "UIA MATELANDIA-LAR COOPERATIVA AGROINDUSTRIAL"
CLIENTE_NOME = "FRIGORIFICO CALAFATE LTDA - 6147936"
PRAZO_PAGAMENTO = "7 Dias"
EXCEL_PATH = r"Códigos dos produtos Lar Alimentos.xlsx"

def carregar_produtos_do_excel(caminho_arquivo):
    """Carrega os códigos de produtos de um arquivo Excel."""
    try:
        df = pd.read_excel(caminho_arquivo)
        codigos = df["CÓDIGO"].astype(str).tolist()
        produtos = [codigo for codigo in codigos]
        return produtos
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return []

def inicializar_driver():
    """Configura e inicializa o WebDriver do Selenium (navegador oculto)."""
    options = webdriver.ChromeOptions()
    # headless moderno (caso seu Chrome suporte) - se der problema, troque por '--headless'
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-first-run')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--disable-extensions')
    options.add_argument('--window-size=1920,1080')

    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.password_manager_leak_detection": False,
        "safebrowsing.enabled": True 
    }
    
    options.add_experimental_option("prefs", prefs)
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Chrome(options=options)
    return driver

def fazer_login(driver, wait):
    """Executa o processo de login no sistema."""
    print("\n➡️ Iniciando processo de login...")
    driver.get(URL_LOGIN)
    
    input_usuario = wait.until(EC.presence_of_element_located((By.ID, "formusuario")))
    input_usuario.clear()
    input_usuario.send_keys(USUARIO)
    print("✅ Usuário preenchido")

    input_senha = wait.until(EC.presence_of_element_located((By.ID, "formsenha")))
    input_senha.clear()
    input_senha.send_keys(SENHA)
    print("✅ Senha preenchida")

    botao_logar = wait.until(EC.element_to_be_clickable((By.ID, "btnGravar")))
    botao_logar.click()
    print("✅ Login realizado com sucesso!")

def preencher_cabecalho_pedido(driver, wait):
    """Preenche as informações do cabeçalho do pedido."""
    print("\n➡️ Navegando para a página de novo pedido...")
    driver.get(URL_PEDIDO)

    print("➡️ Preenchendo cabeçalho...")

    filial = wait.until(EC.element_to_be_clickable((By.ID, "select2-cmbFilial-container")))
    filial.click()

    opcao_filial = wait.until(EC.element_to_be_clickable((By.XPATH, f"//ul[@id='select2-cmbFilial-results']//li[normalize-space(text())='{FILIAL_NOME}']")))
    opcao_filial.click()

    print("✅ Filial selecionada com sucesso!")
    
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))

    campo_cliente = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.search-input-cliente_inputPluginSearchCliente")))
    campo_cliente.clear()
    campo_cliente.send_keys(CLIENTE_NOME)

    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))

    sugestao_cliente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-autocomplete li.ui-menu-item")))
    sugestao_cliente.click()
    print("✅ Cliente selecionado com sucesso!")

    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))

    prazo_pagamento = wait.until(EC.element_to_be_clickable((By.ID, "select2-cmbCondicaoPagamento-container")))
    prazo_pagamento.click()

    opcao_prazo_pagamento = wait.until(EC.element_to_be_clickable((By.XPATH, f"//ul[@id='select2-cmbCondicaoPagamento-results']//li[normalize-space(text())='{PRAZO_PAGAMENTO}']")))
    opcao_prazo_pagamento.click()
    print("✅ Prazo de pagamento selecionado com sucesso!")

    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))

    match = re.search(r'ID_\d+', driver.current_url)
    URL_ID = match.group(0)
    print(f"ID da URL: {URL_ID}")

    return URL_ID

def print_progress(current, total, bar_length=40):
    """Desenha uma progress bar simples no terminal."""
    percent = current / total if total else 0
    filled = int(bar_length * percent)
    bar = '#' * filled + '-' * (bar_length - filled)
    print(f"\r[{bar}] {current}/{total} ({percent*100:5.1f}%)", end='', flush=True)

def adicionar_produtos(driver, wait, produtos_a_processar, url_id):
    """Itera sobre a lista de produtos, adicionando-os ao pedido e coletando os resultados."""
    todos_os_resultados = []
    
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    params = parse_qs(parsed_url.query)

    sk_values = params.get("sk")
    if not sk_values:
        raise RuntimeError("Parâmetro 'sk' não encontrado na URL atual.")
    sk_value = sk_values[0]

    total = len(produtos_a_processar)
    for idx, codigo_produto in enumerate(produtos_a_processar, start=1):
        wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))
        time.sleep(0.3) # Tempo de consulta entre cada produto
        url = f"http://fv.lar.ind.br:8180/piloto/{url_id}/pedido/cadastro.pesquisarProdutos.ws?sk={sk_value}&term={codigo_produto}"
        result = driver.execute_async_script("""
            var url = arguments[0];
            var callback = arguments[1];

            $.getJSON(url)
                .done(function(data) {
                    callback(data);
                })
                .fail(function(err) {
                    callback({error: err.statusText});
                });
        """, url)

        produtos = result.get("produtos", []) if isinstance(result, dict) else []
        produto = next((p for p in produtos if p.get("codigo") == str(codigo_produto)), None)

        if produto:
            status = "Sucesso" if produto["estoque"] != "0,00" else "Sem Estoque"
            todos_os_resultados.append([produto["codigo"], produto["label"], produto["precoBase"], produto["precoVenda"], produto["estoque"], status])
        else:
            todos_os_resultados.append([codigo_produto, "Produto não encontrado", 0, 0, 0, "Não encontrado"])

        print_progress(idx, total)

    return todos_os_resultados

def salvar_resultados(resultados, tempo_execucao):
    """Salva os resultados em um arquivo Excel e um TXT de resumo."""
    if not resultados:
        print("⚠️ Nenhum resultado para salvar.")
        return

    df_pedido = pd.DataFrame(resultados, columns=["Codigo", "Descricao", "Preco_Tabela", "Preco_Venda", "Quantidade", "Status"])
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Pedido_Digitado_{timestamp}.xlsx"

    print(f"\n➡️ Salvando resultados em {filename}...")
    try:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df_pedido.to_excel(writer, index=False, sheet_name='Produtos')
            resumo_df = pd.DataFrame({"Info": ["Tempo total de execução"], "Valor": [tempo_execucao]})
            resumo_df.to_excel(writer, index=False, sheet_name='Resumo')
        
        print(f"✅ Pedido exportado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao salvar o arquivo: {e}")

def main():
    """Função principal que orquestra a execução do script."""
    produtos_a_processar = carregar_produtos_do_excel(EXCEL_PATH)
    if not produtos_a_processar:
        return

    print(f"{len(produtos_a_processar)} CÓDIGOS CARREGADOS")
    driver = inicializar_driver()
    wait = WebDriverWait(driver, 20)
    tempo_inicio = time.time()

    try:
        fazer_login(driver, wait)
        url_id = preencher_cabecalho_pedido(driver, wait)
        resultados_finais = adicionar_produtos(driver, wait, produtos_a_processar, url_id)
        
        tempo_total = time.time() - tempo_inicio
        minutos, segundos = divmod(int(tempo_total), 60)
        tempo_formatado = f"{minutos}m {segundos}s"
        
        salvar_resultados(resultados_finais, tempo_formatado)
        print(f"\n⏱ Tempo total de execução: {tempo_formatado}")

    except Exception as e:
        print(f"\n❌ OCORREU UM ERRO CRÍTICO: {e}")
    finally:
        print("➡️ Fechando o navegador.")
        driver.quit()

if __name__ == "__main__":
    main()
