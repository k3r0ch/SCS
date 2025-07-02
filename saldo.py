import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
import re


#localFolder = path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
options = uc.ChromeOptions()
# options.add_argument("--headless")
# Caso queira usar seu perfil do Chrome:
#options.add_argument(f'--user-data-dir={localFolder}')
#options.add_argument(r'--profile-directory=Profile 7')
driver = uc.Chrome(options=options)
URL = "https://contratos.sistema.gov.br/transparencia/compras?modalidade_id=76&modalidade_id_text=05+-+Pregão"
execucoes = 0

def consultar_Saldos(URL=""):
    try:
        driver.get(URL)

        print("\nFaça o login manualmente na janela aberta, se necessário. Navegue até a lista de itens do pregão, depois pressione ENTER aqui.")
        input()
        inicio = time.time()

        # Aguarda a div aparecer (ajuste timeout se necessário!)
        div_header = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.header-info div.header-title'))
        )

        texto = div_header.text.strip()
        # Exemplo: "Itens da compra: 160482 - Pregão | 90008/2024"

        ugpregao = ""
        # Supondo que 'texto' seja: "Itens da compra: 160482 - Pregão | 90021/2024"
        match = re.search(r'Itens da compra:\s*(\d+)\s*-\s*.*\|\s*(\d+)/(\d+)', texto)
        if match:
            numero1 = match.group(1)
            numero2 = match.group(2)
            numero3 = match.group(3)
            ugpregao = f"{numero1}-{numero2}{numero3}"
            print(f'[DEBUG] Valor extraído: {ugpregao}')
        else:
            print('[ERRO] Texto inesperado na header-title!')
            ugpregao = None


        select_element = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.NAME, "crudTable_length"))
        )
        select = Select(select_element)
        select.select_by_value("-1")
        # Espera até a div de processamento sumir (ou seja, display: none)
        try:
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.ID, "crudTable_processing"))
            )
            print("[DEBUG] Carregamento da tabela finalizado.")
        except Exception as e:
            print(f"[ERRO] Timeout esperando carregamento da tabela: {e}")

        table = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        rows = table.find_elements(By.TAG_NAME, "tr")
        hrefs = set()
        for row in rows:
            links = row.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                if href:
                    hrefs.add(href)

        hrefs = list(hrefs)
        print(f"\nTotal de links coletados: {len(hrefs)}\n")
        if len(hrefs) == 0:
            print("Nenhum link foi coletado. Verifique o seletor da tabela de links.")
            exit()

        dados = []  # todas as linhas a serem salvas

        for idx, url in enumerate(hrefs, 1):
            print(f'\nExtraindo dados do link {idx}/{len(hrefs)}: {url}')
            driver.get(url)

            # Aguarda até a presença da tabela (máximo de 20 segundos; ajuste se quiser)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table.table-striped.mb-0'))
                )
                print("Tabela pronta para extração.")
            except:
                print("[ERRO] Tabela de itens não encontrada após o timeout!")
                continue

            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            main_table = soup.find('table', class_='table table-striped mb-0')
            main_table = main_table.find('tbody')

            if main_table:
                print("Box de informações encontrado.")
            else:
                print("Box de informações NÃO encontrado!")

            info = {}
            campos_simples = [
                "Número", "Tipo Item", "Descrição",
                "Descrição detalhada", "Qtd. Total"
            ]
            for campo in campos_simples:
                info[campo] = ""

            info["Qtd. Autorizada"] = ""
            info["Qtd. Saldo"] = ""
            info["Número Ata"] = ""
            info["Vigência Fim"] = ""
            info["Fornecedor"] = ""
            info["Val_unit"] = ""
            info["Val_neg"] = ""

            found_campos = []

            for tr in main_table.find_all('tr', recursive=False):
                tds = tr.find_all('td', recursive=False)
                if len(tds) != 2:
                    continue

                chave = tds[0].get_text(strip=True).replace(":", "")
                valor = tds[1].get_text(strip=True)

                if chave in campos_simples:
                    info[chave] = valor
                    found_campos.append((chave, valor))

                if chave == "Unidades Participantes":
                    inner_table = tds[1].find('table')
                    if inner_table:
                        #Caso seja utilizada a busca por titulo da coluna, descomentar a linha abaixo
                        #headers = [th.get_text(strip=True) for th in inner_table.find_all('th')]
                        
                        for row in inner_table.find_all('tr')[1:]:
                            cols = [td.get_text(strip=True) for td in row.find_all('td')]
                            if cols and cols[0].startswith(ug_ext):

                                try:
                                    #idx_aut = headers.index("Qtd. autorizada")
                                    #idx_saldo = headers.index("Qtd. Saldo")
                                    #info["Qtd. Autorizada"] = cols[idx_aut]
                                    #info["Qtd. Saldo"] = cols[idx_saldo]

                                    #Alterado para buscar conforme as colunas 3 e 4 que nao mudam
                                    #O codigo acima realiza a busca conforme o index do texto do titulo da coluna
                                    info["Qtd. Autorizada"] = cols[2]
                                    info["Qtd. Saldo"] = cols[3]
                                    #print(f"Qtd. Autorizada: {info['Qtd. Autorizada']}, Qtd. Saldo: {info['Qtd. Saldo']}")
                                except ValueError:
                                    info["Qtd. Autorizada"] = ""
                                    info["Qtd. Saldo"] = ""
                                break
                    else:
                        info["Qtd. Autorizada"] = ""
                        info["Qtd. Saldo"] = ""

                if chave == "Fornecedores Homologados":
                    inner_table = tds[1].find('table')
                    if inner_table:
                        print("Tabela de fornecedores encontrada.")
                        
                        #linhas_fornecedor = inner_table.find_all('tr')[1:]
                        #print(f"Quantidade de linhas de fornecedores encontradas: {len(linhas_fornecedor)}")
                        #for row_f in linhas_fornecedor:
                            #print("Dados da linha:", [td.text.strip() for td in row_f.find_all('td')])
                    else:
                        print("Tabela de fornecedores NÃO encontrada!")

                    if inner_table:
                        header_texts = [th.get_text(strip=True) for th in inner_table.find_all('th')]
                        idx_fornecedor = header_texts.index("Fornecedor") if "Fornecedor" in header_texts else None
                        idx_val_unit = header_texts.index("Vlr. Unitário") if "Vlr. Unitário" in header_texts else header_texts.index("Val. Unitário")
                        idx_val_neg = header_texts.index("Vlr. Negociado") if "Vlr. Negociado" in header_texts else header_texts.index("Val. Negociado")
                        count_fornecedores = 0
                        for row_f in inner_table.find_all('tr')[1:]:
                            cols = [td.get_text(strip=True) for td in row_f.find_all('td')]
                            if cols and idx_fornecedor is not None:

                                info["Fornecedor"] = cols[idx_fornecedor]
                                info["Val_unit"] = cols[idx_val_unit]
                                info["Val_neg"] = cols[idx_val_neg]

                                count_fornecedores += 1
                        if count_fornecedores == 0:
                            print("Tabela 'Fornecedores Homologados' presente, mas nenhum fornecedor encontrado.")
                    else:
                        print("Nenhum fornecedor homologado neste item.")

                if chave == "Atas de Registro de Preços":
                    inner_table = tds[1].find('table')
                    if inner_table:
                        header_texts = [th.get_text(strip=True) for th in inner_table.find_all('th')]
                        idx_numero = header_texts.index("Número") if "Número" in header_texts else None
                        idx_vigenciafim = header_texts.index("Vigência fim") if "Vigência fim" in header_texts else header_texts.index("Vigência Final")
                        rows = inner_table.find_all('tr')
                        for row in rows[1:]:
                            cols = row.find_all('td')
                            if not cols:
                                continue
                            # Exemplo: supondo que "Número" está na coluna 0 e "Vigência Fim" na coluna 5
                            numero = cols[idx_numero].get_text(strip=True)
                            vigencia_fim = cols[idx_vigenciafim].get_text(strip=True)
                                        
                            info["Número Ata"] = numero
                            info["Vigência Fim"] = vigencia_fim
                                #print(f"Número Ata: {info['Número Ata']}, Vigência Fim: {info['Vigência Fim']}")
                    else:
                        info["Número Ata"] = ""
                        info["Vigência Fim"] = ""
                        print("Nenhuma ata vigente neste item.")

            # Cria a linha com os dados extraídos e adiciona ao array dados
            linha = [
                info["Número"],
                info["Tipo Item"],
                info["Descrição"],
                info["Descrição detalhada"],
                info["Qtd. Total"],
                info["Qtd. Autorizada"],
                info["Qtd. Saldo"],
                info["Fornecedor"],
                info["Val_unit"],
                info["Val_neg"],
                info["Número Ata"],
                info["Vigência Fim"]
            ]
            dados.append(linha)

            #print("Dados acumulados até aqui:", dados)
            # Mostra campos simples encontrados
            #print("Campos simples extraídos:", found_campos)
        titulos = [
            "Número",
            "Tipo Item",
            "Descrição",
            "Descrição detalhada",
            "Qtd. Total",
            "Qtd. Autorizada",
            "Qtd. Saldo",
            "Fornecedor",
            "Vlr. Unitário",
            "Vlr. Negociado",
            "Número Ata",
            "Vigência Fim"
        ]

        print(f"\nLinhas extraídas para planilha: {len(dados)}")
        if len(dados) == 0:
            print("Nenhum dado foi extraído! Reveja os seletores e prints acima.")

        # Agora pega data/hora atual do sistema
        agora = datetime.now()  # por padrão está no fuso do sistema operacional
        # Formata como "DDHHmmMMAAAA"
        datahora_fmt = agora.strftime("%d%H%M%m%Y")
        # Monta o nome do arquivo
        nome_arquivo = f"{ugpregao}-{datahora_fmt}.xlsx"
        print(f"[DEBUG] Nome do arquivo de saída: {nome_arquivo}")

        df = pd.DataFrame(dados, columns=titulos)
        df.to_excel(nome_arquivo, index=False)
        #df.to_csv('dados_extraidos.csv', index=False, sep=";")
        print("\nProcesso finalizado! Arquivo salvo com sucesso.")
        fim = time.time()
        tempo_execucao = fim - inicio
        print(f"O script foi executado em: {tempo_execucao:.4f} segundos")

    except Exception as e:
            print(f"[ERRO] {e}")
    finally:
        main()

def mostrar_menu(execucoes):
    RED = "\33[91m"
    PURPLE = '\033[0;35m' 
    END = "\033[0m"

    font = f"""{RED}
[|*]=============================================================[*|]
 |Z|                                                              |Z|
 |Z| ░▒▓██████████████▓▒░░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ |Z|
 |Z| ░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓██████▓▒░  |Z|
 |Z|                                                              |Z|
[|*]=============================================================[*|]
{PURPLE}
 Criado por: 1º Ten QUEIROZ - Adj SALC/1ª Bda Inf Sl
 Versão: v1 - 23JUN25
[|*]============================================================[*|]{END}
"""
    print(font)

    if execucoes == 1:
        global ug_ext
        ug_ext = input("Digite a UG a serem extraídos os saldos (Ex.: 160482): ")

    print("\nMenu:")
    print("1. Nova Consulta")
    print("2. Sair")

def main():
    while True:
        global execucoes
        execucoes += 1
        mostrar_menu(execucoes)
        escolha = input("Escolha uma opção: ")

        match escolha:
            case "1":
                consultar_Saldos(URL)
            case "2":
                print("Saindo do programa.")
                driver.quit()
                break
            case _:
                print("Opção inválida.")

if __name__ == "__main__":
    main()