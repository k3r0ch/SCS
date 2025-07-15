import customtkinter as ctk
import sys
import webbrowser
from PIL import Image

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
        self.botao_2 = ctk.CTkButton(master=self.frame_botoes, text="Iniciar", command=lambda: master.showFrame(master.confirmar_login))
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
        self.botao_2 = ctk.CTkButton(master=self.frame_botoes, text="Login Feito")
        self.botao_2.pack(side="left", padx=5)

        # 4. Rodapé com Copyright
        # Usamos `side="bottom"` para fixá-lo na parte inferior da janela.
        self.label_copyright = ctk.CTkLabel(
            master=self,
            text="Ten QUEIROZ © 2025",
            font=ctk.CTkFont(size=9)
        )
        self.label_copyright.pack(side="bottom", pady=5)

if __name__ == "__main__":
    app = App()
    app.mainloop()