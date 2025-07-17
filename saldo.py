import customtkinter as ctk
import undetected_chromedriver as uc
import threading
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
import sys

# --- INÍCIO: CONFIGURAÇÃO DE PERFIL PERSISTENTE (À PROVA DE PYINSTALLER) ---
# Determina o caminho base de forma robusta
if getattr(sys, 'frozen', False):
    # Se estiver rodando 'congelado' (como .exe), o caminho é o diretório do executável
    application_path = os.path.dirname(sys.executable)
else:
    # Se estiver rodando como .py normal, o caminho é o do próprio script
    application_path = os.path.dirname(os.path.abspath(__file__))

# Define o nome da pasta do perfil usando o caminho base correto
profile_path = os.path.join(application_path, "chrome_profile")

# Cria a pasta do perfil se ela não existir.
# Agora, isso acontecerá ao lado do seu .exe ou do seu .py
os.makedirs(profile_path, exist_ok=True)

# --- FIM: CONFIGURAÇÃO DE PERFIL PERSISTENTE ---


# --- INÍCIO: SCRIPT DE EXTRAÇÃO DE DADOS ---
# Este é o local onde seu script de extração de dados deve ser colocado.
# Ele recebe o 'driver' como argumento para que possa interagir com a
# página que já está logada.
# ALTERADO: A função agora recebe os parâmetros da Tela 3.
def extrair_dados_do_site(driver, tipo_pregao, tipo_ug, lista_pregoes, ug_unica, progress_callback, pregao_callback, completion_callback):
    """
    Função de exemplo para extrair dados após o login.
    Substitua o conteúdo desta função pelo seu script.
    """
    #tipo_pregao: 1 = UM pregao; 2 = MULTIPLOS pregoes
    #tipo_ug: 1 = UMA ug; 2 = MULTIPLAS ug
    #lista_pregoes: array com links
    #ug_unica: Codigo UG quando a variavel tipo_ug for 1

    if tipo_ug == "1":
        ug_ext = ug_unica
    else:
        ug_ext = 999999

    print("\n[+] Iniciando a extração de dados...")

    try:
        if tipo_pregao == "1":
            lista_pregoes = [driver.current_url]
            
        for pre, link_pregao in enumerate(lista_pregoes, 1):
            driver.get(link_pregao)
            inicio = time.time()

            # Aguarda a div aparecer (ajuste timeout se necessário!)
            div_header = WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, 'div.header-info div.header-title'))
            )

            texto = div_header.text.strip()
            # Exemplo: "Itens da compra: 160482 - Pregão | 90008/2024"

            # ATUALIZA A BARRA DE PROGRESSO
            pregao_callback(texto)

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
            total_itens = len(hrefs)
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

                info["Tipo UASG"] = ""
                info["Qtd. Autorizada"] = ""
                info["Qtd. Saldo"] = ""
                info["Número Ata"] = ""
                info["Vigência Fim"] = ""
                info["Fornecedor"] = ""
                info["Val_unit"] = ""
                info["Val_neg"] = ""

                found_campos = []

                unidades_participantes_inner_table_ref = None
                
                for tr in main_table.find_all('tr', recursive=False):
                    info["UG"] = ug_ext

                    tds = tr.find_all('td', recursive=False)
                    if len(tds) != 2:
                        continue

                    chave = tds[0].get_text(strip=True).replace(":", "")
                    valor = tds[1].get_text(strip=True)

                    if chave in campos_simples:
                        info[chave] = valor
                        found_campos.append((chave, valor))

                    #Realiza a busca e armazenamento dos dados na variavel info[]
                    if ug_ext != 999999:
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
                                            info["Tipo UASG"] = cols[1]
                                            info["Qtd. Autorizada"] = cols[2]
                                            info["Qtd. Saldo"] = cols[3]
                                            #print(f"Qtd. Autorizada: {info['Qtd. Autorizada']}, Qtd. Saldo: {info['Qtd. Saldo']}")
                                        except ValueError:
                                            info["Tipo UASG"] =""
                                            info["Qtd. Autorizada"] = ""
                                            info["Qtd. Saldo"] = ""
                                        break
                            else:
                                info["Tipo UASG"] = ""
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
                    else: 
                        if chave == "Unidades Participantes":
                            # Apenas armazena a referência para a tabela de Unidades Participantes
                            unidades_participantes_inner_table_ref = tds[1].find('table')

                        elif chave == "Fornecedores Homologados":
                            inner_table = tds[1].find('table')
                            if inner_table:
                                header_texts = [th.get_text(strip=True) for th in inner_table.find_all('th')]
                                idx_fornecedor = header_texts.index("Fornecedor") if "Fornecedor" in header_texts else None
                                idx_val_unit = header_texts.index("Vlr. Unitário") if "Vlr. Unitário" in header_texts else (header_texts.index("Val. Unitário") if "Val. Unitário" in header_texts else None)
                                idx_val_neg = header_texts.index("Vlr. Negociado") if "Vlr. Negociado" in header_texts else (header_texts.index("Val. Negociado") if "Val. Negociado" in header_texts else None)

                                # Pega a primeira linha de dados do fornecedor, conforme o requisito de "apenas um fornecedor"
                                data_rows = inner_table.find_all('tr')[1:] # Ignora a linha de cabeçalho
                                if data_rows:
                                    cols_f = [td.get_text(strip=True) for td in data_rows[0].find_all('td')]
                                    if cols_f and idx_fornecedor is not None and idx_val_unit is not None and idx_val_neg is not None:
                                        # Assegura que os índices existem antes de tentar acessá-los
                                        if len(cols_f) > idx_fornecedor and len(cols_f) > idx_val_unit and len(cols_f) > idx_val_neg:
                                            info["Fornecedor"] = cols_f[idx_fornecedor]
                                            info["Val_unit"] = cols_f[idx_val_unit]
                                            info["Val_neg"] = cols_f[idx_val_neg]

                        elif chave == "Atas de Registro de Preços":
                            inner_table = tds[1].find('table')
                            if inner_table:
                                header_texts_atas = [th.get_text(strip=True) for th in inner_table.find_all('th')]
                                idx_numero_ata = header_texts_atas.index("Número") if "Número" in header_texts_atas else None
                                idx_vigencia_fim_ata = header_texts_atas.index("Vigência fim") if "Vigência fim" in header_texts_atas else (header_texts_atas.index("Vigência Final") if "Vigência Final" in header_texts_atas else None)

                                # Pega a primeira linha de dados da ata, conforme o requisito
                                data_rows_atas = inner_table.find_all('tr')[1:] # Ignora a linha de cabeçalho
                                if data_rows_atas:
                                    cols_ata = data_rows_atas[0].find_all('td')
                                    if cols_ata and idx_numero_ata is not None and idx_vigencia_fim_ata is not None:
                                        # Assegura que os índices existem antes de tentar acessá-los
                                        if len(cols_ata) > idx_numero_ata and len(cols_ata) > idx_vigencia_fim_ata:
                                            info["Número Ata"] = cols_ata[idx_numero_ata].get_text(strip=True)
                                            info["Vigência Fim"] = cols_ata[idx_vigencia_fim_ata].get_text(strip=True)
                        

                #Realiza a criação de cada linha a ser inserida no arquivo Excel
                if ug_ext != 999999:
                    # Cria a linha com os dados extraídos e adiciona ao array dados
                    linha = [
                        info["Número"],
                        info["Tipo Item"],
                        info["Descrição"],
                        info["Descrição detalhada"],
                        info["Qtd. Total"],
                        info["UG"],
                        info["Tipo UASG"],
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
                else:
                    if unidades_participantes_inner_table_ref:
                        # Loop para cada linha de unidade participante, criando um registro distinto para cada
                        for row in unidades_participantes_inner_table_ref.find_all('tr')[1:]: # Ignora a linha de cabeçalho da tabela interna
                            cols = [td.get_text(strip=True) for td in row.find_all('td')]
                            
                            # Garante que a linha tem colunas suficientes para extrair os dados
                            if cols and len(cols) >= 4: # Verifica se há pelo menos 4 colunas (0, 1, 2, 3)

                                #ug_current_row = cols[0] # "Unidade" (Ex: "160482 - CMDO 1A BDA INF SL")

                                #qtd_autorizada_current_row = cols[2] # "Qtd. autorizada"
                                #qtd_saldo_current_row = cols[3] # "Qtd. Saldo" (assumindo que o seu HTML se alinha com isso)

                                # Cria a 'linha' usando as informações comuns (info) e as específicas da unidade

                                info["UG"] = cols[0][0:6]
                                info["Tipo UASG"] = cols[1]
                                info["Qtd. Autorizada"] = cols[2]
                                info["Qtd. Saldo"] = cols[3]

                                linha = [
                                    info["Número"],
                                    info["Tipo Item"],
                                    info["Descrição"],
                                    info["Descrição detalhada"],
                                    info["Qtd. Total"],
                                    info["UG"],
                                    info["Tipo UASG"],
                                    info["Qtd. Autorizada"],
                                    info["Qtd. Saldo"],
                                    info["Fornecedor"],
                                    info["Val_unit"],
                                    info["Val_neg"],
                                    info["Número Ata"],
                                    info["Vigência Fim"]
                                ]
                                dados.append(linha) # Adiciona esta linha ao array 'dados'

                # ATUALIZA A BARRA DE PROGRESSO
                progresso_atual = (idx + 1) / total_itens
                progress_callback(progresso_atual)


            titulos = [
                "Número",
                "Tipo Item",
                "Descrição",
                "Descrição detalhada",
                "Qtd. Total",
                "UG",
                "Tipo UASG",
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

            # ATUALIZA A BARRA DE PROGRESSO
            progress_callback(0)
            
            fim = time.time()
            tempo_execucao = fim - inicio
            print(f"O script foi executado em: {tempo_execucao:.4f} segundos")
      

    except Exception as e:
        print(f"[ERRO] {e}")

    finally:
        # Chama o callback de finalização, aconteça o que acontecer
        completion_callback()
# --- FIM: SCRIPT DE EXTRAÇÃO DE DADOS ---


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurações da Janela Principal ---
        self.title("Assistente de Login e Extração")
        self.geometry("500x600") # Aumentei a altura para a nova tela
        ctk.set_appearance_mode("dark")

        self.driver = None
        # --- Container principal ---
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Criação dos frames (telas) ---
        self.tela1 = ctk.CTkFrame(self.container)
        self.tela2 = ctk.CTkFrame(self.container)
        self.tela3 = ctk.CTkFrame(self.container)
        self.tela4 = ctk.CTkFrame(self.container) # TELA 4
        self.tela5 = ctk.CTkFrame(self.container) # TELA 5

        # --- NOVO: Variáveis para armazenar as seleções da tela 3 ---
        self.tipo_pregao_var = ctk.StringVar(value="1")
        self.tipo_ug_var = ctk.StringVar(value="1")
        self.ug_unica_var = ctk.StringVar()

        # Variáveis para os labels informativos da Tela 4
        self.info_pregao_var = ctk.StringVar()
        self.info_ug_var = ctk.StringVar()
        self.info_ug_unica_var = ctk.StringVar()
        self.pregao_atual = ctk.StringVar()

        # --- Chama os métodos para criar os widgets de todas as telas ---
        self.criar_widgets_tela1()
        self.criar_widgets_tela2()
        self.criar_widgets_tela3() # NOVO: Chamada para criar a tela 3
        self.criar_widgets_tela4() # Chamada para criar a tela 4
        self.criar_widgets_tela5() # Chamada para criar a tela 5

        # --- Inicia mostrando a primeira tela ---
        self.mostrar_tela(self.tela1)
        
        self.protocol("WM_DELETE_WINDOW", self.ao_fechar)

# --- CRIAÇÃO WIDGETS TELAS---
    def criar_widgets_tela1(self):
        # ... (Este método permanece inalterado)
        self.tela1.pack_propagate(False)
        titulo_tela1 = ctk.CTkLabel(self.tela1, text="Passo 1: Iniciar Login", font=ctk.CTkFont(size=24, weight="bold"))
        titulo_tela1.pack(pady=(20, 10))
        texto_explicativo1 = ctk.CTkLabel(self.tela1, text="Ao clicar em 'Continuar', um navegador será aberto.\nPor favor, realize o login manualmente na página que aparecer.", wraplength=400, justify="center")
        texto_explicativo1.pack(pady=10, padx=20)
        self.botao_continuar = ctk.CTkButton(self.tela1, text="Continuar", command=self.ir_para_tela2)
        self.botao_continuar.pack(pady=20, ipadx=10)

    def criar_widgets_tela2(self):
        # ALTERADO: O texto e o comando do botão foram atualizados.
        self.tela2.pack_propagate(False)
        titulo_tela2 = ctk.CTkLabel(self.tela2, text="Passo 2: Navegação", font=ctk.CTkFont(size=24, weight="bold"))
        titulo_tela2.pack(pady=(20, 10))
        texto_explicativo2 = ctk.CTkLabel(self.tela2, text="Após fazer o login, navegue até a página exata de onde os dados devem ser extraídos. Quando a página estiver aberta, clique no botão abaixo.", wraplength=400, justify="center")
        texto_explicativo2.pack(pady=10, padx=20)
        self.botao_confirmar = ctk.CTkButton(self.tela2, text="Confirmar e Avançar", command=self.ir_para_tela3)
        self.botao_confirmar.pack(pady=20, ipadx=10)

    def criar_widgets_tela3(self):
        """Cria os componentes gráficos da terceira tela, com a nova lógica de UG."""
        self.tela3.pack_propagate(False)

        label_titulo = ctk.CTkLabel(self.tela3, text="Passo 3: Configurar Extração", font=ctk.CTkFont(size=24, weight="bold"))
        label_titulo.pack(pady=(20, 10))
        
        # --- Seção de Pregões (permanece igual) ---
        label_pregao = ctk.CTkLabel(self.tela3, text="Tipo de Extração (Pregão):", font=ctk.CTkFont(weight="bold"))
        label_pregao.pack(pady=(10, 5), padx=20, anchor="w")
        radio_pregao1 = ctk.CTkRadioButton(self.tela3, text="Um Pregão", variable=self.tipo_pregao_var, value="1", command=self.gerenciar_visibilidade_textbox_pregoes)
        radio_pregao1.pack(pady=2, padx=20, anchor="w")
        radio_pregao2 = ctk.CTkRadioButton(self.tela3, text="Múltiplos Pregões", variable=self.tipo_pregao_var, value="2", command=self.gerenciar_visibilidade_textbox_pregoes)
        radio_pregao2.pack(pady=2, padx=20, anchor="w")
        self.textbox_pregoes_label = ctk.CTkLabel(self.tela3, text="Liste aqui os links dos pregões, um por linha.\nO link deve terminar em /XXXXXX/itens", font=ctk.CTkFont(weight="bold"))
        self.textbox_pregoes = ctk.CTkTextbox(self.tela3, height=160)

        # --- Seção de UGs (ALTERADA) ---
        label_ug = ctk.CTkLabel(self.tela3, text="Tipo de Extração (UG):", font=ctk.CTkFont(weight="bold"))
        label_ug.pack(pady=(15, 5), padx=20, anchor="w")
        
        # NOVO: Frame para alinhar o rádio e a caixa de texto horizontalmente
        frame_ug_unica = ctk.CTkFrame(self.tela3, fg_color="transparent")
        frame_ug_unica.pack(fill="x", padx=20, pady=2)
        
        radio_ug1 = ctk.CTkRadioButton(frame_ug_unica, text="Uma UG", variable=self.tipo_ug_var, value="1", command=self.gerenciar_visibilidade_entry_ug)
        radio_ug1.pack(side="left")

        # NOVO: Caixa de texto para a UG única
        self.entry_ug = ctk.CTkEntry(frame_ug_unica, placeholder_text="Digite a UG", textvariable=self.ug_unica_var)
        # O .pack() será chamado pelo método de controle de visibilidade
        
        radio_ug2 = ctk.CTkRadioButton(self.tela3, text="Múltiplas UGs", variable=self.tipo_ug_var, value="2", command=self.gerenciar_visibilidade_entry_ug)
        radio_ug2.pack(pady=2, padx=20, anchor="w")

        # --- Botão Final ---
        self.botao_extrair = ctk.CTkButton(self.tela3, text="Continuar e Extrair Dados", command=self.iniciar_extracao)
        self.botao_extrair.pack(pady=20, side="bottom")

        # Chama a função de visibilidade uma vez no início para garantir o estado correto
        self.gerenciar_visibilidade_entry_ug()
    
    # NOVO: Método que cria a tela de processamento.
    def criar_widgets_tela4(self):
        self.tela4.pack_propagate(False)
        ctk.CTkLabel(self.tela4, text="Passo 4: Processando", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(20, 10))
        frame_sumario = ctk.CTkFrame(self.tela4)
        frame_sumario.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(frame_sumario, text="Tipo de Pregão:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ctk.CTkLabel(frame_sumario, textvariable=self.info_pregao_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)

        ctk.CTkLabel(frame_sumario, text="Tipo de UG:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ctk.CTkLabel(frame_sumario, textvariable=self.info_ug_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.label_ug_unica_titulo = ctk.CTkLabel(frame_sumario, text="UG Única:", font=ctk.CTkFont(weight="bold"))
        self.label_ug_unica_valor = ctk.CTkLabel(frame_sumario, textvariable=self.info_ug_unica_var)

        ctk.CTkLabel(frame_sumario, text="Múltiplos Pregões:", font=ctk.CTkFont(weight="bold")).grid(row=3, column=0, sticky="nw", padx=5, pady=2)
        self.textbox_sumario_pregoes = ctk.CTkTextbox(frame_sumario, height=80, fg_color="transparent", activate_scrollbars=False)
        self.textbox_sumario_pregoes.grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        ctk.CTkLabel(frame_sumario, text="Pregão Atual:", font=ctk.CTkFont(weight="bold")).grid(row=4, column=0, sticky="w", padx=5, pady=2)
        ctk.CTkLabel(frame_sumario, textvariable=self.pregao_atual).grid(row=4, column=1, sticky="w", padx=5, pady=2)

        frame_sumario.grid_columnconfigure(1, weight=1)
        
        self.label_status = ctk.CTkLabel(self.tela4, text="Extração em andamento...", font=ctk.CTkFont(weight="bold"))
        self.label_status.pack(pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(self.tela4)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10, padx=20, fill="x")

    # NOVO: Método que cria a tela final.
    def criar_widgets_tela5(self):
        self.tela5.pack_propagate(False)
        ctk.CTkLabel(self.tela5, text="Extração concluída com sucesso!", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(80, 20))
        ctk.CTkLabel(self.tela5, text="O que você deseja fazer agora?").pack(pady=10)
        frame_botoes = ctk.CTkFrame(self.tela5, fg_color="transparent")
        frame_botoes.pack(pady=20)
        ctk.CTkButton(frame_botoes, text="Nova Consulta", command=self.preparar_nova_consulta).pack(side="left", padx=10, ipadx=10)
        ctk.CTkButton(frame_botoes, text="Sair", fg_color="#DB3E39", hover_color="#C22722", command=self.ao_fechar).pack(side="left", padx=10, ipadx=10)
        
# --- MÉTODOS DE CONTROLE DA APLICAÇÃO ---
    def gerenciar_visibilidade_textbox_pregoes(self):
        if self.tipo_pregao_var.get() == "2":
            self.textbox_pregoes_label.pack(pady=5, padx=20, fill="x", anchor="w")
            self.textbox_pregoes.pack(pady=5, padx=20, fill="x", anchor="w")
        else:
            self.textbox_pregoes_label.pack_forget()
            self.textbox_pregoes.pack_forget()

    def gerenciar_visibilidade_entry_ug(self):
        """Mostra ou oculta a caixa de texto para Uma UG."""
        if self.tipo_ug_var.get() == "1":
            # Exibe a caixa de texto ao lado do radio button
            self.entry_ug.pack(side="left", padx=10, fill="x", expand=True)
        else:
            # Oculta a caixa de texto e limpa seu conteúdo
            self.entry_ug.pack_forget()
            self.ug_unica_var.set("")

    # NOVO: Callback para atualizar a barra de progresso.
    def atualizar_progresso(self, valor):
        self.progress_bar.set(valor)

    # NOVO: Callback para atualizar o pregao extraído.
    def atualizar_pregao(self, valor):
        self.pregao_atual.set(valor)

    # NOVO: Função para ser chamada no final da extração.
    def finalizar_extracao(self):
        self.label_status.configure(text="Extração Concluída!")
        self.mostrar_tela(self.tela5)

    def preparar_nova_consulta(self):
        print("[+] Preparando para uma nova consulta...")
        self.botao_extrair.configure(state="normal", text="Continuar e Extrair Dados")
        self.progress_bar.set(0) # Reseta a barra de progresso
        self.label_status.configure(text="Extração em andamento...") # Reseta o status
        self.mostrar_tela(self.tela3)

    def mostrar_tela(self, tela_para_mostrar):
        for tela in [self.tela1, self.tela2, self.tela3, self.tela4, self.tela5]:
            tela.pack_forget()
        tela_para_mostrar.pack(fill="both", expand=True)

    def iniciar_navegador_em_thread(self):
        """Inicia o UC usando uma pasta de perfil persistente e tamanho definido."""
        print("[+] Iniciando o navegador...")
        try:
            options = uc.ChromeOptions()
            options.add_argument(f'--user-data-dir={profile_path}')
            
            print(f"[+] Usando perfil do Chrome em: {profile_path}")
            
            # ALTERADO: Passa as opções ao criar a instância do Chrome
            self.driver = uc.Chrome(options=options)
            self.driver.set_window_size(1350,720)
            
            # !!! Lembre-se de alterar para a URL de login correta !!!
            self.driver.get("https://contratos.sistema.gov.br/compras/") 
            print("[+] Navegador pronto para o login manual.")

        except Exception as e:
            print(f"[!] Erro ao iniciar o navegador: {e}")

    def ir_para_tela2(self):
        # ... (Este método permanece inalterado)
        self.botao_continuar.configure(state="disabled", text="Aguarde...")
        threading.Thread(target=self.iniciar_navegador_em_thread).start()
        self.mostrar_tela(self.tela2)

    def ir_para_tela3(self):
        if self.driver:
            print("[+] Login confirmado, indo para a tela de configurações.")
            self.mostrar_tela(self.tela3)
        else:
            print("[!] Erro: O navegador não foi iniciado corretamente.")

# --- INICIA A EXTRAÇÃO DOS DADOS ---
    def iniciar_extracao(self):
        """Coleta todos os dados da tela 3 e chama a função de extração."""
        self.botao_extrair.configure(state="disabled", text="Extraindo...")
        
        tipo_pregao = self.tipo_pregao_var.get()
        tipo_ug = self.tipo_ug_var.get()
        lista_pregoes = [l.strip() for l in self.textbox_pregoes.get("1.0", "end-1c").split('\n') if l.strip()] if tipo_pregao == "2" else []
        ug_unica = self.ug_unica_var.get() if tipo_ug == "1" else ""

        if tipo_pregao == "1":
            self.info_pregao_var.set("Extraindo Pregão ÚNICO")
        else:
            self.info_pregao_var.set("Extraindo LISTA Pregões")
        
        if tipo_ug == "1":
            self.info_ug_var.set("Extraindo UMA UG")
        else:
            self.info_ug_var.set("Extraindo TODAS UGs")

        if ug_unica:
            self.info_ug_unica_var.set(ug_unica)
            self.label_ug_unica_titulo.grid(row=2, column=0, sticky="w", padx=5, pady=2)
            self.label_ug_unica_valor.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        else:
            self.label_ug_unica_titulo.grid_forget()
            self.label_ug_unica_valor.grid_forget()
        self.textbox_sumario_pregoes.delete("1.0", "end")
        if lista_pregoes: self.textbox_sumario_pregoes.insert("1.0", "\n".join(lista_pregoes))

        self.mostrar_tela(self.tela4)

        threading.Thread(target=extrair_dados_do_site, args=(self.driver, tipo_pregao, tipo_ug, lista_pregoes, ug_unica, self.atualizar_progresso, self.atualizar_pregao, self.finalizar_extracao)).start()

# --- ENCERRA A EXECUÇÃO
    def ao_fechar(self):
        # ... (Este método permanece inalterado)
        print("[+] Fechando a aplicação...")
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                print(f"[*] O navegador já estava fechado ou houve um erro ao fechar: {e}")
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()