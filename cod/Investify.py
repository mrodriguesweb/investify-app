import calendar
import urllib
from urllib import error
from tkinter import *
from tkinter import messagebox, Button, filedialog, ttk
import tkinter as tk
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import csv
import requests
import datetime
import yfinance as yf
import pandas as pd
import PyPDF2
import mimetypes
import os

# Cria a instancia do App
app = tk.Tk()
app.geometry('1400x1400')
app.title('Investify - Controle seus Investimentos')

# Carrega a imagem
bg_image = Image.open("img/background/background_white.png")
# Redimensiona a imagem para o tamanho da janela
bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))
# Converte a imagem para o formato compatível com Tkinter
bg_image_tk = ImageTk.PhotoImage(bg_image)

bg_image_nologo = Image.open("img/background/background_white_nologo.png")
# Redimensiona a imagem para o tamanho da janela
bg_image_nologo = bg_image_nologo.resize((app.winfo_screenwidth(), app.winfo_screenheight()))
# Converte a imagem para o formato compatível com Tkinter
bg_image_tk_nologo = ImageTk.PhotoImage(bg_image_nologo)

# SQLLite
con = sqlite3.connect('investimentos.db')

cur = con.cursor()

# -------------------------------------- Cria as tabelas -------------------------------------- #

def trata_str_emp(string):
    nova_str = str(string).replace("[", "").replace("'", "").replace("]", "").replace("{", "").replace("}", "").replace(")", "").replace("(", "").replace(",", "").strip()

    return nova_str


nomes_tabelas = ["EMPRESA", "COMPRA", "POSICAO", "COMPRATESOURO", "POSICAOTESOURO", "TEMPTITULOS", "TITULO", "FII"]

for tabela in nomes_tabelas:
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabela}'")
    tabela_existe = cur.fetchone()

    if not tabela_existe:

        if tabela == "EMPRESA":
            cur.execute("CREATE TABLE EMPRESA (ID INTEGER PRIMARY KEY AUTOINCREMENT, NOME TEXT NOT NULL, TICKER TEXT NOT NULL, SETOR TEXT NOT NULL, DESCRICAO TEXT NOT NULL)")

            with open('files/Empresas.CSV', 'r') as arquivo:

                linhas = csv.reader(arquivo)

                lista_csv = list(linhas)

            arquivo.close()

            lista_csv.pop(0)

            lst_empresas = []
            lst_ticker = []
            lst_setor = []
            lst_descricao = []

            for registro in lista_csv:

                emp = str(registro).split(";")[0]
                lst_empresas.append(trata_str_emp(emp))

                tick = str(registro).split(";")[1]
                lst_ticker.append(trata_str_emp(tick))

                setor = str(registro).split(";")[3]
                lst_setor.append(trata_str_emp(setor))

                descricao = str(registro).split(";")[4]
                lst_descricao.append(trata_str_emp(descricao))

            for i in range(0, len(lst_empresas)):
                cur.execute('insert into EMPRESA(NOME, TICKER, SETOR, DESCRICAO) values(?, ?, ?, ?)', (lst_empresas[i], lst_ticker[i], lst_setor[i], lst_descricao[i]))
                con.commit()

        elif tabela == "FII":
            cur.execute("CREATE TABLE FII (ID INTEGER PRIMARY KEY AUTOINCREMENT, RZSOCIAL TEXT NOT NULL, NOME TEXT NOT NULL, TICKER TEXT NOT NULL)")

            with open('files/fundosListados.CSV', 'r') as arquivo:

                linhas = csv.reader(arquivo)

                lista_csv = list(linhas)

            arquivo.close()

            lista_csv.pop(0)

            lst_rzsocial = []
            lst_nome = []
            lst_ticker = []

            for registro in lista_csv:

                rzsoc = str(registro).split(";")[0]
                lst_rzsocial.append(trata_str_emp(rzsoc))

                nome = str(registro).split(";")[1]
                lst_nome.append(trata_str_emp(nome))

                tick = str(registro).split(";")[3]
                lst_ticker.append(trata_str_emp(tick))

            for i in range(0, len(lst_rzsocial)):
                cur.execute('insert into FII(RZSOCIAL, NOME, TICKER) values(?, ?, ?)', (lst_rzsocial[i], lst_nome[i], lst_ticker[i]))
                con.commit()

        elif tabela == "COMPRA":
            cur.execute("CREATE TABLE COMPRA (COMPRA_ID INTEGER PRIMARY KEY AUTOINCREMENT, DATA TEXT NOT NULL, VALOR_ACAO REAL NOT NULL, QUANTIDADE INTEGER NOT NULL, UTICKER TEXT NOT NULL, FONTE TEXT NOT NULL, ID INTEGER, FID INTEGER, FOREIGN KEY (ID) REFERENCES EMPRESA (ID), FOREIGN KEY (FID) REFERENCES FII (ID))")

        elif tabela == "POSICAO":
            cur.execute("CREATE TABLE POSICAO (POSICAO_ID INTEGER PRIMARY KEY AUTOINCREMENT, RISCO INTEGER NOT NULL, DEFINICAO TEXT NOT NULL, VALORTOTAL REAL NOT NULL, PRECOMEDIO REAL NOT NULL, PAPEISTOTAIS INTEGER NOT NULL, UTICKER TEXT NOT NULL, ID INTEGER, FID INTEGER, FOREIGN KEY (ID) REFERENCES EMPRESA (ID), FOREIGN KEY (FID) REFERENCES FII (ID))")

        elif tabela == "COMPRATESOURO":
            cur.execute("CREATE TABLE COMPRATESOURO (COMPRAT_ID INTEGER PRIMARY KEY AUTOINCREMENT, DATA TEXT NOT NULL, VALOR_TIT REAL NOT NULL, QUANTIDADE INTEGER NOT NULL, TIT_ID INTEGER NOT NULL, FOREIGN KEY (TIT_ID) REFERENCES TITULO (TIT_ID))")

        elif tabela == "POSICAOTESOURO":
            cur.execute("CREATE TABLE POSICAOTESOURO (POSICAOT_ID INTEGER PRIMARY KEY AUTOINCREMENT, RISCO INTEGER NOT NULL, DEFINICAO TEXT NOT NULL, VALORTOTAL REAL NOT NULL, PAPEISTOTAIS INTEGER NOT NULL, TIT_ID INTEGER NOT NULL, FOREIGN KEY (TIT_ID) REFERENCES TITULO (TIT_ID))")

        elif tabela == "TEMPTITULOS":
            cur.execute("CREATE TABLE TEMPTITULOS (TMP_TIT_ID INTEGER PRIMARY KEY AUTOINCREMENT, NOME TEXT NOT NULL, DT_VENC TEXT NOT NULL, DT_BASE TEXT NOT NULL, VALOR_TIT REAL NOT NULL)")

        elif tabela == "TITULO":
            cur.execute("CREATE TABLE TITULO (TIT_ID INTEGER PRIMARY KEY AUTOINCREMENT, NOME TEXT NOT NULL, DT_VENC TEXT NOT NULL, TIPO TEXT NOT NULL)")

# -------------------------------------- Váriaveis globais -------------------------------------- #

diretorio_base = os.path.dirname(os.path.abspath(__file__))

SQL_POSICAO_EMPRESAS = "SELECT b.NOME," \
                        "       b.SETOR," \
                        "       a.UTICKER," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PRECOMEDIO," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAO as a " \
                        "inner join EMPRESA as b " \
                        "on (a.ID = b.ID)" \
                        "order by a.VALORTOTAL desc"

SQL_POSICAO_TITULOS = "SELECT b.NOME," \
                        "       b.DT_VENC," \
                        "       b.TIPO," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAOTESOURO as a " \
                        "inner join TITULO as b " \
                        "on (a.TIT_ID = b.TIT_ID)" \
                        "order by a.VALORTOTAL desc"

SQL_POSICAO_FIIS = "SELECT b.NOME," \
                        "       a.UTICKER," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PRECOMEDIO," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAO as a " \
                        "inner join FII as b " \
                        "on (a.FID = b.ID)" \
                        "order by a.VALORTOTAL desc"

SQL_ALL_COMPRAS = "SELECT DATA," \
                        "       VALOR_ACAO," \
                        "       QUANTIDADE," \
                        "       UTICKER," \
                        "       FONTE " \
                        "from COMPRA " \
                        "order by DATA desc"

SQL_APORTES_EMP = "SELECT UTICKER," \
                        "       strftime('%m', SUBSTR(DATA, 7, 4) || '-' || SUBSTR(DATA, 4, 2) || '-' || SUBSTR(DATA, 1, 2)) AS MES," \
                        "       SUM(VALOR_ACAO * QUANTIDADE) " \
                        "from COMPRA " \
                        "where (strftime('%Y', SUBSTR(DATA, 7, 4) || '-' || SUBSTR(DATA, 4, 2) || '-' || SUBSTR(DATA, 1, 2)) = '" + datetime.datetime.now().strftime('%Y') + "') " \
                        "group by UTICKER, MES "

SQL_RISCO_EMP = "SELECT UTICKER, " \
                        "       RISCO " \
                        "from POSICAO " \
                        "order by UTICKER "

SQL_DEFINICAO_EMP = "SELECT UTICKER, " \
                        "       DEFINICAO " \
                        "from POSICAO " \
                        "order by UTICKER "

SQL_GRAF_APORTES = "SELECT strftime('%m/%Y', SUBSTR(DATA, 7, 4) || '-' || SUBSTR(DATA, 4, 2) || '-' || SUBSTR(DATA, 1, 2)) AS MESANO," \
                        "       SUM(VALOR_ACAO * QUANTIDADE) " \
                        "from COMPRA " \
                        "group by MESANO " \
                        "order by date(SUBSTR(DATA, 7, 4) || '-' || SUBSTR(DATA, 4, 2) || '-' || SUBSTR(DATA, 1, 2)) " \
                        "LIMIT 14 "

SQL_GRAF_PSETOR = "SELECT B.SETOR," \
                        "       SUM(A.VALOR_ACAO * A.QUANTIDADE) as VALOR " \
                        "from COMPRA as A " \
                        "inner join EMPRESA as B ON (A.ID = B.ID) " \
                        "group by B.SETOR " \
                        "order by VALOR desc"

SQL_GRAF_ALLATIVOS = "SELECT UTICKER," \
                        "       SUM(VALOR_ACAO * QUANTIDADE) as VALOR " \
                        "from COMPRA " \
                        "group by UTICKER " \
                        "order by VALOR desc"


# -------------------------------------- TELA 1 (Menu, gráfico dos ativos) -------------------------------------- #

try:

    def openoptions():
        state_options = canvas1.itemcget(bt_var_window, 'state')

        if state_options == 'hidden':

            canvas1.itemconfigure(bt_var_window, state='normal')
            canvas1.itemconfigure(bt_fix_window, state='normal')
            canvas1.itemconfigure(bt_fii_window, state='normal')

        else:

            canvas1.itemconfigure(bt_var_window, state='hidden')
            canvas1.itemconfigure(bt_fix_window, state='hidden')
            canvas1.itemconfigure(bt_fii_window, state='hidden')


    def go_menucompra():

        canvas1.pack_forget()
        canvas2.pack()


    def info_ren_variavel(tipo):

        cur.execute(SQL_POSICAO_EMPRESAS)

        dados_tabela = cur.fetchall()

        if tipo == "grafico":
            valor_total = 0
            lst_rent_emp = []

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                empresa = yf.Ticker(str(dados_tabela[l][2]) + ".SA")

                hist_fechamento = empresa.history(period="1day")

                valor_fechamento = empresa.history_metadata.get("regularMarketPrice")

                if valor_fechamento is not None:

                    if type(valor_fechamento) == float:

                        valor_atual = round(float(valor_fechamento) * int(dados_tabela[l][7]), 2)

                        emp_rentabilidade = round(((float(valor_fechamento) * int(dados_tabela[l][7])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                        if tipo == "tabela":
                            table.insert('', 'end', text=dados_tabela[l][0], values=(
                            dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), round(dados_tabela[l][6], 2), dados_tabela[l][7], valor_atual,  emp_rentabilidade))
                        elif tipo == "grafico":
                            lst_rent_emp.append(emp_rentabilidade * float(dados_tabela[l][5]))
                            valor_total += float(dados_tabela[l][5])

                    else:
                        if tipo == "tabela":
                            table.insert('', 'end', text=dados_tabela[l][0], values=(
                            dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), round(dados_tabela[l][6], 2), dados_tabela[l][7], round(dados_tabela[l][5], 2),  "-"))
                        elif tipo == "grafico":
                            lst_rent_emp.append(0)

        if tipo == "grafico":
            rent_carteira = 0
            for emp in lst_rent_emp:
                rent_carteira += emp

            return rent_carteira, valor_total


    def info_ren_fii():

        cur.execute(SQL_POSICAO_FIIS)

        dados_tabela = cur.fetchall()

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                table_fii.insert('', 'end', text=dados_tabela[l][0], values=(dados_tabela[l][1], dados_tabela[l][2], 'Abrir informações...', round(dados_tabela[l][4], 2), round(dados_tabela[l][5], 2), dados_tabela[l][6]))


    def info_ren_fixa(tipo):

        cur.execute(SQL_POSICAO_TITULOS)

        dados_tabela_tit = cur.fetchall()

        if tipo == "grafico":
            valor_total = 0
            lst_rent_tit = []

        if len(dados_tabela_tit) > 0:
            for l in range(0, len(dados_tabela_tit)):

                cur.execute("SELECT VALOR_TIT FROM TEMPTITULOS WHERE UPPER(NOME) = '" + dados_tabela_tit[l][0] + "' and DT_VENC = '" + dados_tabela_tit[l][1] + "'")

                busca_cotacao = cur.fetchall()

                cotacao_tit = busca_cotacao[0][0] / 100

                if (cotacao_tit != "") and (str(cotacao_tit).replace(",", "").replace(".", "").strip().isnumeric()):
                    tit_rentabilidade = round(((float(cotacao_tit) * int(dados_tabela_tit[l][6])) - float(dados_tabela_tit[l][5])) / float(dados_tabela_tit[l][5]) * 100, 2)

                    if tipo == "tabela":
                        table_fix.insert('', 'end', text=dados_tabela_tit[l][0], values=(dados_tabela_tit[l][1], dados_tabela_tit[l][2], dados_tabela_tit[l][3], 'Abrir informações...', round(dados_tabela_tit[l][5], 2), dados_tabela_tit[l][6], tit_rentabilidade))
                    elif tipo == "grafico":
                        lst_rent_tit.append(tit_rentabilidade * float(dados_tabela_tit[l][5]))
                        valor_total += float(dados_tabela_tit[l][5])

                else:
                    if tipo == "grafico":
                        lst_rent_tit.append(0)

        if tipo == "grafico":
            rent_carteira = 0
            for tit in lst_rent_tit:
                rent_carteira += tit

            return rent_carteira, valor_total


    def go_viewativos():

        canvas1.pack_forget()
        canvas4.pack()

        style = ttk.Style()

        style.configure("Treeview", font=("Arial", 12), padding=(0, 35, 0, 35), background='#B0C4DE', rowheight=50)
        style.configure("Treeview.Heading", font=("Arial", 12, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

        table.configure(style="Treeview.Heading")
        table.configure(style="Treeview")

        if table.get_children():
            table.delete(*table.get_children())

            info_ren_variavel("tabela")

        else:

            info_ren_variavel("tabela")


    def go_viewfix():

        canvas1.pack_forget()
        canvas6.pack()

        if table_fix.get_children():
            table_fix.delete(*table_fix.get_children())

            info_ren_fixa("tabela")

        else:

            info_ren_fixa("tabela")


    def go_viewfiis():

        canvas1.pack_forget()
        canvas11.pack()

        style = ttk.Style()

        style.configure("Treeview", font=("Arial", 12), padding=(0, 35, 0, 35), background='#B0C4DE', rowheight=50)
        style.configure("Treeview.Heading", font=("Arial", 12, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

        table_fii.configure(style="Treeview.Heading")
        table_fii.configure(style="Treeview")

        if table_fii.get_children():
            table_fii.delete(*table_fii.get_children())

            info_ren_fii()

        else:

            info_ren_fii()


    def show_grafvar():

        cur.execute("SELECT * FROM POSICAO")

        dado_pos = cur.fetchall()

        cur.execute("SELECT case when B.NOME is NULL then '" + "FIIS" + "' else '" + "AÇÕES" + "'end as TIPO, "
                    "SUM(A.VALORTOTAL) "
                    "FROM POSICAO AS A "
                    "left JOIN EMPRESA AS B ON (A.ID = B.ID) "
                    "left JOIN FII     AS C ON (A.FID = C.ID) "
                    "GROUP BY TIPO "
                    "ORDER BY A.VALORTOTAL")

        if len(dado_pos) > 0:
            dados_renda_var = cur.fetchall()
        else:
            dados_renda_var = []

        lst_valores = []
        lst_empresas = []

        valor_total_graf = []

        for i in dados_renda_var:
            lst_valores.append(float(i[1]))
            lst_empresas.append(str(i[0]))
            valor_total_graf.append(float(i[1]))
        else:
            if len(lst_valores) == 0 and len(lst_empresas) == 0:
                lst_valores = [0.05]
                lst_empresas = [""]
                valor_total_graf.append(0)

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(lst_valores, labels=lst_empresas)
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid', bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16, text='Valor Total: R$ ' + str(round(sum(tuple(valor_total_graf)), 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        rentabilidade, soma_ativos = info_ren_variavel("grafico")

        soma_valida = rentabilidade + soma_ativos
        if soma_valida != 0:
            cart_rentabilidade = (rentabilidade / soma_ativos) * 1
        else:
            cart_rentabilidade = 0.0

        lb_rentabilidade = ttk.Label(canvas1, font=15, text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


    def show_graffix():
        cur.execute("SELECT * FROM POSICAOTESOURO")

        dado_pos = cur.fetchall()

        cur.execute("SELECT B.NOME, B.DT_VENC, A.VALORTOTAL FROM POSICAOTESOURO AS A INNER JOIN TITULO AS B ON (A.TIT_ID = B.TIT_ID) ORDER BY A.VALORTOTAL")

        if len(dado_pos) > 0:
            dados_renda_fix = cur.fetchall()
        else:
            dados_renda_fix = []

        lst_valores_tit = []
        lst_titulos = []

        valor_total_graf = []

        for i in dados_renda_fix:
            lst_valores_tit.append(float(i[2]))
            lst_titulos.append(str(i[0] + " " + i[1][-4:]).replace("TESOURO", "").replace("COM JUROS SEMESTRAIS", "C/ JUROS"))
            valor_total_graf.append(float(i[1]))
        else:
            if len(lst_valores_tit) == 0 and len(lst_titulos) == 0:
                lst_valores_tit = [0.05]
                lst_titulos = [""]
                valor_total_graf.append(0)

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(lst_valores_tit, labels=lst_titulos)
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid', bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16, text='Valor Total: R$ ' + str(round(sum(tuple(valor_total_graf)), 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        rentabilidade_fix, soma_ativos_fix = info_ren_fixa("grafico")

        soma_valida = rentabilidade_fix + soma_ativos_fix
        if soma_valida != 0:
            cart_rentabilidade = (rentabilidade_fix / soma_ativos_fix) * 1
        else:
            cart_rentabilidade = 0.0

        lb_rentabilidade = ttk.Label(canvas1, font=15, text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


    def show_graf():

        cur.execute("SELECT SUM(VALORTOTAL) FROM POSICAO")

        valor_total_var = 0.05
        valor_total_fix = 0.05

        dados_renda_var = cur.fetchall()
        if dados_renda_var[0][0] is not None:
            valor_total_var += sum(x[0] for x in dados_renda_var)

        cur.execute("SELECT SUM(VALORTOTAL) FROM POSICAOTESOURO")

        dados_renda_fix = cur.fetchall()
        if dados_renda_fix[0][0] is not None:
            valor_total_fix += sum(x[0] for x in dados_renda_fix)

        dados = [valor_total_var, valor_total_fix]

        ctl_graphs_fix = tk.IntVar()
        ctl_graphs_fix.set(0)

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(dados, labels=['Renda Variável', 'Renda Fixa'])
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid', bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16, text='Valor Total: R$ ' + str(round((valor_total_var + valor_total_fix) if (valor_total_var + valor_total_fix) != 0.10 else 0.0, 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        rentabilidade, soma_ativos = info_ren_variavel("grafico")
        rentabilidade_fix, soma_ativos_fix = info_ren_fixa("grafico")

        soma_valida = 0;
        soma_valida += rentabilidade + rentabilidade_fix + soma_ativos + soma_ativos_fix

        if soma_valida != 0:
            cart_rentabilidade = ((rentabilidade + rentabilidade_fix) / (soma_ativos + soma_ativos_fix)) * 1
        else:
            cart_rentabilidade = 0.0

        lb_rentabilidade = ttk.Label(canvas1, font=15, text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


    def go_viewgraficos():
        canvas1.pack_forget()
        canvas9.pack()


    def seleciona_graph_fix():
        if ctl_graphs_fix.get() == 0:
            show_graffix()
            ctl_graphs_fix.set(1)
        else:
            show_graf()
            ctl_graphs_fix.set(0)


    def alterna_graph_fix():
        seleciona_graph_fix()


    def seleciona_graph_var():
        if ctl_graphs_var.get() == 0:
            show_grafvar()
            ctl_graphs_var.set(1)
        else:
            show_graf()
            ctl_graphs_var.set(0)


    def alterna_graph_var():
        seleciona_graph_var()


    canvas1 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas1.create_image(0, 0, image=bg_image_tk, anchor='nw')
    canvas1.pack()

    bt_var = ttk.Button = Button(canvas1, font=9, background='#1E90FF', text='Ações', command=go_viewativos)
    bt_var_window = canvas1.create_window(185, 510, anchor='sw', window=bt_var, height=35, width=220)
    canvas1.itemconfigure(bt_var_window, state='hidden')

    bt_fii = ttk.Button = Button(canvas1, font=9, background='#1E90FF', text='FIIS', command=go_viewfiis)
    bt_fii_window = canvas1.create_window(185, 590, anchor='sw', window=bt_fii, height=35, width=220)
    canvas1.itemconfigure(bt_fii_window, state='hidden')

    bt_fix = ttk.Button = Button(canvas1, font=9, background='#1E90FF', text='Renda Fixa', command=go_viewfix)
    bt_fix_window = canvas1.create_window(185, 550, anchor='sw', window=bt_fix, height=35, width=220)
    canvas1.itemconfigure(bt_fix_window, state='hidden')

    state = canvas1.itemcget(bt_var_window, 'state')

    bt_ativos = ttk.Button = Button(canvas1, command=openoptions, font=15, background='#6A5ACD', width=35, text='Meus Ativos')
    bt_ativos_window = canvas1.create_window(100, 470, anchor='sw', window=bt_ativos)

    bt_graficos = ttk.Button = Button(canvas1, font=15, background='#6A5ACD', text='Gráficos', width=35, command=go_viewgraficos)
    bt_graficos_window = canvas1.create_window(100, 640, anchor='sw', window=bt_graficos)

    bt_Cadastro = ttk.Button = Button(canvas1, font=18, background='#6A5ACD', width=40, text='Cadastrar Compra', height=2, command=go_menucompra)
    bt_Cadastro_window = canvas1.create_window(100, 730, anchor='sw', window=bt_Cadastro)

    bt_graf_rendVar = ttk.Button = Button(canvas1, font=15, background='#1E90FF', width=18, text='Renda Variável', command=alterna_graph_var)
    bt_graf_rendVar_window = canvas1.create_window(900, 200, anchor='sw', window=bt_graf_rendVar, width=217)

    bt_graf_rendFix = ttk.Button = Button(canvas1, font=15, background='#1E90FF', width=18, text='Renda Fixa', command=alterna_graph_fix)
    bt_graf_rendFix_window = canvas1.create_window(1117, 200, anchor='sw', window=bt_graf_rendFix, width=217)

    ctl_graphs_fix = tk.IntVar()
    ctl_graphs_fix.set(0)

    ctl_graphs_var = tk.IntVar()
    ctl_graphs_var.set(0)

    show_graf()


    # -------------------------------------- FINAL TELA 1 -------------------------------------- #

    # -------------------------------------- TELA 2 (Menu compra de ativos) -------------------------------------- #

    def go_frm_compra_acao():

        canvas2.pack_forget()
        canvas3.pack()


    def go_frm_compra_fix():
        canvas2.pack_forget()
        canvas5.pack()


    def go_frm_compra_fii():
        canvas2.pack_forget()
        canvas10.pack()

    def go_menuanterior1():

        show_graf()

        canvas2.pack_forget()
        canvas1.pack()


    canvas2 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas2.create_image(0, 0, image=bg_image_tk, anchor='nw')

    lb_question = ttk.Label(canvas2, font=('Helvetica', 18, 'bold'), text='Antes de informar sua compra, nos informe qual o tipo de ativo...', foreground='#171F3D', anchor=CENTER,background="#1E90FF", padding=4)
    lb_question_window = canvas2.create_window(400, 300, anchor='sw', window=lb_question, width=780)

    bt_sel_acao = ttk.Button = Button(canvas2, font=15, width=10, text='Ações', relief="solid", command=go_frm_compra_acao, foreground="#171F3D")
    bt_sel_acao_window = canvas2.create_window(580, 400, anchor='sw', window=bt_sel_acao, width=400)

    bt_sel_fii = ttk.Button = Button(canvas2, font=15, width=10, text='FIIS', relief="solid", foreground="#171F3D", command=go_frm_compra_fii)
    bt_sel_fii_window = canvas2.create_window(580, 480, anchor='sw', window=bt_sel_fii, width=400)

    bt_sel_fixa = ttk.Button = Button(canvas2, font=15, width=10, text='Renda Fixa', relief="solid", command=go_frm_compra_fix, foreground="#171F3D")
    bt_sel_fixa_window = canvas2.create_window(580, 560, anchor='sw', window=bt_sel_fixa, width=400)

    diretorio_destino = os.path.join(diretorio_base, 'img/widgets/voltar.png')

    img_voltar = PhotoImage(file=diretorio_destino)

    bt_Voltar = ttk.Button = Button(canvas2, relief="solid", command=go_menuanterior1, image=img_voltar)
    bt_Voltar_window = canvas2.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)


    # -------------------------------------- FINAL TELA 2 -------------------------------------- #

    # -------------------------------------- TELA 3 (Comprar ações) -------------------------------------- #

    def go_menuanterior2():

        canvas3.pack_forget()
        canvas2.pack()


    def confirma_compra():

        if inp_nome.get() == "":
            texto_erro = "Carregue as informações da empresa primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_ticker.get() == "":
            texto_erro = "Carregue o ticker da empresa primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_setor.get() == "":
            texto_erro = "Carregue as informações da empresa primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_data.get() == "") or (not str(inp_data.get())[0:2].isnumeric()) or (not str(inp_data.get())[3:5].isnumeric()) or (not str(inp_data.get())[6:11].isnumeric()):
            texto_erro = "Carregue a data da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_valor.get() == "") or (not str(inp_valor.get()).replace(",", "").replace(".", "").strip().isnumeric()):
            texto_erro = "Carregue as informações do valor da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_quant.get() == "") or (not str(inp_quant.get()).strip().isnumeric()):
            texto_erro = "Carregue as informações da quantidade da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_risco.get() == "") or (not str(inp_risco.get())[:1].isnumeric()):
            texto_erro = "Carregue as informações referente a risco primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_motivo.get("1.0", "end-1c") == "":
            texto_erro = "Carregue as informações referente ao motivo primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        else:

            cur.execute("SELECT ID FROM EMPRESA where nome = '" + inp_nome.get().upper().strip() + "'")

            dado_id_emp = cur.fetchall()

            id_empresa = dado_id_emp[0][0]

            cur.execute('insert into COMPRA(DATA, VALOR_ACAO, QUANTIDADE, UTICKER, FONTE, ID) values(?, ?, ?, ?, ?, ?)', (str(inp_data.get()).strip(), float(str(inp_valor.get()).replace(",", ".")), int(inp_quant.get()), str(inp_ticker.get()).strip(), "Manual" , int(id_empresa)))
            con.commit()

            cur.execute("SELECT POSICAO_ID FROM POSICAO where ID = " + str(id_empresa) + "")

            dado_id_posicao = cur.fetchall()

            if len(dado_id_posicao) > 0:

                cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                            "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                            "       SUM(QUANTIDADE)" \
                            " FROM COMPRA where ID = " + str(id_empresa) + " " \
                            " GROUP BY ID")

                dados_posicao = cur.fetchall()

                cur.execute('UPDATE POSICAO SET RISCO = ?, DEFINICAO = ?, VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE ID = ? AND UTICKER = ?',
                            (int(inp_risco.get()), inp_motivo.get("1.0", "end-1c"), dados_posicao[0][0], dados_posicao[0][1],
                             dados_posicao[0][2], id_empresa, str(inp_ticker.get()).strip()))

                con.commit()

                texto_info = "Compra registrada com sucesso! Sua posição na empresa foi atualizada."
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()

            else:

                cur.execute('insert into POSICAO(RISCO, DEFINICAO, VALORTOTAL, PRECOMEDIO, PAPEISTOTAIS, UTICKER, ID) values(?, ?, ?, ?, ?, ?, ?)',
                            (int(inp_risco.get()), inp_motivo.get("1.0", "end-1c"),
                             float(str(inp_valor.get()).replace(",", ".")) * int(inp_quant.get()),
                             (float(str(inp_valor.get()).replace(",", ".")) * int(inp_quant.get())) / int(inp_quant.get()),
                             int(inp_quant.get()), str(inp_ticker.get()).strip(), id_empresa))

                con.commit()

                texto_info = "Compra registrada com sucesso!"
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    def carrega_nota():

        canvas3.pack_forget()
        canvas7.pack()


    canvas3 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas3.create_image(0, 0, image=bg_image_tk, anchor='nw')

    lbl_inp_nome = ttk.Label(canvas3, text='Nome da Empresa', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_nome_window = canvas3.create_window(180, 280, anchor='sw', window=lbl_inp_nome, width=150)

    lbl_inp_ticker = ttk.Label(canvas3, text='Ticker', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_ticker_window = canvas3.create_window(380, 280, anchor='sw', window=lbl_inp_ticker, width=110)

    lbl_inp_setor = ttk.Label(canvas3, text='Setor', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_setor_window = canvas3.create_window(550, 280, anchor='sw', window=lbl_inp_setor, width=200)

    lbl_inp_data = ttk.Label(canvas3, text='Data Investimento', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_data_window = canvas3.create_window(820, 280, anchor='sw', window=lbl_inp_data, width=145)

    lbl_inp_valor = ttk.Label(canvas3, text='Valor da Ação', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_valor_window = canvas3.create_window(1050, 280, anchor='sw', window=lbl_inp_valor, width=130)

    lbl_inp_quant = ttk.Label(canvas3, text='Quantidade', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_quant_window = canvas3.create_window(1260, 280, anchor='sw', window=lbl_inp_quant, width=130)

    inp_nome = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_nome_window = canvas3.create_window(180, 330, anchor='sw', window=inp_nome, width=150, height=40)

    inp_ticker = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_ticker_window = canvas3.create_window(380, 330, anchor='sw', window=inp_ticker, width=110, height=40)

    inp_setor = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_setor_window = canvas3.create_window(550, 330, anchor='sw', window=inp_setor, width=200, height=40)

    inp_data = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_data_window = canvas3.create_window(820, 330, anchor='sw', window=inp_data, width=145, height=40)

    inp_valor = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_valor_window = canvas3.create_window(1050, 330, anchor='sw', window=inp_valor, width=130, height=40)

    inp_quant = ttk.Entry(canvas3, font=('Helvetica', 12))
    inp_quant_window = canvas3.create_window(1260, 330, anchor='sw', window=inp_quant, width=130, height=40)

    list_nomes = tk.Listbox(canvas3, width=21, height=5)
    list_nomes_window = canvas3.create_window(180, 410, anchor='sw', window=list_nomes, width=150, height=70)

    list_ticker = tk.Listbox(canvas3, width=21, height=5)
    list_ticker_window = canvas3.create_window(380, 410, anchor='sw', window=list_ticker, width=110, height=70)

    lbl_inp_risco = ttk.Label(canvas3, text='Risco Associado', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_risco_window = canvas3.create_window(550, 430, anchor='sw', window=lbl_inp_risco, width=170)

    lbl_inp_motivo = ttk.Label(canvas3, text='Defina o por que você está investindo nessa empresa...', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_motivo_window = canvas3.create_window(800, 430, anchor='sw', window=lbl_inp_motivo, width=590)

    v = DoubleVar()

    inp_risco = ttk.Scale(canvas3, variable=v, from_=1, to=10, orient=HORIZONTAL)
    inp_risco_window = canvas3.create_window(550, 480, anchor='sw', window=inp_risco, width=170)

    inp_motivo = Text(canvas3, width=90, font=('Helvetica', 10), height=10)
    inp_motivo.delete("1.0", "end")
    inp_motivo_window = canvas3.create_window(800, 530, anchor='sw', window=inp_motivo, width=590, height=90)

    bt_confirma = ttk.Button = Button(canvas3, font=11, text='Confirmar', relief="solid", background='#6A5ACD', command=confirma_compra)
    bt_confirma_window = canvas3.create_window(660, 650, anchor='sw', window=bt_confirma, width=200, height=70)

    diretorio_bt_import = os.path.join(diretorio_base, 'img/widgets/fundo_bt_import.png')
    imagem_fundo = PhotoImage(file=diretorio_bt_import)

    bt_import_nota = ttk.Button = Button(canvas3, font=11, text='Importar Nota', relief="solid", image=imagem_fundo, command=carrega_nota)
    bt_import_nota_window = canvas3.create_window(120, 650, anchor='sw', window=bt_import_nota, width=210, height=130)

    bt_Voltar = ttk.Button = Button(canvas3, relief="solid", command=go_menuanterior2, image=img_voltar)
    bt_Voltar_window = canvas3.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)


    # -------------------------------------- FINAL TELA 3 -------------------------------------- #
    # -------------------------------------- LÓGICA TELA 3 -------------------------------------- #

    def update_suggestions(event):
        list_nomes.delete(0, tk.END)
        text = inp_nome.get()

        for emp in dados_emp:
            if trata_str_emp(str(emp)).startswith(text.upper()):
                list_nomes.insert(tk.END, trata_str_emp(emp))


    def select_empresa(event):
        if len(event.widget.curselection()) > 0:
            index = event.widget.curselection()

            value = event.widget.get(index)

            inp_nome.delete(0, tk.END)
            inp_nome.insert(0, str(value))

            cur.execute("SELECT ticker FROM EMPRESA where nome = '" + str(value) + "'")

            dados_ticker = cur.fetchall()
            list_ticker.delete(0, tk.END)

            for ticker in dados_ticker:
                tickers = list(str(ticker).split())
                for x in tickers:
                    list_ticker.insert(tk.END, trata_str_emp(x.strip()))

            inp_ticker.config(state='normal')
            inp_ticker.delete(0, tk.END)

            cur.execute("SELECT setor FROM EMPRESA where nome = '" + str(value) + "'")
            dado_emp_setor = cur.fetchall()

            inp_setor.config(state='normal')
            inp_setor.delete(0, tk.END)
            inp_setor.insert(0, trata_str_emp(str(dado_emp_setor)).upper())
            inp_setor.config(state='readonly')


    def select_ticker(event):
        if (len(event.widget.curselection()) > 0) and (inp_nome.get() != ""):
            index_ticker = event.widget.curselection()

            value_ticker = event.widget.get(index_ticker)

            inp_ticker.config(state='normal')
            inp_ticker.delete(0, tk.END)
            inp_ticker.insert(0, str(value_ticker))
            inp_ticker.config(state='readonly')


    def format_date(entry):
        current_text = entry.get()

        if len(current_text) == 2 or len(current_text) == 5:
            entry.insert(tk.END, "/")


    def show_risco(event):

        txt_risco = 'Risco Associado: ' + str(int(event.widget.get()))
        lbl_inp_risco.config(text=txt_risco)


    cur.execute("SELECT nome FROM EMPRESA order by nome")

    dados_emp = cur.fetchall()

    for item in dados_emp:
        list_nomes.insert(tk.END, trata_str_emp(item))

    inp_nome.bind('<KeyRelease>', update_suggestions)
    list_nomes.bind('<Button-1>', select_empresa)
    list_ticker.bind('<Button-1>', select_ticker)
    inp_data.bind("<KeyRelease>", lambda event: format_date(inp_data))
    inp_risco.bind('<Button-1>', show_risco)


    # -------------------------------------- TELA 4 (Tabela de ações) -------------------------------------- #

    def go_menuanterior3():

        canvas4.pack_forget()
        canvas1.pack()


    def go_tela_acao(event):

        canvas4.pack_forget()
        canvas8.pack()

        bt_empresa.configure(background='#171F3D')
        bt_definicao.configure(background='#1E90FF')
        bt_lancamentos.configure(background='#1E90FF')

        lb_empresa_window = canvas8.create_window(370, 185, anchor='sw', window=lb_empresa)

        set_tela_empresa('normal')
        set_tela_definicao('hidden')
        set_tela_definicao_pos('hidden')
        set_tela_definicao_ind('hidden')
        set_tela_definicao_risco('hidden')
        set_tela_definicao_notas('hidden')
        set_tela_lancamentos('hidden')
        set_tela_lancamentos_edit('hidden')

        bt_empresa.bind("<Button-1>", muda_cor_botao)
        bt_definicao.bind("<Button-1>", muda_cor_botao)
        bt_lancamentos.bind("<Button-1>", muda_cor_botao)

        canvas8.create_image(0, 0, image=bg_image_tk_nologo, anchor='nw')

        indice = table.focus()

        if indice:
            valor = table.item(indice, "text")
            valores = table.item(indice, "values")

            carrega_tela_empresa(valor, valores[1], float(valores[7])/float(valores[6]))
            carrega_tela_def_posicao(valor, valores[1], valores[4], valores[5], valores[6], valores[7], valores[8])
            carrega_tela_def_ind(valor, valores[1], float(valores[7])/float(valores[6]))
            carrega_tela_def_risco(valores[1])
            carrega_tela_def_definicao(valores[1])
            carrega_tela_lancamentos(valores[1])


    canvas4 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas4.create_image(0, 0, image=bg_image_tk, anchor='nw')

    table = ttk.Treeview(canvas4, columns=('Setor', 'Ticker', 'Risco', 'Definicao', 'Valor', 'Preco', 'Papeis', 'Atual', 'Rentabilidade'))

    table.heading('#0', text='Empresa')
    table.heading('Setor', text='Setor')
    table.heading('Ticker', text='Ticker')
    table.heading('Risco', text='Risco')
    table.heading('Definicao', text='Definição')
    table.heading('Valor', text='Valor Total')
    table.heading('Preco', text='Preço Médio')
    table.heading('Papeis', text='Papeis Totais')
    table.heading('Atual', text='Valor Atual')
    table.heading('Rentabilidade', text='Rentabilidade (%)')

    cur.execute(SQL_POSICAO_EMPRESAS)

    dados_tabela = cur.fetchall()

    table.column("#0", width=180)
    table.column("Ticker", width=120)
    table.column("Setor", width=150)
    table.column("Risco", width=50)
    table.column("Valor", width=95)
    table.column("Preco", width=105)
    table.column("Papeis", width=110)
    table.column("Atual", width=95)
    table.column("Rentabilidade", width=140)

    table.configure(padding=10)

    table_window = canvas4.create_window(120, 700, anchor='sw', window=table, width=1300, height=450)

    table.bind("<Double-1>", go_tela_acao)

    bt_Voltar = ttk.Button = Button(canvas4, relief="solid", command=go_menuanterior3, image=img_voltar)
    bt_Voltar_window = canvas4.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)


    # -------------------------------------- TELA 5 (Comprar títulos renda fix) -------------------------------------- #

    def go_menuanterior4():

        canvas5.pack_forget()
        canvas2.pack()


    def confirma_compra_tit():
        if inp_titulo.get() == "":
            texto_erro = "Carregue as informações do título primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_venc.get() == "":
            texto_erro = "Carregue as informações do título primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_tipo.get() == "":
            texto_erro = "Carregue as informações do título primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_data_tit.get() == "") or (not str(inp_data_tit.get())[0:2].isnumeric()) or (not str(inp_data_tit.get())[3:5].isnumeric()) or (not str(inp_data_tit.get())[6:11].isnumeric()):
            texto_erro = "Carregue a data da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_valor_tit.get() == "") or (not str(inp_valor_tit.get()).replace(",", "").replace(".", "").strip().isnumeric()):
            texto_erro = "Carregue as informações do valor da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_quant_tit.get() == "") or (not str(inp_quant_tit.get()).strip().isnumeric()):
            texto_erro = "Carregue as informações da quantidade da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_risco_tit.get() == "") or (not str(inp_risco_tit.get())[:1].isnumeric()):
            texto_erro = "Carregue as informações referente a risco primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_motivo_tit.get("1.0", "end-1c") == "":
            texto_erro = "Carregue as informações referente ao motivo primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()

        cur.execute("SELECT TIT_ID FROM TITULO where nome = '" + inp_titulo.get().upper().strip() + "' and dt_venc = '" + inp_venc.get().strip() + "'")

        dado_id_tit = cur.fetchall()

        id_titulo = dado_id_tit[0][0]

        cur.execute('insert into COMPRATESOURO(DATA, VALOR_TIT, QUANTIDADE, TIT_ID) values(?, ?, ?, ?)',
                    (str(inp_data_tit.get()).strip(), float(str(inp_valor_tit.get()).replace(",", ".")), int(inp_quant_tit.get()), int(id_titulo)))
        con.commit()

        cur.execute("SELECT POSICAOT_ID FROM POSICAOTESOURO where TIT_ID = " + str(id_titulo) + "")

        dado_id_posicao_tit = cur.fetchall()

        if len(dado_id_posicao_tit) > 0:

            cur.execute("SELECT (SUM(VALOR_TIT) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                        "       (SUM(VALOR_TIT) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                        "       SUM(QUANTIDADE)" \
                        " FROM COMPRATESOURO where TIT_ID = " + str(id_titulo) + " " \
                                                                                 " GROUP BY ID")

            dados_posicao_tit = cur.fetchall()

            cur.execute('UPDATE POSICAOTESOURO SET RISCO = ?, DEFINICAO = ?, VALORTOTAL = ?, PAPEISTOTAIS = ? WHERE TIT_ID = ?',
                        (inp_risco_tit.get(), inp_motivo_tit.get("1.0", "end-1c"), dados_posicao_tit[0][0], dados_posicao_tit[0][1], dados_posicao_tit[0][2], id_titulo))
            con.commit()

            texto_info = "Compra registrada com sucesso! Sua posição no título foi atualizada."
            lbl_info = messagebox.Message(title='Investify', message=texto_info)
            lbl_info.show()

        else:
            cur.execute('insert into POSICAOTESOURO(RISCO, DEFINICAO, VALORTOTAL, PAPEISTOTAIS, TIT_ID) values(?, ?, ?, ?, ?)',
                        (inp_risco_tit.get(), inp_motivo_tit.get("1.0", "end-1c"), float(str(inp_valor_tit.get()).replace(",", ".")) * int(inp_quant_tit.get()), int(inp_quant_tit.get()), id_titulo))
            con.commit()

            texto_info = "Compra registrada com sucesso!"
            lbl_info = messagebox.Message(title='Investify', message=texto_info)
            lbl_info.show()


    canvas5 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas5.create_image(0, 0, image=bg_image_tk, anchor='nw')

    lbl_inp_titulo = ttk.Label(canvas5, text='Nome do Título', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_titulo_window = canvas5.create_window(180, 280, anchor='sw', window=lbl_inp_titulo, width=150)

    lbl_inp_venc = ttk.Label(canvas5, text='Vencimento', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_venc_window = canvas5.create_window(380, 280, anchor='sw', window=lbl_inp_venc, width=110)

    lbl_inp_tipo = ttk.Label(canvas5, text='Tipo', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_tipo_window = canvas5.create_window(550, 280, anchor='sw', window=lbl_inp_tipo, width=200)

    lbl_inp_data_tit = ttk.Label(canvas5, text='Data Compra', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_data_tit_window = canvas5.create_window(820, 280, anchor='sw', window=lbl_inp_data_tit, width=145)

    lbl_inp_valor_tit = ttk.Label(canvas5, text='Valor', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_valor_tit_window = canvas5.create_window(1050, 280, anchor='sw', window=lbl_inp_valor_tit, width=130)

    lbl_inp_quant_tit = ttk.Label(canvas5, text='Quantidade', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_quant_tit_window = canvas5.create_window(1260, 280, anchor='sw', window=lbl_inp_quant_tit, width=130)

    inp_titulo = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_titulo_window = canvas5.create_window(180, 330, anchor='sw', window=inp_titulo, width=150, height=40)

    inp_venc = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_venc_window = canvas5.create_window(380, 330, anchor='sw', window=inp_venc, width=110, height=40)

    inp_tipo = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_tipo_window = canvas5.create_window(550, 330, anchor='sw', window=inp_tipo, width=200, height=40)

    inp_data_tit = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_data_tit_window = canvas5.create_window(820, 330, anchor='sw', window=inp_data_tit, width=145, height=40)

    inp_valor_tit = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_valor_tit_window = canvas5.create_window(1050, 330, anchor='sw', window=inp_valor_tit, width=130, height=40)

    inp_quant_tit = ttk.Entry(canvas5, font=('Helvetica', 12))
    inp_quant_tit_window = canvas5.create_window(1260, 330, anchor='sw', window=inp_quant_tit, width=130, height=40)

    list_nomes_tit = tk.Listbox(canvas5, width=21, height=5)
    list_nomes_tit_window = canvas5.create_window(180, 410, anchor='sw', window=list_nomes_tit, width=150, height=70)

    list_venc = tk.Listbox(canvas5, width=21, height=5)
    list_venc_window = canvas5.create_window(380, 410, anchor='sw', window=list_venc, width=110, height=70)

    lbl_inp_risco_tit = ttk.Label(canvas5, text='Risco Associado', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_risco_tit_window = canvas5.create_window(550, 430, anchor='sw', window=lbl_inp_risco_tit, width=170)

    lbl_inp_motivo_tit = ttk.Label(canvas5, text='Defina o por que você está investindo neste título...', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_motivo_tit_window = canvas5.create_window(800, 430, anchor='sw', window=lbl_inp_motivo_tit, width=590)

    v = DoubleVar()

    inp_risco_tit = ttk.Scale(canvas5, variable=v, from_=1, to=10, orient=HORIZONTAL)
    inp_risco_tit_window = canvas5.create_window(550, 480, anchor='sw', window=inp_risco_tit, width=170)

    inp_motivo_tit = Text(canvas5, width=90, font=('Helvetica', 10), height=10)
    inp_motivo_tit.delete("1.0", "end")
    inp_motivo_tit_window = canvas5.create_window(800, 530, anchor='sw', window=inp_motivo_tit, width=590, height=90)

    bt_confirma_tit = ttk.Button = Button(canvas5, font=11, text='Confirmar', relief="solid", background='#6A5ACD', command=confirma_compra_tit)
    bt_confirma_tit_window = canvas5.create_window(660, 650, anchor='sw', window=bt_confirma_tit, width=200, height=70)

    bt_Voltar = ttk.Button = Button(canvas5, relief="solid", command=go_menuanterior4, image=img_voltar)
    bt_Voltar_window = canvas5.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)


    # -------------------------------------- FINAL TELA 5 -------------------------------------- #
    # -------------------------------------- LÓGICA TELA 5 -------------------------------------- #

    def update_suggestions_tit(event):
        list_nomes_tit.delete(0, tk.END)
        text = inp_titulo.get()

        for tit in dados_tit:
            if trata_str_emp(str(tit)).startswith(text.upper()):
                list_nomes_tit.insert(tk.END, trata_str_emp(tit))


    def select_titulo(event):
        if len(event.widget.curselection()) > 0:
            index = event.widget.curselection()

            value = event.widget.get(index)

            inp_titulo.delete(0, tk.END)
            inp_titulo.insert(0, str(value))

            cur.execute("SELECT DT_VENC FROM TITULO where nome = '" + str(value) + "' order by SUBSTR(DT_VENC, -4)")

            dados_venc = cur.fetchall()
            list_venc.delete(0, tk.END)

            for venc in dados_venc:
                vencs = list(str(venc).split())

                for x in vencs:
                    list_venc.insert(tk.END, trata_str_emp(x.strip()))

            inp_venc.config(state='normal')
            inp_venc.delete(0, tk.END)

            cur.execute("SELECT DISTINCT TIPO FROM TITULO where nome = '" + str(value) + "'")
            dado_tit_tipo = cur.fetchall()

            inp_tipo.config(state='normal')
            inp_tipo.delete(0, tk.END)
            inp_tipo.insert(0, trata_str_emp(str(dado_tit_tipo)).upper())
            inp_tipo.config(state='readonly')


    def select_venc(event):
        if (len(event.widget.curselection()) > 0) and (inp_titulo.get() != ""):
            index_venc = event.widget.curselection()

            value_venc = event.widget.get(index_venc)

            inp_venc.config(state='normal')
            inp_venc.delete(0, tk.END)
            inp_venc.insert(0, str(value_venc))
            inp_venc.config(state='readonly')


    def show_risco_tit(event):
        txt_risco = 'Risco Associado: ' + str(int(event.widget.get()))
        lbl_inp_risco_tit.config(text=txt_risco)


    cur.execute("SELECT DISTINCT nome FROM TITULO order by nome")

    dados_tit = cur.fetchall()

    for item in dados_tit:
        list_nomes_tit.insert(tk.END, trata_str_emp(item))

    inp_titulo.bind('<KeyRelease>', update_suggestions_tit)
    list_nomes_tit.bind('<Button-1>', select_titulo)
    list_venc.bind('<Button-1>', select_venc)
    inp_data_tit.bind("<KeyRelease>", lambda event: format_date(inp_data_tit))
    inp_risco_tit.bind('<Button-1>', show_risco_tit)

    lista_nm_titulos = []
    lista_venc_titulos = []
    lista_data_titulos = []
    lista_valor_titulos = []

    cur.execute("SELECT DISTINCT DT_BASE FROM TEMPTITULOS")

    data_base_tit = cur.fetchall()

    if len(data_base_tit) > 0:
        dt_controle = data_base_tit[0][0]
    else:
        dt_controle = 0

    if dt_controle != (datetime.date.today() - datetime.timedelta(days=1)).strftime('%d/%m/%Y'):

        # URL do arquivo para download
        url_download = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'

        # Diretório de destino para salvar o arquivo
        diretorio_destino = 'files'

        # Efetuar o download do arquivo
        response = requests.get(url_download, stream=True)
        with open(f'{diretorio_destino}/PrecoTaxaTesouroDireto', 'wb') as arquivo:
            for chunk in response.iter_content(1024):
                arquivo.write(chunk)

        with open('files/PrecoTaxaTesouroDireto', 'r') as arquivo:

            linhas = csv.reader(arquivo)

            lista_csv2 = list(linhas)

        arquivo.close()

        lista_csv2.pop(0)


        def obter_ano(data):
            return int(data[-4:])


        lista_csv2.sort(reverse=True, key=lambda x: obter_ano(str(x).replace(",", ".").split(";")[2]))

        control_atu = 0
        dia_menos = 1

        while control_atu == 0:

            for item in lista_csv2:

                list_temp = str(item).replace(",", ".").split(";")

                x = (datetime.date.today() - datetime.timedelta(days=dia_menos)).strftime('%d/%m/%Y')

                if list_temp[2] == (datetime.date.today() - datetime.timedelta(days=dia_menos)).strftime('%d/%m/%Y'):
                    lista_nm_titulos.append(trata_str_emp(list_temp[0]))
                    lista_venc_titulos.append(trata_str_emp(list_temp[1]))
                    lista_data_titulos.append(trata_str_emp(list_temp[2]))
                    lista_valor_titulos.append(trata_str_emp(list_temp[5]).replace(" ", ""))

                    control_atu = 1

            dia_menos = dia_menos + 1

        cur.execute("DELETE FROM TEMPTITULOS")

        for k in range(0, len(lista_nm_titulos)):
            cur.execute('insert into TEMPTITULOS(NOME, DT_VENC, DT_BASE, VALOR_TIT) values(?, ?, ?, ?)',
                        (lista_nm_titulos[k], lista_venc_titulos[k], lista_data_titulos[k], float(str(lista_valor_titulos[k]).replace(",", "."))))
            con.commit()

        cur.execute("SELECT a.NOME," 
                    "       a.DT_VENC " 
                    "from TEMPTITULOS as a " 
                    "left join TITULO as b " 
                    "on (UPPER(a.NOME) = b.NOME and a.DT_VENC = b.DT_VENC) " 
                    "WHERE (b.NOME IS NULL and b.DT_VENC IS NULL) ")

        lst_add_nm = []
        lst_add_venc = []

        dadoss = cur.fetchall()

        for item in dadoss:
            lst_add_nm.append(item[0])
            lst_add_venc.append(item[1])

        for k in range(0, len(lst_add_nm)):
            cur.execute('insert into TITULO(NOME, DT_VENC, TIPO) values(?, ?, ?)', (str(lst_add_nm[k]).upper().strip(), lst_add_venc[k], "TESOURO"))
            con.commit()


    # -------------------------------------- TELA 6 (Tabela de títulos) -------------------------------------- #

    def go_menuanterior5():
        canvas6.pack_forget()
        canvas1.pack()


    def abrir_mensagem(event):
        item_id = table_fix.focus()

        if len(dados_tabela_tit) != len(table_fix.get_children()):

            cur.execute(SQL_POSICAO_TITULOS)

            dados_tabela_tit2 = cur.fetchall()

            messagebox.showinfo('Definição de Riscos', dados_tabela_tit2[int(str(item_id)[-1:]) - 1][4])

        else:

            messagebox.showinfo('Definição de Riscos', dados_tabela_tit[int(str(item_id)[-1:]) - 1][4])


    canvas6 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas6.create_image(0, 0, image=bg_image_tk, anchor='nw')

    bt_Voltar = ttk.Button = Button(canvas6, relief="solid", command=go_menuanterior5, image=img_voltar)
    bt_Voltar_window = canvas6.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    table_fix = ttk.Treeview(canvas6, columns=('Vencimento', 'Tipo', 'Risco', 'Definicao', 'Valor', 'Papeis', 'Rentabilidade'))

    style = ttk.Style()

    style.configure("Treeview", font=("Arial", 12), padding=(0, 35, 0, 35), background='#B0C4DE')
    style.configure("Treeview.Heading", font=("Arial", 12, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

    table_fix.configure(style="Treeview.Heading")
    table_fix.configure(style="Treeview")

    table_fix.heading('#0', text='Titulo')
    table_fix.heading('Vencimento', text='Vencimento')
    table_fix.heading('Tipo', text='Tipo')
    table_fix.heading('Risco', text='Risco')
    table_fix.heading('Definicao', text='Definição')
    table_fix.heading('Valor', text='Valor Total')
    table_fix.heading('Papeis', text='Papeis Totais')
    table_fix.heading('Rentabilidade', text='Rentabilidade (%)')

    cur.execute(SQL_POSICAO_TITULOS)

    dados_tabela_tit = cur.fetchall()

    table_fix.column("#0", width=230)
    table_fix.column("Vencimento", width=110)
    table_fix.column("Tipo", width=110)
    table_fix.column("Risco", width=50)
    table_fix.column("Valor", width=95)
    table_fix.column("Papeis", width=105)
    table_fix.column("Rentabilidade", width=140)

    table_fix.configure(padding=10)

    table_fix_window = canvas6.create_window(170, 700, anchor='sw', window=table_fix, width=1210, height=450)

    table_fix.bind("<Double-1>", abrir_mensagem)


    # -------------------------------------- TELA 7 (Importar nota de Negociação) -------------------------------------- #

    def go_menuanterior6():
        canvas7.pack_forget()
        canvas2.pack()


    def abrir_arquivo():

        arquivo = filedialog.askopenfilename()

        inp_arquivo.config(state='normal')
        inp_arquivo.delete(0, tk.END)
        inp_arquivo.insert(0, str(arquivo))
        inp_arquivo.config(state='readonly')

        trata_pdf_nota(arquivo)


    canvas7 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas7.create_image(0, 0, image=bg_image_tk, anchor='nw')

    inp_arquivo = ttk.Entry(canvas7, font=('Helvetica', 14))
    inp_arquivo_window = canvas7.create_window(400, 400, anchor='sw', window=inp_arquivo, width=730, height=70)
    inp_arquivo.config(state='readonly')

    lb_arquivo = ttk.Label(canvas7, font=('Helvetica', 18, 'bold'), text='Carregue sua nota de Negociação (Formato aceito: PDF)', foreground='#171F3D', anchor=CENTER, background="#1E90FF", padding=4)
    lb_arquivo_window = canvas7.create_window(400, 350, anchor='sw', window=lb_arquivo, width=730)

    lb_nota = ttk.Label(canvas7, font=('Helvetica', 10, 'bold'), text='*No momento atual, apenas notas da corretora Clear são aceitas.', foreground='black', background=None, anchor=W, padding=4)
    lb_nota_window = canvas7.create_window(400, 450, anchor='sw', window=lb_nota, width=450)

    diretorio_base = os.path.dirname(os.path.abspath(__file__))
    diretorio_upd_arq = os.path.join(diretorio_base, 'img/widgets/upd_arquivo.png')
    imagem_fundo2 = PhotoImage(file=diretorio_upd_arq)

    bt_carrega_nota = ttk.Button = Button(canvas7, relief="solid", image=imagem_fundo2, command=abrir_arquivo)
    bt_carrega_nota_window = canvas7.create_window(1150, 400, anchor='sw', window=bt_carrega_nota, width=160, height=93)

    bt_Voltar = ttk.Button = Button(canvas7, relief="solid", command=go_menuanterior6, image=img_voltar)
    bt_Voltar_window = canvas7.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    # -------------------------------------- LÓGICA TELA 7 -------------------------------------- #

    def trata_pdf_nota(arq):

        try:

            def is_pdf(arquivo):
                mime_type, encoding = mimetypes.guess_type(arquivo)
                return mime_type == 'application/pdf'

            if is_pdf(arq):

                nota = open(arq.replace("/", "\\"), 'rb')

                pdf = PyPDF2.PdfReader(nota)

                pagina = pdf.pages[0]
                texto = pagina.extract_text()

                if (texto.count("CLEAR CORRETORA - GRUPO XP") > 0 and texto.count("02.332.886/0011-78") > 0):

                    header = texto[texto.index("Negócios realizados") + 19 + 1:texto.index("D/C") + 3]

                    linhas = header.strip().split('\n')
                    colunas = [linha.strip() for linha in linhas if linha not in ('Q', 'Negociação', 'Prazo', 'Obs. (*)')]

                    linhas = texto[texto.index("D/C") + 3:].strip().split("1-BOVESPA")
                    campos = [linha.strip() for linha in linhas if linha != '']

                    lst_compra_venda, lst_tp_mercado, lst_titulo, lst_quantidade, lst_preco, lst_preco_final, lst_dc = [[] for _ in range(7)]

                    for i in range(0, len(campos)):
                        linhas = campos[i].strip().split('\n')
                        colunas = [linha.strip() for linha in linhas if linha not in ('#', 'EJ', 'N1', 'N2')]

                        lst_compra_venda.append(colunas[0])
                        lst_tp_mercado.append(colunas[1])
                        lst_titulo.append(colunas[2].replace("          ", " ")) if colunas[3].isnumeric() else lst_titulo.append(colunas[2].replace("          ", " ") + " " + colunas[3])
                        lst_quantidade.append(colunas[4]) if colunas[4].isnumeric() else lst_quantidade.append(colunas[3])
                        lst_preco.append(colunas[5]) if colunas[4].isnumeric() else lst_preco.append(colunas[4])
                        lst_preco_final.append(colunas[6]) if colunas[4].isnumeric() else lst_preco_final.append(colunas[5])
                        lst_dc.append(colunas[7]) if colunas[4].isnumeric() else lst_dc.append(colunas[6])

                    data = {
                        "CompraVenda": lst_compra_venda,
                        "TpMercado": lst_tp_mercado,
                        "Titulo": lst_titulo,
                        "Preço": lst_preco,
                        "Quant": lst_quantidade,
                        "PreçoFinal": lst_preco_final,
                        "D/C": lst_dc
                    }

                    df = pd.DataFrame(data)

                    # Só compras no Fracionário e FIIS (LOTES não serão registrados)
                    df_final = df[(df["TpMercado"] == "FRACIONARIO") | (df["TpMercado"] == "VISTA")]

                    dt_negoc = texto[texto.index("Data pregão") + 11:texto.index("CLEAR CORRETORA")]

                    for indice, linha in df_final.iterrows():

                        empresa_ticker = linha['Titulo']
                        preco_compra = linha['Preço']
                        quant_compra = linha['Quant']

                        nome_empresa, ticker_empresa = busca_ticker(empresa_ticker)

                        if (nome_empresa is not False) and (ticker_empresa is not False):

                            registra_compra_nota(nome_empresa, dt_negoc, preco_compra, quant_compra, ticker_empresa)

                        else:

                            texto_info = "Houve um erro ao registrar a ação na empresa " + empresa_ticker
                            lbl_info = messagebox.Message(title='Investify', message=texto_info)
                            lbl_info.show()

                    texto_info = "Nota Importada! Suas posições nas empresas foram atualizadas."
                    lbl_info = messagebox.Message(title='Investify', message=texto_info)
                    lbl_info.show()

                else:
                    texto_info = "No momento apenas notas da corretora CLEAR são aceitos."
                    lbl_info = messagebox.Message(title='Investify', message=texto_info)
                    lbl_info.show()

            else:
                texto_info = "Erro. O arquivo deve ser um PDF."
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()

        except Exception as e:
            print("Erro: " + e)


    def busca_ticker(str_empresa_ticker):

            if str(str_empresa_ticker).split(" ")[0].strip() == "FII":
                nm_titulo = str(str_empresa_ticker).split(" ")[0] + " " + str(str_empresa_ticker).split(" ")[1] + " " + str(str_empresa_ticker).split(" ")[2]

                cur.execute("SELECT ticker FROM FII where nome = '" + str(nm_titulo) + "'")

                dados_ticker = cur.fetchall()

            else:
                nm_titulo = str(str_empresa_ticker).split(" ")[0].strip()
                tipo_acao = str(str_empresa_ticker).split(" ")[1].strip()

                if tipo_acao not in ["ON", "PN", "PNA", "PNB"]:
                    nm_titulo += " " + str(str_empresa_ticker).split(" ")[1].strip()
                    tipo_acao = str(str_empresa_ticker).split(" ")[2].strip()

                cur.execute("SELECT ticker FROM EMPRESA where nome = '" + str(nm_titulo) + "'")

                dados_ticker = cur.fetchall()

                if len(dados_ticker) == 0:
                    query = "SELECT ticker FROM EMPRESA where nome LIKE ?"
                    cur.execute(query, ('%' + str(nm_titulo) + '%',))
                    dados_ticker = cur.fetchall()

                if len(dados_ticker) == 0:
                    query = "SELECT ticker FROM EMPRESA where nome LIKE ?"
                    cur.execute(query, ('%' + str(nm_titulo).split(" ")[0] + '%',))
                    dados_ticker = cur.fetchall()

            tickers = []

            if len(dados_ticker) != 0:

                if str(str_empresa_ticker).split(" ")[0].strip() != "FII":
                    ticker_teste = str(dados_ticker).split("   ")

                    for ticker in ticker_teste:
                        tickers.append(ticker.replace("[", "").replace("]", "").replace("(", "").replace(")", "").replace(",", "").replace("'", ""))
                else:
                    ticker_teste = trata_str_emp(str(dados_ticker))
                    tickers.append(ticker_teste)

                ticker_final = ""

                if len(tickers) == 1:

                    ticker_final = tickers[0]

                else:

                    if tipo_acao == "ON":
                        ticker_final = next(item for item in tickers if item.endswith("3"))
                    elif tipo_acao == "PN":
                        ticker_final = next(item for item in tickers if item.endswith("4"))
                    elif tipo_acao == "PNA":
                        ticker_final = next(item for item in tickers if item.endswith("5"))
                    elif tipo_acao == "PNB":
                        ticker_final = next(item for item in tickers if item.endswith("6"))


                return nm_titulo, ticker_final

            else:

                return False, False

    def registra_compra_nota(empresa, data, valor, quantidade, ticker):

        try:

            if str(empresa).split(" ")[0] != "FII":

                cur.execute("SELECT ID FROM EMPRESA where nome = '" + empresa.upper().strip() + "'")

                dado_id_emp = cur.fetchall()

                if len(dado_id_emp) == 0:

                    query = "SELECT ID FROM EMPRESA where nome LIKE ?"
                    cur.execute(query, ('%' + empresa.upper().strip() + '%',))

                    dado_id_emp = cur.fetchall()

                if len(dado_id_emp) == 0:
                    query = "SELECT ID FROM EMPRESA where nome LIKE ?"
                    cur.execute(query, ('%' + empresa.upper().strip().split(" ")[0] + '%',))

                    dado_id_emp = cur.fetchall()

            else:

                cur.execute("SELECT ID FROM FII where TICKER = '" + ticker.upper() + "'")

                dado_id_emp = cur.fetchall()


            if len(dado_id_emp) != 0:

                id_titulo = dado_id_emp[0][0]

                if str(empresa).split(" ")[0] != "FII":

                    cur.execute('insert into COMPRA(DATA, VALOR_ACAO, QUANTIDADE, UTICKER, FONTE , ID) values(?, ?, ?, ?, ?, ?)', (str(data).strip(), float(str(valor).replace(",", ".")), int(quantidade), str(ticker).strip(), "Nota" , int(id_titulo)))
                    con.commit()

                    cur.execute("SELECT POSICAO_ID FROM POSICAO where ID = " + str(id_titulo) + "")

                else:

                    cur.execute('insert into COMPRA(DATA, VALOR_ACAO, QUANTIDADE, UTICKER, FONTE , FID) values(?, ?, ?, ?, ?, ?)', (str(data).strip(), float(str(valor).replace(",", ".")), int(quantidade), str(ticker).strip(), "Nota", int(id_titulo)))
                    con.commit()

                    cur.execute("SELECT POSICAO_ID FROM POSICAO where FID = " + str(id_titulo) + "")

                dado_id_posicao = cur.fetchall()

                if len(dado_id_posicao) > 0:

                    if str(empresa).split(" ")[0] != "FII":

                        cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                                    "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                                    "       SUM(QUANTIDADE)" \
                                    " FROM COMPRA where ID = " + str(id_titulo) + " " \
                                                                                   " GROUP BY ID")

                        dados_posicao = cur.fetchall()

                        cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE ID = ? AND UTICKER = ?',
                                    (dados_posicao[0][0], dados_posicao[0][1],
                                     dados_posicao[0][2], id_titulo, str(ticker).strip()))

                    else:

                        cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                                    "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                                    "       SUM(QUANTIDADE)" \
                                    " FROM COMPRA where FID = " + str(id_titulo) + " " \
                                                                                  " GROUP BY FID")

                        dados_posicao = cur.fetchall()

                        cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE FID = ? AND UTICKER = ?',
                                    (dados_posicao[0][0], dados_posicao[0][1],
                                     dados_posicao[0][2], id_titulo, str(ticker).strip()))

                    con.commit()

                else:

                    if str(empresa).split(" ")[0] != "FII":

                        cur.execute('insert into POSICAO(RISCO, DEFINICAO, VALORTOTAL, PRECOMEDIO, PAPEISTOTAIS, UTICKER, ID) values(?, ?, ?, ?, ?, ?, ?)',
                                    (0, "",
                                     float(str(valor).replace(",", ".")) * int(quantidade),
                                     (float(str(valor).replace(",", ".")) * int(quantidade)) / int(quantidade),
                                     int(quantidade), str(ticker).strip(), id_titulo))

                    else:

                        cur.execute('insert into POSICAO(RISCO, DEFINICAO, VALORTOTAL, PRECOMEDIO, PAPEISTOTAIS, UTICKER, FID) values(?, ?, ?, ?, ?, ?, ?)',
                                    (0, "",
                                     float(str(valor).replace(",", ".")) * int(quantidade),
                                     (float(str(valor).replace(",", ".")) * int(quantidade)) / int(quantidade),
                                     int(quantidade), str(ticker).strip(), id_titulo))

                    con.commit()


        except Exception as e:
            print(f"Erro genérico: {e}")

    # -------------------------------------- TELA 8 (Sobre - Empresa) -------------------------------------- #

    def go_menuanterior7():

        filtro = lb_empresa.cget('text')

        cur.execute("SELECT COUNT(*) " \
                    " FROM COMPRA where UTICKER = '" + str(filtro) + "' ")

        quant_compras = cur.fetchall()

        if quant_compras[0][0] != 0:

            cur.execute(SQL_RISCO_EMP)

            dados_tabela = cur.fetchall()

            dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

            risco = dados_filtrados[0][1]

            risco_new = v2.get()

            cur.execute(SQL_DEFINICAO_EMP)

            dados_tabela = cur.fetchall()

            dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

            definicao = dados_filtrados[0][1]

            definicao_new = inp_txt_notas.get("1.0", "end-1c")

            if (risco != risco_new) or (definicao != definicao_new):

                risco_alt = int(risco_new if (risco != risco_new) else risco)
                definicao_alt = str(definicao_new if (definicao != definicao_new) else definicao)

                result = messagebox.askyesno("Confirmação", "Salvar as Alterações?")
                if result:

                    cur.execute('UPDATE POSICAO SET RISCO = ?, DEFINICAO = ? WHERE UTICKER = ?',
                                (risco_alt, definicao_alt, str(filtro)))

                    con.commit()

        canvas8.pack_forget()
        canvas4.pack()


    def set_tela_empresa(estado):

        canvas8.itemconfig(1, state=estado)
        canvas8.itemconfig(lb_ind_cotacao_window, state=estado)
        canvas8.itemconfig(lb_ind_cotacao_vlr_window, state=estado)
        canvas8.itemconfig(lb_ind_pl_window, state=estado)
        canvas8.itemconfig(lb_ind_pl_vlr_window, state=estado)
        canvas8.itemconfig(lb_ind_pvp_window, state=estado)
        canvas8.itemconfig(lb_ind_pvp_vlr_window, state=estado)
        canvas8.itemconfig(lb_ind_dy_window, state=estado)
        canvas8.itemconfig(lb_ind_dy_vlr_window, state=estado)
        canvas8.itemconfig(lb_sob_emp_window, state=estado)
        canvas8.itemconfig(inp_txt_emp_window, state=estado)


    def set_tela_definicao(estado):

        canvas8.itemconfig(bt_def_posicao_window, state=estado)
        canvas8.itemconfig(bt_def_indicador_window, state=estado)
        canvas8.itemconfig(bt_def_risco_window, state=estado)
        canvas8.itemconfig(bt_def_notas_window, state=estado)
        canvas8.itemconfig(frame_def_window, state=estado)


    def set_tela_definicao_pos(estado):

        canvas8.itemconfig(lb_def_valor_atu_window, state=estado)
        canvas8.itemconfig(lb_def_valor_atu_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_valor_inv_window, state=estado)
        canvas8.itemconfig(lb_def_valor_inv_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_rentab_window, state=estado)
        canvas8.itemconfig(lb_def_rentab_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_medio_window, state=estado)
        canvas8.itemconfig(lb_def_medio_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_papeis_window, state=estado)
        canvas8.itemconfig(lb_def_papeis_vlr_window, state=estado)
        canvas8.itemconfig(def_chart_window, state=estado)


    def set_tela_definicao_ind(estado):

        canvas8.itemconfig(lb_def_pl_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_pl_window, state=estado)
        canvas8.itemconfig(lb_def_pvp_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_pvp_window, state=estado)
        canvas8.itemconfig(lb_def_dy_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_dy_window, state=estado)
        canvas8.itemconfig(lb_def_pay_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_pay_window, state=estado)
        canvas8.itemconfig(lb_def_mar_bt_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_mar_bt_window, state=estado)
        canvas8.itemconfig(lb_def_mar_liq_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_mar_liq_window, state=estado)
        canvas8.itemconfig(lb_def_roe_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_roe_window, state=estado)
        canvas8.itemconfig(lb_def_divida_vlr_window, state=estado)
        canvas8.itemconfig(lb_def_divida_window, state=estado)


    def set_tela_definicao_risco(estado):

        canvas8.itemconfigure(def_inp_risco_window, state=estado)
        canvas8.itemconfigure(lb_def_risco_window, state=estado)
        canvas8.itemconfigure(lb_def_risco_vlr_window, state=estado)


    def set_tela_definicao_notas(estado):

        canvas8.itemconfigure(inp_txt_notas_window, state=estado)


    def set_tela_lancamentos(estado):

        canvas8.itemconfigure(table_lanc_window, state=estado)


    def set_tela_lancamentos_edit(estado):

        canvas8.itemconfigure(frame_lanc_window, state=estado)
        canvas8.itemconfigure(inp_lanc_data_window, state=estado)
        canvas8.itemconfigure(inp_lanc_valor_window, state=estado)
        canvas8.itemconfigure(inp_lanc_quant_window, state=estado)
        canvas8.itemconfigure(bt_save_lanc_window, state=estado)
        canvas8.itemconfigure(bt_del_lanc_window, state=estado)
        canvas8.itemconfigure(bt_lanc_close_window, state=estado)


    def carrega_lancamentos(ticker):

        cur.execute(SQL_ALL_COMPRAS)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[3] == filtro]

        if table_lanc.get_children():
            table_lanc.delete(*table_lanc.get_children())

        for l in range(0, len(dados_filtrados)):
            table_lanc.insert('', 'end', text=dados_filtrados[l][0], values=(dados_filtrados[l][1], dados_filtrados[l][2], dados_filtrados[l][4]))

        for col in table_lanc["columns"]:
            table_lanc.column(col, anchor="center")


    def botao_desativo(event):
        pass  # Não faz nada quando o botão é clicado


    def edit_lanc(event):
        indice = table_lanc.focus()

        if indice:
            valor = table_lanc.item(indice, "text")
            valores = table_lanc.item(indice, "values")

            inp_lanc_data.delete(0, tk.END)
            inp_lanc_valor.delete(0, tk.END)
            inp_lanc_quant.delete(0, tk.END)

            inp_lanc_data.insert(0, valor)
            inp_lanc_valor.insert(0, valores[0])
            inp_lanc_quant.insert(0, valores[1])

            set_tela_lancamentos_edit('normal')

            bt_empresa.bind("<Button-1>", botao_desativo)
            bt_definicao.bind("<Button-1>", botao_desativo)
            bt_lancamentos.bind("<Button-1>", botao_desativo)


    def fecha_frame(event):
        set_tela_lancamentos_edit('hidden')

        bt_empresa.bind("<Button-1>", muda_cor_botao)
        bt_definicao.bind("<Button-1>", muda_cor_botao)
        bt_lancamentos.bind("<Button-1>", muda_cor_botao)


    def muda_cor_botao(event):
        bt_clicado = event.widget
        bt_clicado.configure(background='#171F3D')

        texto_botao_clicado = bt_clicado.cget("text")
        if texto_botao_clicado == "EMPRESA":
            bt_definicao.configure(background='#1E90FF')
            bt_lancamentos.configure(background='#1E90FF')

            set_tela_empresa("normal")

            lb_empresa_window = canvas8.create_window(370, 185, anchor='sw', window=lb_empresa)

            set_tela_definicao_pos("hidden")

            set_tela_definicao('hidden')

            set_tela_definicao_ind("hidden")

            set_tela_definicao_risco('hidden')

            set_tela_definicao_notas('hidden')

            set_tela_lancamentos('hidden')

        elif texto_botao_clicado == "DEFINIÇÃO":
            bt_empresa.configure(background='#1E90FF')
            bt_lancamentos.configure(background='#1E90FF')

            bt_def_posicao.configure(background='#171F3D')
            bt_def_indicador.configure(background='#1E90FF')
            bt_def_risco.configure(background='#1E90FF')
            bt_def_notas.configure(background='#1E90FF')

            set_tela_empresa("hidden")

            lb_empresa_window = canvas8.create_window(140, 130, anchor='sw', window=lb_empresa)

            set_tela_definicao_pos("normal")
            set_tela_definicao('normal')
            set_tela_definicao_ind('hidden')
            set_tela_definicao_risco('hidden')
            set_tela_definicao_notas('hidden')

            set_tela_lancamentos('hidden')

        elif texto_botao_clicado == "LANÇAMENTOS":
            bt_empresa.configure(background='#1E90FF')
            bt_definicao.configure(background='#1E90FF')

            set_tela_empresa("hidden")

            lb_empresa_window = canvas8.create_window(140, 130, anchor='sw', window=lb_empresa)

            set_tela_definicao_pos("hidden")
            set_tela_definicao('hidden')

            style = ttk.Style()

            style.configure("Treeview", font=("Arial", 14), padding=(0, 35, 0, 35), background='#B0C4DE', rowheight=50)
            style.configure("Treeview.Heading", font=("Arial", 14, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

            table_lanc.configure(style="Treeview.Heading")
            table_lanc.configure(style="Treeview")

            set_tela_lancamentos('normal')


    def muda_cor_def_botao(event):
        bt_clicado = event.widget
        bt_clicado.configure(background='#171F3D')

        texto_botao_clicado = bt_clicado.cget("text")
        if texto_botao_clicado == "Posição":
            bt_def_indicador.configure(background='#1E90FF')
            bt_def_risco.configure(background='#1E90FF')
            bt_def_notas.configure(background='#1E90FF')

            set_tela_definicao_pos("normal")

            set_tela_definicao_ind("hidden")

            set_tela_definicao_risco('hidden')

            set_tela_definicao_notas('hidden')

        elif texto_botao_clicado == "Indicadores":
            bt_def_posicao.configure(background='#1E90FF')
            bt_def_risco.configure(background='#1E90FF')
            bt_def_notas.configure(background='#1E90FF')

            set_tela_definicao_pos("hidden")

            set_tela_definicao_ind("normal")

            set_tela_definicao_risco('hidden')

            set_tela_definicao_notas('hidden')

        elif texto_botao_clicado == "Risco":
            bt_def_posicao.configure(background='#1E90FF')
            bt_def_indicador.configure(background='#1E90FF')
            bt_def_notas.configure(background='#1E90FF')

            set_tela_definicao_pos("hidden")

            set_tela_definicao_ind("hidden")

            set_tela_definicao_risco('normal')

            set_tela_definicao_notas('hidden')

        elif texto_botao_clicado == "Notas":
            bt_def_posicao.configure(background='#1E90FF')
            bt_def_indicador.configure(background='#1E90FF')
            bt_def_risco.configure(background='#1E90FF')

            set_tela_definicao_pos("hidden")

            set_tela_definicao_ind("hidden")

            set_tela_definicao_risco('hidden')

            set_tela_definicao_notas('normal')


    def carrega_ind_pl(empresa, valor_atual, ticker):

        try:

            cur.execute("SELECT TICKER FROM EMPRESA where NOME = '" + empresa + "'")

            tickers = cur.fetchall()

            acoes_negociacao = 0
            for tick in str(tickers[0]).split("   "):
                t = tick

                if not trata_str_emp(t).endswith("11"):

                    emp = yf.Ticker(trata_str_emp(t) + ".SA")

                    acoes_negociacao += emp.info["sharesOutstanding"]

            emp = yf.Ticker(ticker + ".SA")

            lucro_liquido_trimestral = emp.quarterly_income_stmt.loc['Net Income']

            lpa = lucro_liquido_trimestral.sum() / acoes_negociacao

            return round(valor_atual / lpa, 2)

        except Exception:
                return "-"


    def carrega_ind_pvp(empresa, valor_atual, ticker):

        try:

            cur.execute("SELECT TICKER FROM EMPRESA where NOME = '" + empresa + "'")

            tickers = cur.fetchall()

            acoes_negociacao = 0
            for tick in str(tickers[0]).split("   "):
                t = tick

                if not trata_str_emp(t).endswith("11"):
                    emp = yf.Ticker(trata_str_emp(t) + ".SA")

                    acoes_negociacao += emp.info["sharesOutstanding"]

            emp = yf.Ticker(ticker + ".SA")

            balance_sheet = emp.balance_sheet

            patrimonio_liquido = balance_sheet.loc["Stockholders Equity"].iloc[0]

            vpa = patrimonio_liquido / acoes_negociacao

            return round(valor_atual / vpa, 2)

        except Exception:
                return "-"


    def carrega_ind_dy(valor_atual, ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=365)

            df_filtrado = emp.history(start=start_date, end=end_date)["Dividends"]

            dyield = (df_filtrado.sum() / valor_atual) * 100

            return round(dyield, 2)

        except Exception:
                return "-"


    def carrega_txt_emp(empresa):

        cur.execute("SELECT DESCRICAO FROM EMPRESA where NOME = '" + empresa + "'")

        texto = cur.fetchall()

        return texto[0][0]


    def carrega_ind_payout(ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            hist = emp.info
            df = pd.DataFrame(hist)
            pay = round(df['payoutRatio'].loc[0] * 100, 2)

            return pay

        except Exception:
                return "-"


    def carrega_ind_mg_bruta(ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            hist = emp.info
            df = pd.DataFrame(hist)
            margem = round(df['grossMargins'].loc[0] * 100, 2)

            return margem

        except Exception:
                return "-"


    def carrega_ind_mg_liq(ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            hist = emp.info
            df = pd.DataFrame(hist)
            margem = round(df['profitMargins'].loc[0] * 100, 2)

            return margem

        except Exception:
                return "-"


    def carrega_ind_roe(ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            hist = emp.info
            df = pd.DataFrame(hist)
            retorno = round(df['returnOnEquity'].loc[0] * 100, 2)

            return retorno

        except Exception:
                return "-"


    def carrega_ind_divida(ticker):

        try:

            emp = yf.Ticker(ticker + ".SA")

            hist = emp.info
            df = pd.DataFrame(hist)
            divida = round(df['debtToEquity'].loc[0] / 100, 2)

            return divida

        except Exception:
                return "-"


    def carrega_tela_empresa(empresa, ticker, valor_atual):

        valor_pl = str(carrega_ind_pl(empresa, valor_atual, ticker))
        valor_pvp = str(carrega_ind_pvp(empresa, valor_atual, ticker))
        valor_dy = str(carrega_ind_dy(valor_atual, ticker))
        texto_emp = str(carrega_txt_emp(empresa))

        global imagem_emp

        diretorio_foto_emp = os.path.join(diretorio_base, 'img/empresas/' + empresa + '.jpeg')

        caminho = diretorio_foto_emp

        imagem_pil = Image.open(caminho if os.path.exists(caminho) else diretorio_foto_white)
        imagem_emp = ImageTk.PhotoImage(imagem_pil)
        img_empresa_nota.configure(image=imagem_emp)

        lb_empresa.configure(text=ticker if ticker != "" else "")

        lb_ind_cotacao_vlr.configure(text=round(valor_atual, 2) if str(valor_atual) != "" else "")

        lb_ind_pl_vlr.configure(text=valor_pl if valor_pl != "" else "")

        lb_ind_pvp_vlr.configure(text=valor_pvp if valor_pvp != "" else "")

        lb_ind_dy_vlr.configure(text=valor_dy if valor_dy != "" else "")

        inp_txt_emp.delete("1.0", "end")
        inp_txt_emp.insert("1.0", texto_emp if texto_emp != "" else "")


    def carrega_tela_def_posicao(empresa, ticker, valor_total, p_medio, papeis, valor_atual, rentabilidade):

        lb_def_valor_atu_vlr.configure(text=valor_atual)

        lb_def_valor_inv_vlr.configure(text=valor_total)

        lb_def_rentab_vlr.configure(text=rentabilidade)
        lb_def_rentab_vlr.configure(foreground='red' if float(rentabilidade) < -2.0 else '#DAA520' if float(rentabilidade) < 0.0 else '#32CD32' if float(rentabilidade) < 5.0 else '#006400')

        lb_def_medio_vlr.configure(text=p_medio)

        lb_def_papeis_vlr.configure(text=papeis)

        cur.execute(SQL_APORTES_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        meses = {}
        for i in range(0, 5):
            mes_atual = datetime.datetime.now().month - i
            if mes_atual <= 0:
                mes_atual += 12
            nome_mes = calendar.month_name[mes_atual]
            meses[nome_mes] = mes_atual

        meses_sort = dict(sorted(meses.items(), key=lambda item: item[1]))

        for item in dados_filtrados:

            if int(item[1]) in meses_sort.values():
                chave_mes = [chave for chave, valor in meses_sort.items() if valor == int(item[1])][0]
                meses_sort.update({chave_mes: item[2]})

        for chave, valor in meses_sort.items():
            if not isinstance(valor, float):
                meses_sort[chave] = 0

        ax.clear()
        ax.set_xlabel('Meses')
        ax.set_ylabel('Valores')
        ax.set_title('Aportes', color="#171F3D", fontweight='bold')
        ax.bar(list(meses_sort.keys()), list(meses_sort.values()), color="#171F3D")

        chart.draw()


    def carrega_tela_def_ind(empresa, ticker, valor_atual):

        valor_pl = str(carrega_ind_pl(empresa, valor_atual, ticker))
        valor_pvp = str(carrega_ind_pvp(empresa, valor_atual, ticker))
        valor_dy = str(carrega_ind_dy(valor_atual, ticker))
        valor_pay = str(carrega_ind_payout(ticker))
        valor_margem_bruta = str(carrega_ind_mg_bruta(ticker))
        valor_margem_liquida = str(carrega_ind_mg_liq(ticker))
        valor_roe = str(carrega_ind_roe(ticker))
        valor_divida = str(carrega_ind_divida(ticker))

        lb_def_pl_vlr.configure(text=valor_pl)
        lb_def_pvp_vlr.configure(text=valor_pvp)
        lb_def_dy_vlr.configure(text=valor_dy)
        lb_def_pay_vlr.configure(text=valor_pay)
        lb_def_mar_bt_vlr.configure(text=valor_margem_bruta)
        lb_def_mar_liq_vlr.configure(text=valor_margem_liquida)
        lb_def_roe_vlr.configure(text=valor_roe)
        lb_def_divida_vlr.configure(text=valor_divida)


    def carrega_tela_def_risco(ticker):

        cur.execute(SQL_RISCO_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        risco = dados_filtrados[0][1]

        v2.set(value=float(risco))
        lb_def_risco_vlr.configure(text=risco)


    def carrega_tela_def_risco(ticker):

        cur.execute(SQL_RISCO_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        risco = dados_filtrados[0][1]

        v2.set(value=float(risco))
        lb_def_risco_vlr.configure(text=v2.get(), foreground='#006400' if float(risco) < 4.0 else '#32CD32' if float(risco) < 6.0 else '#DAA520' if float(risco) < 9.0 else 'red')


    def carrega_tela_def_definicao(ticker):

        cur.execute(SQL_DEFINICAO_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        definicao = dados_filtrados[0][1]

        inp_txt_notas.delete("1.0", "end")
        inp_txt_notas.insert("end", definicao)


    def carrega_tela_lancamentos(ticker):

        carrega_lancamentos(ticker)


    def salva_lanc():

        ticker = lb_empresa.cget('text')

        indice = table_lanc.focus()

        if indice:
            valor = table_lanc.item(indice, "text")
            valores = table_lanc.item(indice, "values")

            data_new = inp_lanc_data.get()
            valor_acao_new = inp_lanc_valor.get()
            quantidade_new = inp_lanc_quant.get()

            result = messagebox.askyesno("Confirmação", "Salvar as Alterações?")
            if result:

                cur.execute('UPDATE COMPRA SET DATA = ?, VALOR_ACAO = ?, QUANTIDADE = ? WHERE UTICKER = ? AND DATA = ? AND VALOR_ACAO = ? AND QUANTIDADE = ? AND FONTE = ?',
                            (data_new, float(valor_acao_new), int(quantidade_new), ticker, valor, float(valores[0]), int(valores[1]), valores[2]))

                con.commit()

                cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                            "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                            "       SUM(QUANTIDADE)" \
                            " FROM COMPRA where UTICKER = '" + str(ticker) + "' " \
                            " GROUP BY UTICKER")

                dados_posicao = cur.fetchall()

                cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE UTICKER = ?',
                            (dados_posicao[0][0], dados_posicao[0][1],
                             dados_posicao[0][2], str(ticker)))

                con.commit()

                texto_info = "Lançamento Atualizado!"
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    def del_lanc():

        ticker = lb_empresa.cget('text')

        indice = table_lanc.focus()

        if indice:
            valor = table_lanc.item(indice, "text")
            valores = table_lanc.item(indice, "values")

            result = messagebox.askyesno("Confirmação", "Excluir o lançamento?")
            if result:

                cur.execute('DELETE FROM COMPRA WHERE UTICKER = ? AND DATA = ? AND VALOR_ACAO = ? AND QUANTIDADE = ? AND FONTE = ?',
                            (ticker, valor, float(valores[0]), int(valores[1]), valores[2]))

                con.commit()

                cur.execute("SELECT COUNT(*) " \
                            " FROM COMPRA where UTICKER = '" + str(ticker) + "' ")

                quant_compras = cur.fetchall()

                if quant_compras[0][0] == 0:

                    cur.execute('DELETE FROM POSICAO WHERE UTICKER = ?', (str(ticker),))

                else:

                    cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                                "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                                "       SUM(QUANTIDADE)" \
                                " FROM COMPRA where UTICKER = '" + str(ticker) + "' " \
                                                                                 " GROUP BY UTICKER")

                    dados_posicao = cur.fetchall()

                    cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE UTICKER = ?',
                                (dados_posicao[0][0], dados_posicao[0][1],
                                 dados_posicao[0][2], str(ticker)))


                con.commit()

                texto_info = "Lançamento deletado."
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    canvas8 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())

    diretorio_foto_white = os.path.join(diretorio_base, 'img/empresas/white.jpg')
    imagem_pil = Image.open(diretorio_foto_white)
    imagem_white = ImageTk.PhotoImage(imagem_pil)
    img_empresa_nota = tk.Label(canvas8, relief="solid", image=imagem_white)
    canvas8.create_window(150, 240, anchor='sw', window=img_empresa_nota, width=190, height=190)

    lb_empresa = ttk.Label(canvas8, font=('Helvetica', 40, 'bold'), text='', foreground='#171F3D', background='white', anchor=W, padding=4)
    lb_empresa_window = canvas8.create_window(370, 185, anchor='sw', window=lb_empresa)

    lb_ind_cotacao = ttk.Label(canvas8, font=('Helvetica', 24), text='Cotação', foreground='black', background='white', anchor=N, padding=5, borderwidth=2, relief='ridge')
    lb_ind_cotacao_window = canvas8.create_window(800, 120, anchor='sw', window=lb_ind_cotacao, width=140)

    lb_ind_cotacao_vlr = ttk.Label(canvas8, font=('Helvetica', 29, 'bold'), text='', foreground='black', background='white', anchor=N, padding=15, borderwidth=2, relief='ridge')
    lb_ind_cotacao_vlr_window = canvas8.create_window(800, 210, anchor='sw', window=lb_ind_cotacao_vlr, height=90, width=140)

    lb_ind_pl = ttk.Label(canvas8, font=('Helvetica', 24), text='P/L', foreground='black', background='white', anchor=N, padding=5, borderwidth=2, relief='ridge')
    lb_ind_pl_window = canvas8.create_window(980, 120, anchor='sw', window=lb_ind_pl, width=140)

    lb_ind_pl_vlr = ttk.Label(canvas8, font=('Helvetica', 29, 'bold'), text='', foreground='black', background='white', anchor=N, padding=15, borderwidth=2, relief='ridge')
    lb_ind_pl_vlr_window = canvas8.create_window(980, 210, anchor='sw', window=lb_ind_pl_vlr, height=90, width=140)

    lb_ind_pvp = ttk.Label(canvas8, font=('Helvetica', 24), text='P/VP', foreground='black', background='white', anchor=N, padding=5, borderwidth=2, relief='ridge')
    lb_ind_pvp_window = canvas8.create_window(1160, 120, anchor='sw', window=lb_ind_pvp, width=140)

    lb_ind_pvp_vlr = ttk.Label(canvas8, font=('Helvetica', 29, 'bold'), text='', foreground='black', background='white', anchor=N, padding=15, borderwidth=2, relief='ridge')
    lb_ind_pvp_vlr_window = canvas8.create_window(1160, 210, anchor='sw', window=lb_ind_pvp_vlr, height=90, width=140)

    lb_ind_dy = ttk.Label(canvas8, font=('Helvetica', 24), text='DY', foreground='black', background='white', anchor=N, padding=5, borderwidth=2, relief='ridge')
    lb_ind_dy_window = canvas8.create_window(1340, 120, anchor='sw', window=lb_ind_dy, width=140)

    lb_ind_dy_vlr = ttk.Label(canvas8, font=('Helvetica', 29, 'bold'), text='', foreground='black', background='white', anchor=N, padding=15, borderwidth=2, relief='ridge')
    lb_ind_dy_vlr_window = canvas8.create_window(1340, 210, anchor='sw', window=lb_ind_dy_vlr, height=90, width=140)

    lb_sob_emp = ttk.Label(canvas8, font=('Helvetica', 20), text='Sobre a Empresa', foreground='black', background='#1E90FF', anchor=N, padding=3, borderwidth=2, relief='ridge')
    lb_sob_emp_window = canvas8.create_window(150, 350, anchor='sw', window=lb_sob_emp, width=280)

    inp_txt_emp = Text(canvas8, width=90, font=('Roboto', 16), wrap="word", height=10, foreground='black', background='white', borderwidth=2, relief='ridge', spacing1=3)
    inp_txt_emp.delete("1.0", "end")
    inp_txt_emp.insert("1.0", "")
    inp_txt_emp_window = canvas8.create_window(150, 630, anchor='sw', window=inp_txt_emp, width=1250, height=280)

    bt_empresa = ttk.Button = Button(canvas8, font=('Roboto', 25, 'bold'), text='EMPRESA', foreground='black', background='#171F3D', anchor=N, borderwidth=2, relief='ridge')
    canvas8.create_window(300, 750, anchor='sw', window=bt_empresa, width=310, height=60)

    bt_definicao = ttk.Button = Button(canvas8, font=('Roboto', 25, 'bold'), text='DEFINIÇÃO', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas8.create_window(610, 750, anchor='sw', window=bt_definicao, width=310, height=60)

    bt_lancamentos = ttk.Button = Button(canvas8, font=('Roboto', 25, 'bold'), text='LANÇAMENTOS', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas8.create_window(920, 750, anchor='sw', window=bt_lancamentos, width=310, height=60)

    bt_def_posicao = ttk.Button = Button(canvas8, font=('Roboto', 20), text='Posição', foreground='black', background='#171F3D', anchor=N, borderwidth=2, relief='ridge')
    bt_def_posicao_window = canvas8.create_window(200, 260, anchor='sw', window=bt_def_posicao, width=300, height=50)

    bt_def_indicador = ttk.Button = Button(canvas8, font=('Roboto', 20), text='Indicadores', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    bt_def_indicador_window = canvas8.create_window(500, 260, anchor='sw', window=bt_def_indicador, width=300, height=50)

    bt_def_risco = ttk.Button = Button(canvas8, font=('Roboto', 20), text='Risco', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    bt_def_risco_window = canvas8.create_window(800, 260, anchor='sw', window=bt_def_risco, width=300, height=50)

    bt_def_notas = ttk.Button = Button(canvas8, font=('Roboto', 20), text='Notas', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    bt_def_notas_window = canvas8.create_window(1100, 260, anchor='sw', window=bt_def_notas, width=300, height=50)

    style = ttk.Style()
    style.configure("My.TFrame", background="#B0E0E6")

    frame_def = ttk.Frame(canvas8, relief="solid", borderwidth=2, style="My.TFrame")
    frame_def_window = canvas8.create_window(200, 630, anchor='sw', window=frame_def, width=1200, height=370)

    lb_def_valor_atu_vlr = ttk.Label(canvas8, font=('Roboto', 33, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_valor_atu_vlr_window = canvas8.create_window(260, 360, anchor='sw', window=lb_def_valor_atu_vlr, width=160)

    lb_def_valor_atu = ttk.Label(canvas8, font=('Helvetica', 15), text='Valor Atual', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_valor_atu_window = canvas8.create_window(260, 380, anchor='sw', window=lb_def_valor_atu, width=160)

    lb_def_valor_inv_vlr = ttk.Label(canvas8, font=('Roboto', 29, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_valor_inv_vlr_window = canvas8.create_window(500, 360, anchor='sw', window=lb_def_valor_inv_vlr, width=160)

    lb_def_valor_inv = ttk.Label(canvas8, font=('Helvetica', 13), text='Valor Investido', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_valor_inv_window = canvas8.create_window(500, 380, anchor='sw', window=lb_def_valor_inv, width=160)

    lb_def_rentab_vlr = ttk.Label(canvas8, font=('Roboto', 29, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_rentab_vlr_window = canvas8.create_window(740, 360, anchor='sw', window=lb_def_rentab_vlr, width=160)

    lb_def_rentab = ttk.Label(canvas8, font=('Helvetica', 13), text='Rentabilidade', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_rentab_window = canvas8.create_window(740, 380, anchor='sw', window=lb_def_rentab, width=160)

    lb_def_medio_vlr = ttk.Label(canvas8, font=('Roboto', 29, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_medio_vlr_window = canvas8.create_window(980, 360, anchor='sw', window=lb_def_medio_vlr, width=160)

    lb_def_medio = ttk.Label(canvas8, font=('Helvetica', 13), text='Preço Médio', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_medio_window = canvas8.create_window(980, 380, anchor='sw', window=lb_def_medio, width=160)

    lb_def_papeis_vlr = ttk.Label(canvas8, font=('Roboto', 29, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_papeis_vlr_window = canvas8.create_window(1220, 360, anchor='sw', window=lb_def_papeis_vlr, width=160)

    lb_def_papeis = ttk.Label(canvas8, font=('Helvetica', 13), text='Papeis Totais', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_papeis_window = canvas8.create_window(1220, 380, anchor='sw', window=lb_def_papeis, width=160)

    lst_meses = ['', '', '', '', '']
    lst_valores = [0, 0, 0, 0, 0]

    figure = plt.Figure(figsize=(8, 2))
    figure.set_facecolor('#B0E0E6')
    ax = figure.add_subplot(111)

    ax.bar(lst_meses, lst_valores)

    ax.set_xlabel('Meses')
    ax.set_ylabel('Valores')
    ax.set_title('Aportes', color="#171F3D", fontweight='bold')

    chart = FigureCanvasTkAgg(figure, master=canvas8)
    def_chart = chart.get_tk_widget()
    def_chart_window = canvas8.create_window(400, 610, anchor='sw', window=def_chart)

    set_tela_definicao('hidden')
    set_tela_definicao_pos("hidden")

    lb_def_pl_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pl_vlr_window = canvas8.create_window(240, 360, anchor='sw', window=lb_def_pl_vlr, width=210)

    lb_def_pl = ttk.Label(canvas8, font=('Helvetica', 15), text='P/L', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pl_window = canvas8.create_window(240, 385, anchor='sw', window=lb_def_pl, width=210)

    lb_def_pvp_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pvp_vlr_window = canvas8.create_window(540, 360, anchor='sw', window=lb_def_pvp_vlr, width=210)

    lb_def_pvp = ttk.Label(canvas8, font=('Helvetica', 15), text='P/VP', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pvp_window = canvas8.create_window(540, 385, anchor='sw', window=lb_def_pvp, width=210)

    lb_def_dy_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_dy_vlr_window = canvas8.create_window(840, 360, anchor='sw', window=lb_def_dy_vlr, width=210)

    lb_def_dy = ttk.Label(canvas8, font=('Helvetica', 15), text='DY (%)', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_dy_window = canvas8.create_window(840, 385, anchor='sw', window=lb_def_dy, width=210)

    lb_def_pay_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pay_vlr_window = canvas8.create_window(1140, 360, anchor='sw', window=lb_def_pay_vlr, width=210)

    lb_def_pay = ttk.Label(canvas8, font=('Helvetica', 15), text='Payout (%)', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_pay_window = canvas8.create_window(1140, 385, anchor='sw', window=lb_def_pay, width=210)

    lb_def_mar_bt_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_mar_bt_vlr_window = canvas8.create_window(240, 560, anchor='sw', window=lb_def_mar_bt_vlr, width=210)

    lb_def_mar_bt = ttk.Label(canvas8, font=('Helvetica', 15), text='Margem Bruta (%)', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_mar_bt_window = canvas8.create_window(240, 585, anchor='sw', window=lb_def_mar_bt, width=210)

    lb_def_mar_liq_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_mar_liq_vlr_window = canvas8.create_window(540, 560, anchor='sw', window=lb_def_mar_liq_vlr, width=210)

    lb_def_mar_liq = ttk.Label(canvas8, font=('Helvetica', 15), text='Margem Líquida (%)', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_mar_liq_window = canvas8.create_window(540, 585, anchor='sw', window=lb_def_mar_liq, width=210)

    lb_def_roe_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_roe_vlr_window = canvas8.create_window(840, 560, anchor='sw', window=lb_def_roe_vlr, width=210)

    lb_def_roe = ttk.Label(canvas8, font=('Helvetica', 15), text='ROE (%)', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_roe_window = canvas8.create_window(840, 585, anchor='sw', window=lb_def_roe, width=210)

    lb_def_divida_vlr = ttk.Label(canvas8, font=('Roboto', 38, 'bold'), text='', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_divida_vlr_window = canvas8.create_window(1140, 560, anchor='sw', window=lb_def_divida_vlr, width=210)

    lb_def_divida = ttk.Label(canvas8, font=('Helvetica', 15), text='Dívida Bruta/Patrimônio', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_divida_window = canvas8.create_window(1140, 585, anchor='sw', window=lb_def_divida, width=210)

    set_tela_definicao_ind("hidden")

    v2 = DoubleVar(value=0.0)

    style = ttk.Style()
    style.configure("Custom.Horizontal.TScale", sliderlength=1300, sliderthickness=800, troughcolor="#171F3D", borderwidth=2, relief="raised")

    def on_scale_change(value):
        lb_def_risco_vlr = ttk.Label(canvas8, font=('Helvetica', 25, 'bold'), text=int(float(value)), foreground='#006400' if float(value) < 4.0 else '#32CD32' if float(value) < 6.0 else '#DAA520' if float(value) < 9.0 else 'red', anchor=N, background="#B0E0E6")
        canvas8.itemconfigure(lb_def_risco_vlr_window, window=lb_def_risco_vlr)

    def_inp_risco = ttk.Scale(canvas8, variable=v2, from_=0, to=10, orient=HORIZONTAL, style='Custom.Horizontal.TScale', command=on_scale_change)
    def_inp_risco_window = canvas8.create_window(500, 420, anchor='sw', window=def_inp_risco, width=600, height=100)

    lb_def_risco = ttk.Label(canvas8, font=('Helvetica', 22), text='Risco: ', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_risco_window = canvas8.create_window(680, 530, anchor='sw', window=lb_def_risco, width=210)

    lb_def_risco_vlr = ttk.Label(canvas8, font=('Helvetica', 25, 'bold'), text="", foreground=None, anchor=N, background="#B0E0E6")
    lb_def_risco_vlr_window = canvas8.create_window(830, 530, anchor='sw', window=lb_def_risco_vlr, width=50)

    set_tela_definicao_risco('hidden')

    inp_txt_notas = Text(canvas8, width=90, font=('Roboto', 14), wrap="word", height=10, foreground='black', background='white', borderwidth=2, relief='ridge', spacing1=3)
    inp_txt_notas.delete("1.0", "end")
    inp_txt_notas_window = canvas8.create_window(225, 610, anchor='sw', window=inp_txt_notas, width=1150, height=340)

    set_tela_definicao_notas('hidden')

    table_lanc = ttk.Treeview(canvas8, columns=('Valor', 'Quantidade', 'Fonte'))

    table_lanc.heading('#0', text='Data')
    table_lanc.heading('Valor', text='Valor Ação')
    table_lanc.heading('Quantidade', text='Quantidade')
    table_lanc.heading('Fonte', text='Fonte')

    table_lanc.column("#0", width=180)
    table_lanc.column("Valor", width=130)
    table_lanc.column("Quantidade", width=130)
    table_lanc.column("Fonte", width=90)

    table_lanc.configure(padding=10)

    table_lanc_window = canvas8.create_window(160, 630, anchor='sw', window=table_lanc, width=1200, height=450)

    table_lanc.bind("<Double-1>", edit_lanc)

    frame_lanc = ttk.Frame(canvas8, relief="solid", borderwidth=2, style="My.TFrame")
    frame_lanc_window = canvas8.create_window(400, 500, anchor='sw', window=frame_lanc, width=700, height=100)

    inp_lanc_data = ttk.Entry(canvas8, font=('Helvetica', 12))
    inp_lanc_data_window = canvas8.create_window(410, 480, anchor='sw', window=inp_lanc_data, width=140, height=55)

    inp_lanc_valor = ttk.Entry(canvas8, font=('Helvetica', 12))
    inp_lanc_valor_window = canvas8.create_window(570, 480, anchor='sw', window=inp_lanc_valor, width=120, height=55)

    inp_lanc_quant = ttk.Entry(canvas8, font=('Helvetica', 12))
    inp_lanc_quant_window = canvas8.create_window(710, 480, anchor='sw', window=inp_lanc_quant, width=145, height=55)

    diretorio_img_save = os.path.join(diretorio_base, 'img/widgets/save_arquivo.png')
    img_save = PhotoImage(file=diretorio_img_save)

    bt_save_lanc = ttk.Button = Button(canvas8, relief="solid", image=img_save, command=salva_lanc)
    bt_save_lanc_window = canvas8.create_window(880, 480, anchor='sw', window=bt_save_lanc, width=90, height=70)

    diretorio_img_del = os.path.join(diretorio_base, 'img/widgets/del_arquivo.png')
    img_del = PhotoImage(file=diretorio_img_del)

    bt_del_lanc = ttk.Button = Button(canvas8, relief="solid", image=img_del, command=del_lanc)
    bt_del_lanc_window = canvas8.create_window(980, 480, anchor='sw', window=bt_del_lanc, width=90, height=70)

    bt_lanc_close = ttk.Button = Button(canvas8, font=('Helvetica', 11, 'bold'), text='Fechar', foreground='black', background='red', anchor=N, borderwidth=2, relief='ridge')
    bt_lanc_close_window = canvas8.create_window(690, 520, anchor='sw', window=bt_lanc_close, width=100)

    set_tela_lancamentos('hidden')
    set_tela_lancamentos_edit('hidden')

    bt_Voltar = ttk.Button = Button(canvas8, relief="solid", command=go_menuanterior7, image=img_voltar)
    bt_Voltar_window = canvas8.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    bt_empresa.bind("<Button-1>", muda_cor_botao)
    bt_definicao.bind("<Button-1>", muda_cor_botao)
    bt_lancamentos.bind("<Button-1>", muda_cor_botao)

    bt_def_posicao.bind("<Button-1>", muda_cor_def_botao)
    bt_def_indicador.bind("<Button-1>", muda_cor_def_botao)
    bt_def_risco.bind("<Button-1>", muda_cor_def_botao)
    bt_def_notas.bind("<Button-1>", muda_cor_def_botao)

    bt_lanc_close.bind("<Button-1>", fecha_frame)


    # -------------------------------------- TELA 9 (Gráficos) -------------------------------------- #

    def go_menuanterior8():
        canvas9.pack_forget()
        canvas1.pack()


    def carrega_graf_aportes():

        cur.execute(SQL_GRAF_APORTES)

        dados_tabela = cur.fetchall()

        lst_graf_meses = []
        lst_graf_valores = []

        for i in range(0, len(dados_tabela)):
            lst_graf_meses.append(dados_tabela[i][0])
            lst_graf_valores.append(dados_tabela[i][1])

        graf_ax.clear()

        graf_ax.axis('auto')

        graf_ax.bar(lst_graf_meses, lst_graf_valores, align='center')

        graf_ax.plot(lst_graf_meses, lst_graf_valores, marker='o', color='#171F3D')

        graf_ax.set_xlabel('Meses', color="#171F3D", fontweight='bold')
        graf_ax.set_ylabel('Valores', color="#171F3D", fontweight='bold')
        graf_ax.set_title('Aportes ao longo do tempo', color="#171F3D", fontweight='bold', fontsize=20)

        graf_chart.draw()


    def carrega_graf_psetor():

        cur.execute(SQL_GRAF_PSETOR)

        dados_tabela = cur.fetchall()

        lst_graf_setores = []
        lst_graf_valores = []

        for i in range(0, len(dados_tabela)):
            lst_graf_setores.append(dados_tabela[i][0])
            lst_graf_valores.append(dados_tabela[i][1])

        graf_ax.clear()

        wedges, texts, autotexts = graf_ax.pie(lst_graf_valores, pctdistance=0.85, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'grey'})

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        graf_figure.gca().add_artist(centre_circle)

        pcts = []

        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_color('#171F3D')
            pcts.append(autotext.get_text())

        for i in range(0, len(lst_graf_setores)):
            lst_graf_setores[i] = lst_graf_setores[i] + " (" + pcts[i] + ")"

        graf_ax.legend(wedges, lst_graf_setores, title="Setores", loc="center left", bbox_to_anchor=(0.8, 0.5))

        graf_ax.axis('equal')

        graf_chart.draw()


    def carrega_graf_allativos():

        cur.execute(SQL_GRAF_ALLATIVOS)

        dados_tabela = cur.fetchall()

        lst_graf_ativo = []
        lst_graf_valores = []

        for i in range(0, len(dados_tabela)):
            lst_graf_ativo.append(dados_tabela[i][0])
            lst_graf_valores.append(dados_tabela[i][1])

        graf_ax.clear()

        wedges, texts, autotexts = graf_ax.pie(lst_graf_valores, labels=lst_graf_ativo, rotatelabels=True, autopct='%1.1f%%', startangle=90, wedgeprops={'edgecolor': 'white'})

        pcts = []

        for autotext in autotexts:
            pcts.append(autotext.get_text())
            autotext.remove()

        for i in range(0, len(lst_graf_ativo)):
            lst_graf_ativo[i] = lst_graf_ativo[i] + " (" + pcts[i] + ")"

        graf_ax.legend(wedges, lst_graf_ativo, title="Ativos", loc="center left", bbox_to_anchor=(0.9, 0.5))

        graf_ax.axis('equal')

        graf_chart.draw()


    def troca_graf(event):
        bt_clicado = event.widget
        bt_clicado.configure(background='#171F3D')

        texto_botao_clicado = bt_clicado.cget("text")
        if texto_botao_clicado == "APORTES":
            bt_graf_psetor.configure(background='#1E90FF')
            bt_graf_allativos.configure(background='#1E90FF')

            carrega_graf_aportes()

        elif texto_botao_clicado == "POR SETOR":
            bt_graf_aportes.configure(background='#1E90FF')
            bt_graf_allativos.configure(background='#1E90FF')

            carrega_graf_psetor()

        elif texto_botao_clicado == "TODOS OS ATIVOS":
            bt_graf_aportes.configure(background='#1E90FF')
            bt_graf_psetor.configure(background='#1E90FF')

            carrega_graf_allativos()

    canvas9 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas9.create_image(0, 0, image=bg_image_tk_nologo, anchor='nw')

    bt_graf_aportes = ttk.Button = Button(canvas9, font=('Roboto', 25, 'bold'), text='APORTES', foreground='black', background='#171F3D', anchor=N, borderwidth=2, relief='ridge')
    canvas9.create_window(250, 760, anchor='sw', window=bt_graf_aportes, width=360, height=60)

    bt_graf_psetor = ttk.Button = Button(canvas9, font=('Roboto', 25, 'bold'), text='POR SETOR', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas9.create_window(610, 760, anchor='sw', window=bt_graf_psetor, width=360, height=60)

    bt_graf_allativos = ttk.Button = Button(canvas9, font=('Roboto', 25, 'bold'), text='TODOS OS ATIVOS', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas9.create_window(970, 760, anchor='sw', window=bt_graf_allativos, width=360, height=60)

    graf_figure = plt.Figure(figsize=(13, 6))
    graf_ax = graf_figure.add_subplot(111)

    graf_chart = FigureCanvasTkAgg(graf_figure, master=canvas9)
    graf_def_chart = graf_chart.get_tk_widget()
    graf_def_chart_window = canvas9.create_window(120, 670, anchor='sw', window=graf_def_chart)

    carrega_graf_aportes()

    bt_Voltar = ttk.Button = Button(canvas9, relief="solid", command=go_menuanterior8, image=img_voltar)
    bt_Voltar_window = canvas9.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    bt_graf_aportes.bind("<Button-1>", troca_graf)
    bt_graf_psetor.bind("<Button-1>", troca_graf)
    bt_graf_allativos.bind("<Button-1>", troca_graf)


    # -------------------------------------- TELA 10 (Comprar FIIS) -------------------------------------- #


    def go_menuanterior9():

        canvas10.pack_forget()
        canvas2.pack()


    def confirma_compra():

        if inp_nome_fii.get() == "":
            texto_erro = "Carregue as informações do fundo primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_data_fii.get() == "") or (not str(inp_data_fii.get())[0:2].isnumeric()) or (not str(inp_data_fii.get())[3:5].isnumeric()) or (not str(inp_data_fii.get())[6:11].isnumeric()):
            texto_erro = "Carregue a data da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_valor_fii.get() == "") or (not str(inp_valor_fii.get()).replace(",", "").replace(".", "").strip().isnumeric()):
            texto_erro = "Carregue as informações do valor da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_quant_fii.get() == "") or (not str(inp_quant_fii.get()).strip().isnumeric()):
            texto_erro = "Carregue as informações da quantidade da compra primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif (inp_risco_fii.get() == "") or (not str(inp_risco_fii.get())[:1].isnumeric()):
            texto_erro = "Carregue as informações referente a risco primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        elif inp_motivo_fii.get("1.0", "end-1c") == "":
            texto_erro = "Carregue as informações referente ao motivo primeiro."
            lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
            lbl_erro.show()
        else:

            cur.execute("SELECT ID FROM FII where TICKER = '" + inp_nome_fii.get().upper().strip() + "'")

            dado_id_fii = cur.fetchall()

            id_fii = dado_id_fii[0][0]

            cur.execute('insert into COMPRA(DATA, VALOR_ACAO, QUANTIDADE, UTICKER, FONTE, FID) values(?, ?, ?, ?, ?, ?)', (str(inp_data_fii.get()).strip(), float(str(inp_valor_fii.get()).replace(",", ".")), int(inp_quant_fii.get()), str(inp_nome_fii.get()).strip(), "Manual" , int(id_fii)))
            con.commit()

            cur.execute("SELECT POSICAO_ID FROM POSICAO where FID = " + str(id_fii) + "")

            dado_id_posicao = cur.fetchall()

            if len(dado_id_posicao) > 0:

                cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                            "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                            "       SUM(QUANTIDADE)" \
                            " FROM COMPRA where FID = " + str(id_fii) + " " \
                            " GROUP BY FID")

                dados_posicao = cur.fetchall()

                cur.execute('UPDATE POSICAO SET RISCO = ?, DEFINICAO = ?, VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE FID = ? AND UTICKER = ?',
                            (int(inp_risco_fii.get()), inp_motivo_fii.get("1.0", "end-1c"), dados_posicao[0][0], dados_posicao[0][1],
                             dados_posicao[0][2], id_fii, str(inp_nome_fii.get()).strip()))

                con.commit()

                texto_info = "Compra registrada com sucesso! Sua posição no fundo foi atualizada."
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()

            else:

                cur.execute('insert into POSICAO(RISCO, DEFINICAO, VALORTOTAL, PRECOMEDIO, PAPEISTOTAIS, UTICKER, FID) values(?, ?, ?, ?, ?, ?, ?)',
                            (int(inp_risco_fii.get()), inp_motivo_fii.get("1.0", "end-1c"),
                             float(str(inp_valor_fii.get()).replace(",", ".")) * int(inp_quant_fii.get()),
                             (float(str(inp_valor_fii.get()).replace(",", ".")) * int(inp_quant_fii.get())) / int(inp_quant_fii.get()),
                             int(inp_quant_fii.get()), str(inp_nome_fii.get()).strip(), id_fii))

                con.commit()

                texto_info = "Compra registrada com sucesso!"
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    def carrega_nota():

        canvas10.pack_forget()
        canvas7.pack()


    canvas10 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas10.create_image(0, 0, image=bg_image_tk, anchor='nw')

    lbl_inp_nome_fii = ttk.Label(canvas10, text='Ticker do Fundo', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_nome_fii_window = canvas10.create_window(380, 280, anchor='sw', window=lbl_inp_nome_fii, width=150)

    lbl_inp_data_fii = ttk.Label(canvas10, text='Data Investimento', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_data_fii_window = canvas10.create_window(630, 280, anchor='sw', window=lbl_inp_data_fii, width=145)

    lbl_inp_valor_fii = ttk.Label(canvas10, text='Valor do Papel', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_valor_fii_window = canvas10.create_window(880, 280, anchor='sw', window=lbl_inp_valor_fii, width=130)

    lbl_inp_quant_fii = ttk.Label(canvas10, text='Quantidade', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_quant_fii_window = canvas10.create_window(1130, 280, anchor='sw', window=lbl_inp_quant_fii, width=130)

    inp_nome_fii = ttk.Entry(canvas10, font=('Helvetica', 12))
    inp_nome_fii_window = canvas10.create_window(380, 330, anchor='sw', window=inp_nome_fii, width=150, height=40)

    inp_data_fii = ttk.Entry(canvas10, font=('Helvetica', 12))
    inp_data_fii_window = canvas10.create_window(630, 330, anchor='sw', window=inp_data_fii, width=145, height=40)

    inp_valor_fii = ttk.Entry(canvas10, font=('Helvetica', 12))
    inp_valor_fii_window = canvas10.create_window(880, 330, anchor='sw', window=inp_valor_fii, width=130, height=40)

    inp_quant_fii = ttk.Entry(canvas10, font=('Helvetica', 12))
    inp_quant_fii_window = canvas10.create_window(1130, 330, anchor='sw', window=inp_quant_fii, width=130, height=40)

    list_nomes_fii = tk.Listbox(canvas10, width=21, height=5)
    list_nomes_fii_window = canvas10.create_window(380, 410, anchor='sw', window=list_nomes_fii, width=150, height=70)

    lbl_inp_risco_fii = ttk.Label(canvas10, text='Risco Associado', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_risco_fii_window = canvas10.create_window(420, 480, anchor='sw', window=lbl_inp_risco_fii, width=170)

    lbl_inp_motivo_fii = ttk.Label(canvas10, text='Defina o por que você está investindo nesse fii...', font=('Helvetica', 13), background="#D3D3D3", padding=5, anchor='center')
    lbl_inp_motivo_fii_window = canvas10.create_window(670, 480, anchor='sw', window=lbl_inp_motivo_fii, width=590)

    v = DoubleVar()

    inp_risco_fii = ttk.Scale(canvas10, variable=v, from_=1, to=10, orient=HORIZONTAL)
    inp_risco_fii_window = canvas10.create_window(420, 530, anchor='sw', window=inp_risco_fii, width=170)

    inp_motivo_fii = Text(canvas10, width=90, font=('Helvetica', 10), height=10)
    inp_motivo_fii.delete("1.0", "end")
    inp_motivo_fii_window = canvas10.create_window(670, 580, anchor='sw', window=inp_motivo_fii, width=590, height=90)

    bt_confirma_fii = ttk.Button = Button(canvas10, font=11, text='Confirmar', relief="solid", background='#6A5ACD', command=confirma_compra)
    bt_confirma_fii_window = canvas10.create_window(660, 730, anchor='sw', window=bt_confirma_fii, width=200, height=70)

    bt_import_nota_fii = ttk.Button = Button(canvas10, font=11, text='Importar Nota', relief="solid", image=imagem_fundo, command=carrega_nota)
    bt_import_nota_fii_window = canvas10.create_window(120, 650, anchor='sw', window=bt_import_nota_fii, width=210, height=130)

    bt_Voltar = ttk.Button = Button(canvas10, relief="solid", command=go_menuanterior9, image=img_voltar)
    bt_Voltar_window = canvas10.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)


    # -------------------------------------- FINAL TELA 10 -------------------------------------- #
    # -------------------------------------- LÓGICA TELA 10 -------------------------------------- #

    def update_suggestions(event):
        list_nomes_fii.delete(0, tk.END)
        text = inp_nome_fii.get()

        for fii in dados_fii:
            if trata_str_emp(str(fii)).startswith(text.upper()):
                list_nomes_fii.insert(tk.END, trata_str_emp(fii))


    def select_fii(event):
        if len(event.widget.curselection()) > 0:
            index = event.widget.curselection()

            value = event.widget.get(index)

            inp_nome_fii.delete(0, tk.END)
            inp_nome_fii.insert(0, str(value))


    def format_date(entry):
        current_text = entry.get()

        if len(current_text) == 2 or len(current_text) == 5:
            entry.insert(tk.END, "/")


    def show_risco(event):

        txt_risco = 'Risco Associado: ' + str(int(event.widget.get()))
        lbl_inp_risco_fii.config(text=txt_risco)


    cur.execute("SELECT TICKER FROM FII order by TICKER")

    dados_fii = cur.fetchall()

    for item in dados_fii:
        list_nomes_fii.insert(tk.END, trata_str_emp(item))

    inp_nome_fii.bind('<KeyRelease>', update_suggestions)
    list_nomes_fii.bind('<Button-1>', select_fii)
    inp_data_fii.bind("<KeyRelease>", lambda event: format_date(inp_data_fii))
    inp_risco_fii.bind('<Button-1>', show_risco)


    # -------------------------------------- TELA 11 (Tabela de FIIS) -------------------------------------- #

    def go_menuanterior10():

        canvas11.pack_forget()
        canvas1.pack()


    def go_tela_fii(event):

        canvas11.pack_forget()
        canvas12.pack()

        bt_definicao_fii.configure(background='#171F3D')
        bt_lancamentos_fii.configure(background='#1E90FF')
        bt_def_risco_fii.configure(background='#171F3D')
        bt_def_notas_fii.configure(background='#1E90FF')

        lb_fii_window = canvas12.create_window(140, 130, anchor='sw', window=lb_fii)

        set_tela_definicao_fii('normal')
        set_tela_definicao_risco_fii('normal')
        set_tela_definicao_notas_fii('hidden')
        set_tela_lancamentos_fii('hidden')
        set_tela_lancamentos_fii_edit('hidden')

        bt_definicao_fii.bind("<Button-1>", muda_cor_botao_fii)
        bt_lancamentos_fii.bind("<Button-1>", muda_cor_botao_fii)

        canvas12.create_image(0, 0, image=bg_image_tk_nologo, anchor='nw')

        indice = table_fii.focus()

        if indice:
            valor = table_fii.item(indice, "text")
            valores = table_fii.item(indice, "values")

            carrega_tela_def_risco_fii(valores[0])
            carrega_tela_def_definicao_fii(valores[0])
            carrega_tela_lancamentos_fii(valores[0])

            lb_fii.configure(text=valores[0] if valores[0] != "" else "")


    canvas11 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas11.create_image(0, 0, image=bg_image_tk, anchor='nw')

    table_fii = ttk.Treeview(canvas11, columns=('Ticker', 'Risco', 'Definicao', 'Valor', 'Preco', 'Papeis'))

    table_fii.heading('#0', text='Fundo')
    table_fii.heading('Ticker', text='Ticker')
    table_fii.heading('Risco', text='Risco')
    table_fii.heading('Definicao', text='Definição')
    table_fii.heading('Valor', text='Valor Total')
    table_fii.heading('Preco', text='Preço Médio')
    table_fii.heading('Papeis', text='Papeis Totais')

    cur.execute(SQL_POSICAO_FIIS)

    dados_tabela_fii = cur.fetchall()

    table_fii.column("#0", width=180)
    table_fii.column("Ticker", width=120)
    table_fii.column("Risco", width=70)
    table_fii.column("Valor", width=95)
    table_fii.column("Preco", width=105)
    table_fii.column("Papeis", width=110)

    table_fii.configure(padding=10)

    table_fii_window = canvas11.create_window(180, 700, anchor='sw', window=table_fii, width=1200, height=450)

    bt_Voltar = ttk.Button = Button(canvas11, relief="solid", command=go_menuanterior10, image=img_voltar)
    bt_Voltar_window = canvas11.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    table_fii.bind("<Double-1>", go_tela_fii)

# -------------------------------------- TELA 12 (Sobre - FII) -------------------------------------- #

    def go_menuanterior11():

        filtro = lb_fii.cget('text')

        cur.execute("SELECT COUNT(*) " \
                    " FROM COMPRA where UTICKER = '" + str(filtro) + "' ")

        quant_compras = cur.fetchall()

        if quant_compras[0][0] != 0:

            cur.execute(SQL_RISCO_EMP)

            dados_tabela = cur.fetchall()

            dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

            risco = dados_filtrados[0][1]

            risco_new = v3.get()

            cur.execute(SQL_DEFINICAO_EMP)

            dados_tabela = cur.fetchall()

            dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

            definicao = dados_filtrados[0][1]

            definicao_new = inp_txt_notas_fii.get("1.0", "end-1c")

            if (risco != risco_new) or (definicao != definicao_new):

                risco_alt = int(risco_new if (risco != risco_new) else risco)
                definicao_alt = str(definicao_new if (definicao != definicao_new) else definicao)

                result = messagebox.askyesno("Confirmação", "Salvar as Alterações?")
                if result:

                    cur.execute('UPDATE POSICAO SET RISCO = ?, DEFINICAO = ? WHERE UTICKER = ?',
                                (risco_alt, definicao_alt, str(filtro)))

                    con.commit()




        canvas12.pack_forget()
        canvas11.pack()


    def set_tela_definicao_fii(estado):

        canvas12.itemconfig(bt_def_risco_fii_window, state=estado)
        canvas12.itemconfig(bt_def_notas_fii_window, state=estado)
        canvas12.itemconfig(frame_def_fii_window, state=estado)


    def set_tela_definicao_risco_fii(estado):

        canvas12.itemconfigure(def_inp_risco_fii_window, state=estado)
        canvas12.itemconfigure(lb_def_risco_fii_window, state=estado)
        canvas12.itemconfigure(lb_def_risco_vlr_fii_window, state=estado)


    def set_tela_definicao_notas_fii(estado):

        canvas12.itemconfigure(inp_txt_notas_fii_window, state=estado)


    def set_tela_lancamentos_fii(estado):

        canvas12.itemconfigure(table_lanc_fii_window, state=estado)


    def set_tela_lancamentos_fii_edit(estado):

        canvas12.itemconfigure(frame_lanc_fii_window, state=estado)
        canvas12.itemconfigure(inp_lanc_data_fii_window, state=estado)
        canvas12.itemconfigure(inp_lanc_valor_fii_window, state=estado)
        canvas12.itemconfigure(inp_lanc_quant_fii_window, state=estado)
        canvas12.itemconfigure(bt_save_lanc_fii_window, state=estado)
        canvas12.itemconfigure(bt_del_lanc_fii_window, state=estado)
        canvas12.itemconfigure(bt_lanc_close_fii_window, state=estado)


    def carrega_lancamentos_fii(ticker):

        cur.execute(SQL_ALL_COMPRAS)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[3] == filtro]

        if table_lanc_fii.get_children():
            table_lanc_fii.delete(*table_lanc_fii.get_children())

        for l in range(0, len(dados_filtrados)):
            table_lanc_fii.insert('', 'end', text=dados_filtrados[l][0], values=(dados_filtrados[l][1], dados_filtrados[l][2], dados_filtrados[l][4]))

        for col in table_lanc_fii["columns"]:
            table_lanc_fii.column(col, anchor="center")


    def botao_desativo(event):
        pass  # Não faz nada quando o botão é clicado


    def edit_lanc(event):
        indice = table_lanc_fii.focus()

        if indice:
            valor = table_lanc_fii.item(indice, "text")
            valores = table_lanc_fii.item(indice, "values")

            inp_lanc_data_fii.delete(0, tk.END)
            inp_lanc_valor_fii.delete(0, tk.END)
            inp_lanc_quant_fii.delete(0, tk.END)

            inp_lanc_data_fii.insert(0, valor)
            inp_lanc_valor_fii.insert(0, valores[0])
            inp_lanc_quant_fii.insert(0, valores[1])

            set_tela_lancamentos_fii_edit('normal')

            bt_definicao_fii.bind("<Button-1>", botao_desativo)
            bt_lancamentos_fii.bind("<Button-1>", botao_desativo)


    def fecha_frame_fii(event):
        set_tela_lancamentos_fii_edit('hidden')

        bt_definicao_fii.bind("<Button-1>", muda_cor_botao_fii)
        bt_lancamentos_fii.bind("<Button-1>", muda_cor_botao_fii)


    def muda_cor_botao_fii(event):
        bt_clicado = event.widget
        bt_clicado.configure(background='#171F3D')

        texto_botao_clicado = bt_clicado.cget("text")
        if texto_botao_clicado == "DEFINIÇÃO":
            bt_lancamentos_fii.configure(background='#1E90FF')

            bt_def_risco_fii.configure(background='#171F3D')
            bt_def_notas_fii.configure(background='#1E90FF')

            set_tela_definicao_fii('normal')
            set_tela_definicao_risco_fii('normal')
            set_tela_definicao_notas_fii('hidden')

            set_tela_lancamentos_fii('hidden')

        elif texto_botao_clicado == "LANÇAMENTOS":
            bt_definicao_fii.configure(background='#1E90FF')

            set_tela_definicao_fii('hidden')

            style = ttk.Style()

            style.configure("Treeview", font=("Arial", 14), padding=(0, 35, 0, 35), background='#B0C4DE', rowheight=50)
            style.configure("Treeview.Heading", font=("Arial", 14, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

            table_lanc_fii.configure(style="Treeview.Heading")
            table_lanc_fii.configure(style="Treeview")

            set_tela_lancamentos_fii('normal')


    def muda_cor_def_botao_fii(event):
        bt_clicado = event.widget
        bt_clicado.configure(background='#171F3D')

        texto_botao_clicado = bt_clicado.cget("text")
        if texto_botao_clicado == "Risco":
            bt_def_notas_fii.configure(background='#1E90FF')

            set_tela_definicao_risco_fii('normal')

            set_tela_definicao_notas_fii('hidden')

        elif texto_botao_clicado == "Notas":
            bt_def_risco_fii.configure(background='#1E90FF')

            set_tela_definicao_risco_fii('hidden')

            set_tela_definicao_notas_fii('normal')


    def carrega_tela_def_risco_fii(ticker):

        cur.execute(SQL_RISCO_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        risco = dados_filtrados[0][1]

        v3.set(value=float(risco))
        lb_def_risco_vlr_fii.configure(text=v3.get(), foreground='#006400' if float(risco) < 4.0 else '#32CD32' if float(risco) < 6.0 else '#DAA520' if float(risco) < 9.0 else 'red')


    def carrega_tela_def_definicao_fii(ticker):

        cur.execute(SQL_DEFINICAO_EMP)

        dados_tabela = cur.fetchall()

        filtro = ticker
        dados_filtrados = [linha for linha in dados_tabela if linha[0] == filtro]

        definicao = dados_filtrados[0][1]

        inp_txt_notas_fii.delete("1.0", "end")
        inp_txt_notas_fii.insert("end", definicao)


    def carrega_tela_lancamentos_fii(ticker):

        carrega_lancamentos_fii(ticker)


    def salva_lanc_fii():

        ticker = lb_fii.cget('text')

        indice = table_lanc_fii.focus()

        if indice:
            valor = table_lanc_fii.item(indice, "text")
            valores = table_lanc_fii.item(indice, "values")

            data_new = inp_lanc_data_fii.get()
            valor_acao_new = inp_lanc_valor_fii.get()
            quantidade_new = inp_lanc_quant_fii.get()

            result = messagebox.askyesno("Confirmação", "Salvar as Alterações?")
            if result:

                cur.execute('UPDATE COMPRA SET DATA = ?, VALOR_ACAO = ?, QUANTIDADE = ? WHERE UTICKER = ? AND DATA = ? AND VALOR_ACAO = ? AND QUANTIDADE = ? AND FONTE = ?',
                            (data_new, float(valor_acao_new), int(quantidade_new), ticker, valor, float(valores[0]), int(valores[1]), valores[2]))

                con.commit()

                cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                            "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                            "       SUM(QUANTIDADE)" \
                            " FROM COMPRA where UTICKER = '" + str(ticker) + "' " \
                            " GROUP BY UTICKER")

                dados_posicao = cur.fetchall()

                cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE UTICKER = ?',
                            (dados_posicao[0][0], dados_posicao[0][1],
                             dados_posicao[0][2], str(ticker)))

                con.commit()

                texto_info = "Lançamento Atualizado!"
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    def del_lanc_fii():

        ticker = lb_fii.cget('text')

        indice = table_lanc_fii.focus()

        if indice:
            valor = table_lanc_fii.item(indice, "text")
            valores = table_lanc_fii.item(indice, "values")

            result = messagebox.askyesno("Confirmação", "Excluir o lançamento?")
            if result:

                cur.execute('DELETE FROM COMPRA WHERE UTICKER = ? AND DATA = ? AND VALOR_ACAO = ? AND QUANTIDADE = ? AND FONTE = ?',
                            (ticker, valor, float(valores[0]), int(valores[1]), valores[2]))

                con.commit()

                cur.execute("SELECT COUNT(*) " \
                            " FROM COMPRA where UTICKER = '" + str(ticker) + "' ")

                quant_compras = cur.fetchall()

                if quant_compras[0][0] == 0:

                    cur.execute('DELETE FROM POSICAO WHERE UTICKER = ?', (str(ticker),))

                else:

                    cur.execute("SELECT (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                                "       (SUM(VALOR_ACAO) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                                "       SUM(QUANTIDADE)" \
                                " FROM COMPRA where UTICKER = '" + str(ticker) + "' " \
                                                                                 " GROUP BY UTICKER")

                    dados_posicao = cur.fetchall()

                    cur.execute('UPDATE POSICAO SET VALORTOTAL = ?, PRECOMEDIO = ?, PAPEISTOTAIS = ? WHERE UTICKER = ?',
                                (dados_posicao[0][0], dados_posicao[0][1],
                                 dados_posicao[0][2], str(ticker)))


                con.commit()

                texto_info = "Lançamento deletado."
                lbl_info = messagebox.Message(title='Investify', message=texto_info)
                lbl_info.show()


    canvas12 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())

    lb_fii = ttk.Label(canvas12, font=('Helvetica', 40, 'bold'), text='', foreground='#171F3D', background='white', anchor=W, padding=4)
    lb_fii_window = canvas12.create_window(140, 130, anchor='sw', window=lb_fii)

    bt_definicao_fii = ttk.Button = Button(canvas12, font=('Roboto', 25, 'bold'), text='DEFINIÇÃO', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas12.create_window(510, 750, anchor='sw', window=bt_definicao_fii, width=310, height=60)

    bt_lancamentos_fii = ttk.Button = Button(canvas12, font=('Roboto', 25, 'bold'), text='LANÇAMENTOS', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    canvas12.create_window(820, 750, anchor='sw', window=bt_lancamentos_fii, width=310, height=60)

    bt_def_risco_fii = ttk.Button = Button(canvas12, font=('Roboto', 20), text='Risco', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    bt_def_risco_fii_window = canvas12.create_window(200, 260, anchor='sw', window=bt_def_risco_fii, width=600, height=50)

    bt_def_notas_fii = ttk.Button = Button(canvas12, font=('Roboto', 20), text='Notas', foreground='black', background='#1E90FF', anchor=N, borderwidth=2, relief='ridge')
    bt_def_notas_fii_window = canvas12.create_window(800, 260, anchor='sw', window=bt_def_notas_fii, width=600, height=50)

    style = ttk.Style()
    style.configure("My.TFrame", background="#B0E0E6")

    frame_def_fii = ttk.Frame(canvas12, relief="solid", borderwidth=2, style="My.TFrame")
    frame_def_fii_window = canvas12.create_window(200, 630, anchor='sw', window=frame_def_fii, width=1200, height=370)

    set_tela_definicao_fii('hidden')

    v3 = DoubleVar(value=0.0)

    style = ttk.Style()
    style.configure("Custom.Horizontal.TScale", sliderlength=1300, sliderthickness=800, troughcolor="#171F3D", borderwidth=2, relief="raised")

    def on_scale_change(value):
        lb_def_risco_vlr_fii = ttk.Label(canvas12, font=('Helvetica', 25, 'bold'), text=int(float(value)), foreground='#006400' if float(value) < 4.0 else '#32CD32' if float(value) < 6.0 else '#DAA520' if float(value) < 9.0 else 'red', anchor=N, background="#B0E0E6")
        canvas12.itemconfigure(lb_def_risco_vlr_fii_window, window=lb_def_risco_vlr_fii)

    def_inp_risco_fii = ttk.Scale(canvas12, variable=v3, from_=0, to=10, orient=HORIZONTAL, style='Custom.Horizontal.TScale', command=on_scale_change)
    def_inp_risco_fii_window = canvas12.create_window(500, 420, anchor='sw', window=def_inp_risco_fii, width=600, height=100)

    lb_def_risco_fii = ttk.Label(canvas12, font=('Helvetica', 22), text='Risco: ', foreground='black', anchor=N, background="#B0E0E6")
    lb_def_risco_fii_window = canvas12.create_window(680, 530, anchor='sw', window=lb_def_risco_fii, width=210)

    lb_def_risco_vlr_fii = ttk.Label(canvas12, font=('Helvetica', 25, 'bold'), text="", foreground=None, anchor=N, background="#B0E0E6")
    lb_def_risco_vlr_fii_window = canvas12.create_window(830, 530, anchor='sw', window=lb_def_risco_vlr_fii, width=50)

    set_tela_definicao_risco_fii('hidden')

    inp_txt_notas_fii = Text(canvas12, width=90, font=('Roboto', 14), wrap="word", height=10, foreground='black', background='white', borderwidth=2, relief='ridge', spacing1=3)
    inp_txt_notas_fii.delete("1.0", "end")
    inp_txt_notas_fii_window = canvas12.create_window(225, 610, anchor='sw', window=inp_txt_notas_fii, width=1150, height=340)

    set_tela_definicao_notas_fii('hidden')

    table_lanc_fii = ttk.Treeview(canvas12, columns=('Valor', 'Quantidade', 'Fonte'))

    table_lanc_fii.heading('#0', text='Data')
    table_lanc_fii.heading('Valor', text='Valor Ação')
    table_lanc_fii.heading('Quantidade', text='Quantidade')
    table_lanc_fii.heading('Fonte', text='Fonte')

    table_lanc_fii.column("#0", width=180)
    table_lanc_fii.column("Valor", width=130)
    table_lanc_fii.column("Quantidade", width=130)
    table_lanc_fii.column("Fonte", width=90)

    table_lanc_fii.configure(padding=10)

    table_lanc_fii_window = canvas12.create_window(160, 630, anchor='sw', window=table_lanc_fii, width=1200, height=450)

    table_lanc_fii.bind("<Double-1>", edit_lanc)

    frame_lanc_fii = ttk.Frame(canvas12, relief="solid", borderwidth=2, style="My.TFrame")
    frame_lanc_fii_window = canvas12.create_window(400, 500, anchor='sw', window=frame_lanc_fii, width=700, height=100)

    inp_lanc_data_fii = ttk.Entry(canvas12, font=('Helvetica', 12))
    inp_lanc_data_fii_window = canvas12.create_window(410, 480, anchor='sw', window=inp_lanc_data_fii, width=140, height=55)

    inp_lanc_valor_fii = ttk.Entry(canvas12, font=('Helvetica', 12))
    inp_lanc_valor_fii_window = canvas12.create_window(570, 480, anchor='sw', window=inp_lanc_valor_fii, width=120, height=55)

    inp_lanc_quant_fii = ttk.Entry(canvas12, font=('Helvetica', 12))
    inp_lanc_quant_fii_window = canvas12.create_window(710, 480, anchor='sw', window=inp_lanc_quant_fii, width=145, height=55)

    bt_save_lanc_fii = ttk.Button = Button(canvas12, relief="solid", image=img_save, command=salva_lanc_fii)
    bt_save_lanc_fii_window = canvas12.create_window(880, 480, anchor='sw', window=bt_save_lanc_fii, width=90, height=70)

    bt_del_lanc_fii = ttk.Button = Button(canvas12, relief="solid", image=img_del, command=del_lanc_fii)
    bt_del_lanc_fii_window = canvas12.create_window(980, 480, anchor='sw', window=bt_del_lanc_fii, width=90, height=70)

    bt_lanc_close_fii = ttk.Button = Button(canvas12, font=('Helvetica', 11, 'bold'), text='Fechar', foreground='black', background='red', anchor=N, borderwidth=2, relief='ridge')
    bt_lanc_close_fii_window = canvas12.create_window(690, 520, anchor='sw', window=bt_lanc_close_fii, width=100)

    set_tela_lancamentos_fii('hidden')
    set_tela_lancamentos_fii_edit('hidden')

    bt_Voltar = ttk.Button = Button(canvas12, relief="solid", command=go_menuanterior11, image=img_voltar)
    bt_Voltar_window = canvas12.create_window(80, 760, anchor='sw', window=bt_Voltar, width=90, height=70)

    bt_definicao_fii.bind("<Button-1>", muda_cor_botao_fii)
    bt_lancamentos_fii.bind("<Button-1>", muda_cor_botao_fii)

    bt_def_risco_fii.bind("<Button-1>", muda_cor_def_botao_fii)
    bt_def_notas_fii.bind("<Button-1>", muda_cor_def_botao_fii)

    bt_lanc_close_fii.bind("<Button-1>", fecha_frame_fii)


except urllib.error.URLError:
    texto_erro = "Sem conexão com a internet. Conecte para usar o app."
    lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
    lbl_erro.show()

    app.destroy()


#################
app.mainloop()

con.close()