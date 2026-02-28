import re
import time
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs

# --- CONFIGURAÇÕES GLOBAIS ---
URL_LOGIN = "https://sfa.frimesa.com.br:8443/piloto/login.form.ws"
URL_PEDIDO = "https://sfa.frimesa.com.br:8443/piloto/pedido/cadastro.novo.ws"
USUARIO = "5757"
SENHA = "sim3gm"
CLIENTE_NOME = "ENEIDE RODRIGUES PINTO CRUZ"
TABELA_NOME = "FIBH - FOOD SERVICE DISPONÍVEL"
CONDICAO_PAGAMENTO = "ANTECIPADO"
EXCEL_PATH = r"Códigos dos produtos Frimesa.xlsx"

def carregar_produtos_do_excel(caminho_arquivo):
    """Carrega os códigos de produtos de um arquivo Excel."""
    try:
        df = pd.read_excel(caminho_arquivo)
        codigos = df["CÓDIGO"].astype(str).tolist()
        produtos = codigos
        return produtos
    except FileNotFoundError:
        print(f"❌ Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return []

def inicializar_driver():
    """Configura e inicializa o WebDriver do Selenium."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--window-size=1920,1080')
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

    print("➡️ Preenchendo cliente...")
    campo_cliente = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "search-input-cliente_inputPluginSearchCliente")))
    campo_cliente.clear()
    campo_cliente.send_keys(CLIENTE_NOME)
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))

    sugestao_cliente = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ui-autocomplete li.ui-menu-item")))
    sugestao_cliente.click()
    print("✅ Cliente selecionado com sucesso!")

    print("➡️ Selecionando tabela de preço...")
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))
    tabela_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "select2-cmbTabelaPreco-container")))
    tabela_dropdown.click()
    opcao_tabela = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{TABELA_NOME}')]")))
    opcao_tabela.click()
    print(f"✅ Tabela '{TABELA_NOME}' selecionada!")

    print("➡️ Selecionando condição de pagamento...")
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "minimalist-loading-background")))
    condicao_dropdown = wait.until(EC.element_to_be_clickable((By.ID, "select2-cmbCondicaoPagamento-container")))
    condicao_dropdown.click()
    opcao_condicao = wait.until(EC.element_to_be_clickable((By.XPATH, f"//li[contains(text(), '{CONDICAO_PAGAMENTO}')]")))
    opcao_condicao.click()
    print(f"✅ Condição de pagamento '{CONDICAO_PAGAMENTO}' selecionada!")

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
    print("➡️ Iniciando processo de adição de produtos...")
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
        url = f"https://sfa.frimesa.com.br:8443/piloto/{url_id}/pedido/cadastro.pesquisarProdutos.ws?sk={sk_value}&term={codigo_produto}"
        result = driver.execute_async_script("""
            const url = arguments[0];
            const codigoBuscado = arguments[1];
            const callback = arguments[2];

            (async () => {
                try {
                    let data = await $.getJSON(url);
                    if (!data || !data.produtos || data.produtos.length === 0)
                        return callback({ error: "Produto não encontrado" });

                    let item = data.produtos.find(p => p.codigo === codigoBuscado);

                    if (!item)
                        return callback({ error: "Produto não encontrado" });

                    let urlPost = url.replace("cadastro.pesquisarProdutos.ws", "cadastro.addItem.ws") + "&isGridCarrinho=true";
                    let res = await $.post(urlPost, { produto: item.id });
                    let json = JSON.parse(res);

                    let escUrl = url.replace("cadastro.pesquisarProdutos.ws", "cadastro.buscarEscalonamentoPrecoVenda.ws")
                                    + "&idProduto=" + json.item.id;

                    let escalonamento = await $.getJSON(escUrl);

                    callback({ produto: item, escalonamento: escalonamento });
                } catch (e) {
                    callback({ error: e.toString() });
                }
            })();
        """, url, codigo_produto)

        escalonamentos = [["N/A", "", ""] for _ in range(6)]
        if isinstance(result, dict):
            escalonamento = result.get("escalonamento", {})
            html_escalonamento = escalonamento.get("htmlEscalonamentoPrecoVenda", "")

            if html_escalonamento:
                soup = BeautifulSoup(html_escalonamento, "html.parser")
                tabela = soup.find("table")
                if tabela:
                    tbody = tabela.find("tbody") or tabela
                    linhas = tbody.find_all("tr")
                    for i, linha in enumerate(linhas[:6]):
                        tds = linha.find_all("td")
                        if len(tds) >= 5:
                            qtd_min = tds[0].get_text(strip=True).replace("\xa0", " ")
                            faixa_inicial = tds[2].get_text(strip=True).replace("\xa0", " ")
                            preco_tag = tds[4].find("b") or tds[4]
                            preco = preco_tag.get_text(strip=True).replace("\xa0", " ")
                            escalonamentos[i] = [preco, qtd_min, faixa_inicial]
        
        produto = result.get("produto")

        if produto:
            status = "Sucesso" if produto["estoque"] != "0,00" else "Sem Estoque"
            todos_os_resultados.append([
                produto["codigo"],
                f"{produto['label']} - {produto['codigo']}",
                produto["precoBase"],
                produto["precoVenda"],
                produto["estoque"],
                status,
                *[val for trio in escalonamentos for val in trio]
            ])
        else:
            todos_os_resultados.append([
                codigo_produto, "Produto não encontrado", 0, 0, 0, "Não encontrado",
                *[val for trio in escalonamentos for val in trio]
            ])

        print_progress(idx, total)

    return todos_os_resultados

def salvar_resultados(resultados, tempo_execucao):
    """Salva os resultados em um arquivo Excel e um TXT de resumo."""
    if not resultados:
        print("⚠️ Nenhum resultado para salvar.")
        return

    colunas_base = [
        "Codigo", "Descricao", "Preco_Tabela", "Preco_Venda", 
        "Quantidade", "Status"
    ]

    colunas_escalonamento = []
    for i in range(1, 7):
        colunas_escalonamento.extend([
            f"Escalonamento {i}",
            f"Qtd.Mín.",
            f"Faixa Inicial"
        ])

    df_pedido = pd.DataFrame(
        resultados,
        columns=colunas_base + colunas_escalonamento
    )
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Pedido_Digitado_{timestamp}.xlsx"

    print(f"\n➡️ Salvando resultados em {filename}...")
    try:
        with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
            df_pedido.to_excel(writer, index=False, sheet_name='Produtos')
            resumo_df = pd.DataFrame({"Info": ["Tempo total de execução"], "Valor": [tempo_execucao]})
            resumo_df.to_excel(writer, index=False, sheet_name='Resumo')

        txt_filename = filename.replace('.xlsx', '.txt')
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"Tempo total de execução: {tempo_execucao}\n")
        
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
    wait = WebDriverWait(driver, 120)
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
