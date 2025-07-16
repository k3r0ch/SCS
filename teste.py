import customtkinter as ctk
import sys
import webbrowser
from PIL import Image
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
from bs4 import BeautifulSoup
import pandas as pd
import re
import os

ug_ext = 999999

class App(ctk.CTk):
    # --- Configurações da Aparência ---
    # Modos: "System" (padrão do sistema), "Dark", "Light"
    
    # Temas: "blue" (padrão), "green", "dark-blue"
    ctk.set_appearance_mode("Dark")
    
    def __init__(self):
        super().__init__()
        # --- Criação da Janela Principal ---
        self.geometry("640x360")
        self.title("SCS")
        # Impede que a janela seja redimensionada
        self.resizable(False, False)

        self.options = uc.ChromeOptions()
        self.driver = uc.Chrome(options=self.options)
        self.URL = "https://contratos.sistema.gov.br/transparencia/compras?modalidade_id=76&modalidade_id_text=05+-+Pregão"

        self.driver.get(self.URL)

        # --- Criação Telas ---
        self.pagina_inicial = PaginaInicial(self)
        self.confirmar_login = ConfirmarLogin(self)

        self.showFrame(self.pagina_inicial)

    def showFrame(self, frame_to_show):
        for frame in [self.pagina_inicial, self.confirmar_login]:
            frame.pack_forget() # Hide all frames
        frame_to_show.pack(fill="both", expand=True) # Show the desired frame

class PaginaInicial(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        # --- Criação dos Widgets (Componentes Gráficos) ---
        # 1. Título "BEM VINDO"
        # Usamos uma fonte maior e em negrito para destaque.
        # O `pady` adiciona um espaçamento vertical (20 pixels acima, 10 abaixo).
        self.label_titulo = ctk.CTkLabel(
            master=self, 
            text="BEM VINDO", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 10), padx=10)

        # 2. Texto Explicativo
        # O `\n` cria uma quebra de linha para o texto se ajustar melhor.
        self.label_descricao = ctk.CTkLabel(
            master=self,
            text="Interface de exemplo para\ninteragir com o programa.",
            justify="center" # Garante que o texto de múltiplas linhas fique centralizado
        )
        self.label_descricao.pack(pady=0, padx=10)

        # 3. Botões de Ação
        # Criamos um frame invisível para agrupar os botões lado a lado.
        self.frame_botoes = ctk.CTkFrame(master=self,fg_color="transparent")
        self.frame_botoes.pack(pady=20)

        # Botão 1
        self.botao_1 = ctk.CTkButton(master=self.frame_botoes, text="Tutorial", command=self.tutorial)
        self.botao_1.pack(side="left", padx=5)

        # Botão 2
        self.botao_2 = ctk.CTkButton(master=self.frame_botoes, text="Iniciar", command=lambda: [master.showFrame(master.confirmar_login)])
        self.botao_2.pack(side="left", padx=5)

        # Botão 3
        self.botao_3 = ctk.CTkButton(master=self.frame_botoes, text="SAIR", command=self.fechar_programa)
        self.botao_3.pack(side="left", padx=5)

        # 4. Rodapé com Copyright
        # Usamos `side="bottom"` para fixá-lo na parte inferior da janela.
        self.label_copyright = ctk.CTkLabel(
            master=self,
            text="Ten QUEIROZ © 2025",
            font=ctk.CTkFont(size=9)
        )
        self.label_copyright.pack(side="bottom", pady=5)

    def fechar_programa(self):
        #driver.quit()
        sys.exit()
    
    def tutorial(self):
        webbrowser.open_new("https://github.com/k3r0ch/SCS")
        
class ConfirmarLogin(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        self.label_titulo = ctk.CTkLabel(
            master=self, 
            text="LOGIN", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.label_titulo.pack(pady=(20, 10), padx=10)

        # 2. Texto Explicativo
        # O `\n` cria uma quebra de linha para o texto se ajustar melhor.
        self.frame_label = ctk.CTkFrame(master=self,fg_color="transparent",width=384)
        self.frame_label.pack(pady=20)

        self.label_descricao = ctk.CTkLabel(
            master=self.frame_label,
            text="Realize o Login na tela de Contratos, seguindo todos os passos necessários do GOV.br\n assim como geralmente realiza.",
            justify="center" # Garante que o texto de múltiplas linhas fique centralizado
        )
        self.label_descricao.pack(pady=0, padx=10)

        # 3. IMAGENS
        # O `\n` cria uma quebra de linha para o texto se ajustar melhor.
        self.frame_image = ctk.CTkFrame(master=self,fg_color="transparent")
        self.frame_image.pack(pady=5)

        imagem_login = ctk.CTkImage(light_image=Image.open('images/login.png'),dark_image=Image.open('images/login.png'),size=(229,122))
        self.label_imagemLogin = ctk.CTkLabel(master=self.frame_image, text="", image=imagem_login)
        self.label_imagemLogin.pack(side="left",pady=0, padx=10)

        imagem_login2 = ctk.CTkImage(light_image=Image.open('images/login2.png'),dark_image=Image.open('images/login2.png'),size=(229,122))
        self.label_imagemLogin2 = ctk.CTkLabel(master=self.frame_image, text="", image=imagem_login2)
        self.label_imagemLogin2.pack(side="left",pady=0, padx=10)

        # 3. Botões de Ação
        # Criamos um frame invisível para agrupar os botões lado a lado.
        self.frame_botoes = ctk.CTkFrame(master=self,fg_color="transparent")
        self.frame_botoes.pack(pady=20)

        # Botão 1
        self.botao_1 = ctk.CTkButton(master=self.frame_botoes, text="⇦ Voltar", command=lambda: master.showFrame(master.pagina_inicial))
        self.botao_1.pack(side="left", padx=5)

        # Botão 2
        self.botao_2 = ctk.CTkButton(master=self.frame_botoes, text="Login Feito", command= self.consultar_Saldos(master.driver))
        self.botao_2.pack(side="left", padx=5)

        # 4. Rodapé com Copyright
        # Usamos `side="bottom"` para fixá-lo na parte inferior da janela.
        self.label_copyright = ctk.CTkLabel(
            master=self,
            text="Ten QUEIROZ © 2025",
            font=ctk.CTkFont(size=9)
        )
        self.label_copyright.pack(side="bottom", pady=5)

    
    def consultar_Saldos(self, driver):
        try:
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
            fim = time.time()
            tempo_execucao = fim - inicio
            print(f"O script foi executado em: {tempo_execucao:.4f} segundos")

        except Exception as e:
                print(f"[ERRO] {e}")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()