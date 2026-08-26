import tkinter as tk
from tkinter import messagebox

from src.config.settings import PRODUTOS_CORRETORA
from src.controllers.converter_controller import processar_conversao_json
from src.services.formatacao_service import gerar_relatorio_formatacao


class AppConversorTkinter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conversor Json -> Goalfy")
        self.iconbitmap("raio.ico")
        self.geometry("850x750")
        self.resizable(True, True)

        # Configura o fundo da janela principal para preto/escuro
        self.configure(bg="#0e1117")

        # Estado da Aplicação
        self.lote_jsons = []

        self.criar_interface()

    def criar_interface(self):
        # Frame Principal Dark
        self.main_frame = tk.Frame(self, padx=15, pady=15, bg="#0e1117")
        self.main_frame.pack(fill="both", expand=True)

        # 1. Título e Subtítulo
        tk.Label(
            self.main_frame,
            text="⚡ EXTRAÇÃO DOS LEADS",
            font=("Arial", 16, "bold"),
            fg="#00d4ff",
            bg="#0e1117",
        ).pack(anchor="w")

        subtitulo = (
            "Acumule as páginas colando o JSON e clicando em Próxima Página. "
            "Ao terminar, clique em Salvar Lote na Matriz."
        )
        tk.Label(
            self.main_frame,
            text=subtitulo,
            font=("Arial", 9),
            fg="#b0b3b8",
            bg="#0e1117",
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(2, 10))

        # 2. Seleção de Produto (Estilizado Dark)
        tk.Label(
            self.main_frame,
            text="PRODUTO:",
            font=("Arial", 9, "bold"),
            fg="#ffffff",
            bg="#0e1117",
        ).pack(anchor="w")

        lista_produtos = (
            list(PRODUTOS_CORRETORA)
            if isinstance(PRODUTOS_CORRETORA, (list, dict, tuple))
            else []
        )

        self.var_produto = tk.StringVar(self)
        if lista_produtos:
            self.var_produto.set(lista_produtos[0])

        # Menu suspenso estilizado em Dark Mode
        self.opt_produto = tk.OptionMenu(
            self.main_frame, self.var_produto, *lista_produtos
        )
        self.opt_produto.config(
            bg="#262730",
            fg="#ffffff",
            activebackground="#0056b3",
            activeforeground="#ffffff",
            highlightthickness=0,
            bd=1,
            relief="flat",
            font=("Arial", 9, "bold"),
            anchor="w",
            width=55,
        )

        # Estiliza a lista que abre ao clicar (dropdown real)
        menu = self.opt_produto["menu"]
        menu.config(
            bg="#262730",
            fg="#ffffff",
            activebackground="#007bff",
            activeforeground="#ffffff",
            font=("Arial", 9),
        )
        self.opt_produto.pack(anchor="w", pady=(2, 10))

        # 3. Contador Visual de Lote Acumulado (Verde Neon/Dark)
        self.lbl_contador = tk.Label(
            self.main_frame,
            text="",
            font=("Arial", 9, "bold"),
            bg="#1c3b2b",
            fg="#00ff66",
            padx=10,
            pady=5,
        )

        # 4. Campo de Texto (JSON)
        tk.Label(
            self.main_frame,
            text="Cole o JSON da página atual aqui:",
            font=("Arial", 9, "bold"),
            fg="#ffffff",
            bg="#0e1117",
        ).pack(anchor="w")

        self.txt_json = tk.Text(
            self.main_frame,
            height=9,
            width=78,
            bg="#262730",
            fg="#ffffff",
            insertbackground="white",  # Cursor piscante branco
            relief="flat",
        )
        self.txt_json.pack(fill="x", pady=(2, 10))

        # 5. Botões de Ação
        frame_botoes = tk.Frame(self.main_frame, bg="#0e1117")
        frame_botoes.pack(fill="x", pady=(0, 10))

        btn_proxima = tk.Button(
            frame_botoes,
            text="➡️ Próxima Página (Acumular)",
            command=self.cb_adicionar_e_proxima,
            bg="#17a2b8",
            fg="white",
            font=("Arial", 9, "bold"),
            pady=5,
            relief="flat",
        )
        btn_proxima.pack(side="left", fill="x", expand=True, padx=(0, 3))

        btn_salvar = tk.Button(
            frame_botoes,
            text="🚀 Salvar Lote na Matriz",
            command=self.cb_salvar_lote,
            bg="#28a745",
            fg="white",
            font=("Arial", 9, "bold"),
            pady=5,
            relief="flat",
        )
        btn_salvar.pack(side="left", fill="x", expand=True, padx=3)

        btn_reset = tk.Button(
            frame_botoes,
            text="🗑️ Resetar",
            command=self.cb_limpar_tudo,
            bg="#dc3545",
            fg="white",
            font=("Arial", 9, "bold"),
            pady=5,
            relief="flat",
        )
        btn_reset.pack(side="left", fill="x", expand=True, padx=(3, 0))

        # 6. Área de Resultados Visual (Terminal/Console Dark)
        tk.Label(
            self.main_frame,
            text="STATUS E RESULTADOS:",
            font=("Arial", 9, "bold"),
            fg="#ffffff",
            bg="#0e1117",
        ).pack(anchor="w", pady=(5, 2))

        self.txt_resultado = tk.Text(
            self.main_frame,
            height=10,
            width=78,
            bg="#14171d",
            fg="#00ff66",  # Texto estilo console/matrix
            insertbackground="white",
            state="disabled",
            relief="flat",
        )
        self.txt_resultado.pack(fill="both", expand=True)

    # --- LÓGICA DE CALLBACKS ---

    def atualizar_contador(self):
        qtd = len(self.lote_jsons)
        if qtd > 0:
            self.lbl_contador.config(
                text=f"📦 {qtd} página(s) de JSON acumulada(s) na fila prontas para salvar."
            )
            self.lbl_contador.pack(anchor="w", pady=(0, 10))
        else:
            self.lbl_contador.pack_forget()

    def escrever_log(self, mensagem):
        self.txt_resultado.config(state="normal")
        self.txt_resultado.insert(tk.END, mensagem + "\n")
        self.txt_resultado.see(tk.END)
        self.txt_resultado.config(state="disabled")

    def limpar_log(self):
        self.txt_resultado.config(state="normal")
        self.txt_resultado.delete("1.0", tk.END)
        self.txt_resultado.config(state="disabled")

    def cb_adicionar_e_proxima(self):
        texto = self.txt_json.get("1.0", tk.END).strip()
        if texto:
            self.lote_jsons.append(texto)
            self.txt_json.delete("1.0", tk.END)
            self.atualizar_contador()
            self.escrever_log(f"ℹ️ Página {len(self.lote_jsons)} adicionada à fila.")
        else:
            messagebox.showwarning("Aviso", "Cole o JSON da página antes de acumular.")

    def cb_limpar_tudo(self):
        self.lote_jsons = []
        self.txt_json.delete("1.0", tk.END)
        self.atualizar_contador()
        self.limpar_log()
        self.escrever_log("🗑️ Fila e estado resetados com sucesso.")

    def cb_salvar_lote(self):
        produto = self.var_produto.get()

        texto = self.txt_json.get("1.0", tk.END).strip()
        if texto:
            self.lote_jsons.append(texto)
            self.txt_json.delete("1.0", tk.END)
            self.atualizar_contador()

        if not self.lote_jsons:
            messagebox.showerror(
                "Erro", "Nenhum JSON foi acumulado ainda. Cole um JSON antes de salvar."
            )
            return

        self.limpar_log()
        self.escrever_log("⚙️ Processando lote de JSONs...")

        total_salvos = 0
        total_ignorados = 0
        todos_duplicados = []
        todos_registros_acumulados = []
        caminho_dropbox = ""

        for json_str in self.lote_jsons:
            res = processar_conversao_json(json_str, produto)
            if res.get("sucesso"):
                total_salvos += res.get("salvos", 0)
                total_ignorados += res.get("ignorados_status", 0)
                todos_duplicados.extend(res.get("duplicados", []))
                caminho_dropbox = res.get("caminho_arquivo", "")

                if "registros_validos" in res:
                    todos_registros_acumulados.extend(res["registros_validos"])

        caminho_formatacao = None
        if todos_registros_acumulados:
            caminho_formatacao = gerar_relatorio_formatacao(
                todos_registros_acumulados, produto
            )

        self.escrever_log("----------------------------------------")
        self.escrever_log(
            f"✅ Processamento concluído! Total de {total_salvos} registro(s) salvo(s)!"
        )

        if caminho_dropbox:
            self.escrever_log(f"📁 Dropbox: {caminho_dropbox}")

        if caminho_formatacao:
            self.escrever_log(f"🖥️ Planilha de Formatação criada:\n{caminho_formatacao}")
        else:
            self.escrever_log(
                "⚠️ Planilha de formatação não gerada (nenhum registro válido)."
            )

        if total_ignorados > 0:
            self.escrever_log(
                f"ℹ️ {total_ignorados} registro(s) ignorados (Status GDO diferente de 7)."
            )

        if todos_duplicados:
            self.escrever_log(f"⚠️ {len(todos_duplicados)} registro(s) duplicado(s):")
            for dup in todos_duplicados:
                self.escrever_log(f"  - ID: {dup['id']} | Cliente: {dup['nome']}")

        self.lote_jsons = []
        self.atualizar_contador()


if __name__ == "__main__":
    app = AppConversorTkinter()
    app.mainloop()
