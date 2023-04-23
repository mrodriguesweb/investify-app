import urllib
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter as tk
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3
import csv
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import datetime

# Cria a instancia do App
app = tk.Tk()
app.geometry('1400x1400')
app.title('Investify - Controle seus Investimentos')

# Carrega a imagem
bg_image = Image.open("background.png")
# Redimensiona a imagem para o tamanho da janela
bg_image = bg_image.resize((app.winfo_screenwidth(), app.winfo_screenheight()))
# Converte a imagem para o formato compatível com Tkinter
bg_image_tk = ImageTk.PhotoImage(bg_image)

con = sqlite3.connect('C:\\Users\\mrodr\\PycharmProjects\\pythonProject\\investimentos.db')

cur = con.cursor()

# -------------------------------------- TELA 1 (Menu, gráfico dos ativos) -------------------------------------- #

try:

    def openoptions():
        state = canvas1.itemcget(bt_var_window, 'state')

        if state == 'hidden':

            canvas1.itemconfigure(bt_var_window, state='normal')
            canvas1.itemconfigure(bt_fix_window, state='normal')

        else:

            canvas1.itemconfigure(bt_var_window, state='hidden')
            canvas1.itemconfigure(bt_fix_window, state='hidden')


    def go_menucompra():

        canvas1.pack_forget()
        canvas2.pack()


    def go_viewativos():

        canvas1.pack_forget()
        canvas4.pack()

        lst_cotacoes = []

        # if True, o obj treeView já foi criado, então caso algum ativo novo tenha sido criado, irá atualizar
        if table.get_children():

            emps_tbl = []

            for i in range(1, len(table.get_children()) + 1):
                item = table.item("I00" + str(i), option='text')
                emps_tbl.append(item)

            tcks_tbl = []

            for i in range(1, len(table.get_children()) + 1):
                item = table.item("I00" + str(i), option='values')[0]
                tcks_tbl.append(item)

            emps_tbl_str = ', '.join(["'{}'".format(valor) for valor in emps_tbl])
            tcks_tbl_str = ', '.join(["'{}'".format(valor) for valor in tcks_tbl])

            # Seleciona somente os ativos novos pra adicionar no treeview
            query = "SELECT b.NOME," \
                        "       b.SETOR," \
                        "       a.UTICKER," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PRECOMEDIO," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAO as a " \
                        "inner join EMPRESA as b " \
                        "on (a.ID = b.ID) WHERE (b.NOME NOT IN ({}) AND a.UTICKER NOT IN ({}))".format(emps_tbl_str, tcks_tbl_str, emps_tbl_str, tcks_tbl_str)

            cur.execute(query)

            dados_tabela = cur.fetchall()

            if len(dados_tabela) > 0:
                for l in range(0, len(dados_tabela)):

                    url = "https://www.infomoney.com.br/cotacoes/b3/acao/" + str(dados_tabela[l][0]) + "-" + str(dados_tabela[l][2]) + "/"

                    page = urlopen(url)

                    html_bytes = page.read()
                    html = html_bytes.decode("utf-8")

                    soup = BeautifulSoup(html, "html.parser")

                    busca_cotacao = list(soup.find_all("p"))

                    if len(busca_cotacao) > 0:
                        cotacao_emp = str(busca_cotacao[15]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                        if str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric() == False:
                            cotacao_emp = str(busca_cotacao[16]).replace("p", "").replace(">", "").replace("<", "").replace("/", "").replace(",", ".")

                        lst_cotacoes.append(cotacao_emp)

                        if (cotacao_emp != "") and (str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric()):

                            emp_rentabilidade = round(((float(cotacao_emp) * int(dados_tabela[l][7])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                            table.insert('', 'end', text=dados_tabela[l][0], values=(dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), dados_tabela[l][6], dados_tabela[l][7], emp_rentabilidade))

                        else:

                            table.insert('', 'end', text=dados_tabela[l][0], values=(dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), dados_tabela[l][6], dados_tabela[l][7], "-"))

        else:

            cur.execute("SELECT b.NOME," \
                        "       b.SETOR," \
                        "       a.UTICKER," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PRECOMEDIO," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAO as a " \
                        "inner join EMPRESA as b " \
                        "on (a.ID = b.ID)")

            dados_tabela = cur.fetchall()

            if len(dados_tabela) > 0:
                for l in range(0, len(dados_tabela)):

                    url = "https://www.infomoney.com.br/cotacoes/b3/acao/" + str(dados_tabela[l][0]).replace(" ", "-") + "-" + str(dados_tabela[l][2]) + "/"

                    page = urlopen(url)

                    html_bytes = page.read()
                    html = html_bytes.decode("utf-8")

                    soup = BeautifulSoup(html, "html.parser")

                    busca_cotacao = list(soup.find_all("p"))

                    if len(busca_cotacao) > 0:
                        cotacao_emp = str(busca_cotacao[15]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                        if str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric() == False:
                            cotacao_emp = str(busca_cotacao[16]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                        lst_cotacoes.append(cotacao_emp)

                        if (cotacao_emp != "") and (str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric()):

                            emp_rentabilidade = round(((float(cotacao_emp) * int(dados_tabela[l][7])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                            table.insert('', 'end', text=dados_tabela[l][0], values=(dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), dados_tabela[l][6], dados_tabela[l][7], emp_rentabilidade))

                        else:

                            table.insert('', 'end', text=dados_tabela[l][0], values=(dados_tabela[l][1], dados_tabela[l][2], dados_tabela[l][3], 'Abrir informações...', round(dados_tabela[l][5], 2), dados_tabela[l][6], dados_tabela[l][7], "-"))


    def go_viewfix():
        canvas1.pack_forget()
        canvas6.pack()

        if table_fix.get_children():

            titulos_tbl = []

            for i in range(1, len(table_fix.get_children()) + 1):
                item = table_fix.item("I00" + str(i), option='text')
                titulos_tbl.append(item)

            dtvenc_tbl = []

            for i in range(1, len(table_fix.get_children()) + 1):
                item = table_fix.item("I00" + str(i), option='values')[0]
                dtvenc_tbl.append(item)

            papeis_tbl = []

            for i in range(1, len(table_fix.get_children()) + 1):
                item = table_fix.item("I00" + str(i), option='values')[5]
                papeis_tbl.append(item)

            titulos_tbl_str = ', '.join(["'{}'".format(valor) for valor in titulos_tbl])
            dtvenc_tbl_str = ', '.join(["'{}'".format(valor) for valor in dtvenc_tbl])

            query = "SELECT b.NOME," \
                        "       b.DT_VENC," \
                        "       b.TIPO," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAOTESOURO as a " \
                        "inner join TITULO as b " \
                        "on (a.TIT_ID = b.TIT_ID) WHERE (b.NOME NOT IN ({}) OR b.DT_VENC NOT IN ({})) OR (b.NOME NOT IN ({}) AND b.DT_VENC NOT IN ({}))".format(titulos_tbl_str, dtvenc_tbl_str, titulos_tbl_str, dtvenc_tbl_str)

            cur.execute(query)

            dados_tabela_tit = cur.fetchall()

            if len(dados_tabela_tit) > 0:
                for l in range(0, len(dados_tabela_tit)):

                    cur.execute("SELECT VALOR_TIT FROM TEMPTITULOS WHERE UPPER(NOME) = '" + dados_tabela_tit[l][0] + "' and DT_VENC = '" + dados_tabela_tit[l][1] + "'")

                    busca_cotacao = cur.fetchall()

                    cotacao_tit = busca_cotacao[0][0] / 100

                    if (cotacao_tit != "") and (str(cotacao_tit).replace(",", "").replace(".", "").strip().isnumeric()):
                        tit_rentabilidade = round(((float(cotacao_tit) * int(dados_tabela_tit[l][6])) - float(dados_tabela_tit[l][5])) / float(dados_tabela_tit[l][5]) * 100, 2)

                        table_fix.insert('', 'end', text=dados_tabela_tit[l][0], values=(dados_tabela_tit[l][1], dados_tabela_tit[l][2], dados_tabela_tit[l][3], 'Abrir informações...', round(dados_tabela_tit[l][5], 2), dados_tabela_tit[l][6], tit_rentabilidade))

        else:

            cur.execute("SELECT b.NOME," \
                        "       b.DT_VENC," \
                        "       b.TIPO," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAOTESOURO as a " \
                        "inner join TITULO as b " \
                        "on (a.TIT_ID = b.TIT_ID)")

            dados_tabela_tit = cur.fetchall()

            if len(dados_tabela_tit) > 0:
                for l in range(0, len(dados_tabela_tit)):

                    cur.execute("SELECT VALOR_TIT FROM TEMPTITULOS WHERE UPPER(NOME) = '" + dados_tabela_tit[l][0] + "' and DT_VENC = '" + dados_tabela_tit[l][1] + "'")

                    busca_cotacao = cur.fetchall()

                    cotacao_tit = busca_cotacao[0][0] / 100

                    if (cotacao_tit != "") and (str(cotacao_tit).replace(",", "").replace(".", "").strip().isnumeric()):
                        tit_rentabilidade = round(((float(cotacao_tit) * int(dados_tabela_tit[l][6])) - float(dados_tabela_tit[l][5])) / float(dados_tabela_tit[l][5]) * 100, 2)

                        table_fix.insert('', 'end', text=dados_tabela_tit[l][0], values=(dados_tabela_tit[l][1], dados_tabela_tit[l][2], dados_tabela_tit[l][3], 'Abrir informações...', round(dados_tabela_tit[l][5], 2), dados_tabela_tit[l][6], tit_rentabilidade))


    def show_grafvar():

        cur.execute("SELECT * FROM POSICAO")

        dado_pos = cur.fetchall()

        cur.execute("SELECT B.NOME, A.VALORTOTAL FROM POSICAO AS A INNER JOIN EMPRESA AS B ON (A.ID = B.ID) ORDER BY A.VALORTOTAL")

        if len(dado_pos) > 0:
            dados_renda_var = cur.fetchall()
        else:
            dados_renda_var = ((0,), (0,))

        lst_valores = []
        lst_empresas = []

        for i in dados_renda_var:
            lst_valores.append(float(i[1]))
            lst_empresas.append(str(i[0]))

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(lst_valores, labels=lst_empresas)
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid', bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16, text='Valor Total: R$ ' + str(round(sum(tuple(lst_valores)), 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        cur.execute("SELECT b.NOME," \
                    "       b.SETOR," \
                    "       a.UTICKER," \
                    "       a.RISCO," \
                    "       a.DEFINICAO," \
                    "       a.VALORTOTAL," \
                    "       a.PRECOMEDIO," \
                    "       a.PAPEISTOTAIS " \
                    "from POSICAO as a " \
                    "inner join EMPRESA as b " \
                    "on (a.ID = b.ID)")

        dados_tabela = cur.fetchall()

        valor_total = 0
        lst_rent_emp = []

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                url = "https://www.infomoney.com.br/cotacoes/b3/acao/" + str(dados_tabela[l][0]).replace(" ", "-") + "-" + str(dados_tabela[l][2]) + "/"

                page = urlopen(url)

                html_bytes = page.read()
                html = html_bytes.decode("utf-8")

                soup = BeautifulSoup(html, "html.parser")

                busca_cotacao = list(soup.find_all("p"))

                if len(busca_cotacao) > 0:
                    cotacao_emp = str(busca_cotacao[15]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                    if str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric() == False:
                        cotacao_emp = str(busca_cotacao[16]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                    if (cotacao_emp != "") and (str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric()):

                        emp_rentabilidade = round(((float(cotacao_emp) * int(dados_tabela[l][7])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                        lst_rent_emp.append(emp_rentabilidade * float(dados_tabela[l][5]))
                        valor_total += float(dados_tabela[l][5])
                    else:
                        lst_rent_emp.append(0)

            rent_carteira = 0
            for emp in lst_rent_emp:
                rent_carteira += emp

        cart_rentabilidade = (rent_carteira / valor_total) * 1

        lb_rentabilidade = ttk.Label(canvas1, font=15,text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


    def show_graffix():
        cur.execute("SELECT * FROM POSICAOTESOURO")

        dado_pos = cur.fetchall()

        cur.execute("SELECT B.NOME, B.DT_VENC, A.VALORTOTAL FROM POSICAOTESOURO AS A INNER JOIN TITULO AS B ON (A.TIT_ID = B.TIT_ID) ORDER BY A.VALORTOTAL")

        if len(dado_pos) > 0:
            dados_renda_fix = cur.fetchall()
        else:
            dados_renda_fix = ((0,), (0,))

        lst_valores_tit = []
        lst_titulos = []

        for i in dados_renda_fix:
            lst_valores_tit.append(float(i[2]))
            lst_titulos.append(str(i[0] + " " + i[1][-4:]).replace("TESOURO", "").replace("COM JUROS SEMESTRAIS", "C/ JUROS"))

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(lst_valores_tit, labels=lst_titulos)
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid', bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16, text='Valor Total: R$ ' + str(round(sum(tuple(lst_valores_tit)), 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        cur.execute("SELECT b.NOME," \
                    "       b.DT_VENC," \
                    "       b.TIPO," \
                    "       a.RISCO," \
                    "       a.DEFINICAO," \
                    "       a.VALORTOTAL," \
                    "       a.PAPEISTOTAIS " \
                    "from POSICAOTESOURO as a " \
                    "inner join TITULO as b " \
                    "on (a.TIT_ID = b.TIT_ID)")

        dados_tabela = cur.fetchall()

        valor_total = 0
        lst_rent_tit = []

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                cur.execute("SELECT VALOR_TIT FROM TEMPTITULOS WHERE UPPER(NOME) = '" + dados_tabela[l][0] + "' and DT_VENC = '" + dados_tabela[l][1] + "'")

                busca_cotacao = cur.fetchall()

                cotacao_tit = busca_cotacao[0][0] / 100

                if (cotacao_tit != "") and (str(cotacao_tit).replace(",", "").replace(".", "").strip().isnumeric()):

                    tit_rentabilidade = round(((float(cotacao_tit) * int(dados_tabela[l][6])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                    lst_rent_tit.append(tit_rentabilidade * float(dados_tabela[l][5]))
                    valor_total += float(dados_tabela[l][5])
                else:
                    lst_rent_tit.append(0)

        rent_carteira = 0
        for tit in lst_rent_tit:
            rent_carteira += tit

        cart_rentabilidade = (rent_carteira / valor_total) * 1

        lb_rentabilidade = ttk.Label(canvas1, font=15, text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


    def show_graf():
        cur.execute("SELECT * FROM POSICAO")

        dado_pos = cur.fetchall()

        cur.execute("SELECT SUM(VALORTOTAL) FROM POSICAO")

        if len(dado_pos) > 0:
            dados_renda_var = cur.fetchall()
        else:
            dados_renda_var = ((0,), (0,))

        cur.execute("SELECT * FROM POSICAOTESOURO")

        dado_pos_tit = cur.fetchall()

        cur.execute("SELECT SUM(VALORTOTAL) FROM POSICAOTESOURO")

        if len(dado_pos_tit) > 0:
            dados_renda_fix = cur.fetchall()
        else:
            dados_renda_fix = ((0,), (0,))

        dados = [dados_renda_var[0][0], dados_renda_fix[0][0]]

        ctl_graphs_fix = tk.IntVar()
        ctl_graphs_fix.set(0)

        figure = plt.Figure(figsize=(4, 3))
        figure.set_facecolor('#1E90FF')
        ax = figure.add_subplot(111)

        ax.pie(dados, labels=['Renda Variável', 'Renda Fixa'])
        chart = FigureCanvasTkAgg(figure, canvas1)
        chart_window = canvas1.create_window(900, 500, anchor='sw', window=chart.get_tk_widget(), width=434)

        style_border = ttk.Style()
        style_border.configure("BW.TLabel", foreground="black", background="#1E90FF", borderwidth=10, relief='solid',bordercolor='#3419E6', padding=4)

        lb_vlr_total = ttk.Label(canvas1, font=16,text='Valor Total: R$ ' + str(round(dados_renda_var[0][0] + dados_renda_fix[0][0], 2)), anchor=CENTER, style='BW.TLabel')
        lb_vlr_total_window = canvas1.create_window(900, 600, anchor='sw', window=lb_vlr_total, width=434)

        cur.execute("SELECT b.NOME," \
                    "       b.SETOR," \
                    "       a.UTICKER," \
                    "       a.RISCO," \
                    "       a.DEFINICAO," \
                    "       a.VALORTOTAL," \
                    "       a.PRECOMEDIO," \
                    "       a.PAPEISTOTAIS " \
                    "from POSICAO as a " \
                    "inner join EMPRESA as b " \
                    "on (a.ID = b.ID)")

        dados_tabela = cur.fetchall()

        valor_total = 0
        lst_rent_emp = []
        lst_rent_tit = []

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                url = "https://www.infomoney.com.br/cotacoes/b3/acao/" + str(dados_tabela[l][0]).replace(" ","-") + "-" + str(dados_tabela[l][2]) + "/"

                page = urlopen(url)

                html_bytes = page.read()
                html = html_bytes.decode("utf-8")

                soup = BeautifulSoup(html, "html.parser")

                busca_cotacao = list(soup.find_all("p"))

                if len(busca_cotacao) > 0:
                    cotacao_emp = str(busca_cotacao[15]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                    if str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric() == False:
                        cotacao_emp = str(busca_cotacao[16]).replace("p", "").replace(">", "").replace("<", "").replace("/","").replace(",", ".")

                    if (cotacao_emp != "") and (str(cotacao_emp).replace(",", "").replace(".", "").strip().isnumeric()):

                        emp_rentabilidade = round(((float(cotacao_emp) * int(dados_tabela[l][7])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                        lst_rent_emp.append(emp_rentabilidade * float(dados_tabela[l][5]))
                        valor_total += float(dados_tabela[l][5])
                    else:
                        lst_rent_emp.append(0)

            rent_carteira = 0
            for emp in lst_rent_emp:
                rent_carteira += emp

            cur.execute("SELECT b.NOME," \
                        "       b.DT_VENC," \
                        "       b.TIPO," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAOTESOURO as a " \
                        "inner join TITULO as b " \
                        "on (a.TIT_ID = b.TIT_ID)")

            dados_tabela = cur.fetchall()

        if len(dados_tabela) > 0:
            for l in range(0, len(dados_tabela)):

                cur.execute(
                    "SELECT VALOR_TIT FROM TEMPTITULOS WHERE UPPER(NOME) = '" + dados_tabela[l][0] + "' and DT_VENC = '" +
                    dados_tabela[l][1] + "'")

                busca_cotacao = cur.fetchall()

                cotacao_tit = busca_cotacao[0][0] / 100

                if (cotacao_tit != "") and (str(cotacao_tit).replace(",", "").replace(".", "").strip().isnumeric()):

                    tit_rentabilidade = round(((float(cotacao_tit) * int(dados_tabela[l][6])) - float(dados_tabela[l][5])) / float(dados_tabela[l][5]) * 100, 2)

                    lst_rent_tit.append(tit_rentabilidade * float(dados_tabela[l][5]))
                    valor_total += float(dados_tabela[l][5])
                else:
                    lst_rent_tit.append(0)

        for tit in lst_rent_tit:
            rent_carteira += tit

        cart_rentabilidade = (rent_carteira / valor_total) * 1

        lb_rentabilidade = ttk.Label(canvas1, font=15,text='Rentabilidade Total: ' + str(round(cart_rentabilidade, 2)) + '%', anchor=CENTER, style='BW.TLabel')
        lb_rentabilidade_window = canvas1.create_window(900, 650, anchor='sw', window=lb_rentabilidade, width=434)


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

    bt_var = ttk.Button = Button(canvas1, font=15, background='#1E90FF', text='Renda Variável', width=35, command=go_viewativos)
    bt_var_window = canvas1.create_window(100, 550, anchor='sw', window=bt_var)
    canvas1.itemconfigure(bt_var_window, state='hidden')

    bt_fix = ttk.Button = Button(canvas1, font=15, background='#1E90FF', text='Renda Fixa', width=35, command=go_viewfix)
    bt_fix_window = canvas1.create_window(100, 600, anchor='sw', window=bt_fix)
    canvas1.itemconfigure(bt_fix_window, state='hidden')

    state = canvas1.itemcget(bt_var_window, 'state')

    bt_ativos = ttk.Button = Button(canvas1, command=openoptions, font=15, background='#6A5ACD', width=35, text='Meus Ativos')
    bt_ativos_window = canvas1.create_window(100, 500, anchor='sw', window=bt_ativos)

    bt_Cadastro = ttk.Button = Button(canvas1, font=18, background='#6A5ACD', width=40, text='Cadastrar Compra', height=2, command=go_menucompra)
    bt_Cadastro_window = canvas1.create_window(100, 700, anchor='sw', window=bt_Cadastro)

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

    def go_menuanterior1():

        show_graf()

        canvas2.pack_forget()
        canvas1.pack()


    canvas2 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas2.create_image(0, 0, image=bg_image_tk, anchor='nw')

    lb_question = ttk.Label(canvas2, font=('Helvetica', 18, 'bold'),text='Antes de informar sua compra, nos informe qual o tipo de ativo...', foreground='#171F3D', anchor=CENTER, background="#1E90FF", padding=4)
    lb_question_window = canvas2.create_window(400, 300, anchor='sw', window=lb_question, width=780)

    bt_sel_acao = ttk.Button = Button(canvas2, font=15, width=10, text='Ações', relief="solid", command=go_frm_compra_acao, foreground="#171F3D")
    bt_sel_acao_window = canvas2.create_window(580, 400, anchor='sw', window=bt_sel_acao, width=400)

    bt_sel_fii = ttk.Button = Button(canvas2, font=15, width=10, text='FIIS', relief="solid", foreground="#171F3D")
    bt_sel_fii_window = canvas2.create_window(580, 480, anchor='sw', window=bt_sel_fii, width=400)

    bt_sel_fixa = ttk.Button = Button(canvas2, font=15, width=10, text='Renda Fixa', relief="solid", command=go_frm_compra_fix, foreground="#171F3D")
    bt_sel_fixa_window = canvas2.create_window(580, 560, anchor='sw', window=bt_sel_fixa, width=400)

    bt_Voltar = ttk.Button = Button(canvas2, font=18, background='#6A5ACD', width=30, text='Voltar', height=2, command=go_menuanterior1)
    bt_Voltar_window = canvas2.create_window(580, 80, anchor='sw', window=bt_Voltar, width=140, height=50)


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
        elif (inp_data.get() == "") or (not str(inp_data.get())[0:2].isnumeric()) or (
                not str(inp_data.get())[3:5].isnumeric()) or (not str(inp_data.get())[6:11].isnumeric()):
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

        cur.execute("SELECT ID FROM EMPRESA where nome = '" + inp_nome.get().upper().strip() + "'")

        dado_id_emp = cur.fetchall()

        id_empresa = dado_id_emp[0][0]

        cur.execute('insert into COMPRA(DATA, VALOR_ACAO, QUANTIDADE, UTICKER, ID) values(?, ?, ?, ?, ?)', (str(inp_data.get()).strip(), float(str(inp_valor.get()).replace(",", ".")), int(inp_quant.get()), str(inp_ticker.get()).strip(), int(id_empresa)))
        con.commit()

        cur.execute("SELECT POSICAO_ID FROM POSICAO where ID = " + str(id_empresa) + "")

        dado_id_posicao = cur.fetchall()

        if len(dado_id_posicao) > 0:
            id_posicao = dado_id_posicao[0]

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

    bt_Voltar = ttk.Button = Button(canvas3, font=18, background='#6A5ACD', width=30, text='Voltar', height=2, command=go_menuanterior2)
    bt_Voltar_window = canvas3.create_window(580, 80, anchor='sw', window=bt_Voltar, width=140, height=50)


    # -------------------------------------- FINAL TELA 3 -------------------------------------- #
    # -------------------------------------- LÓGICA TELA 3 -------------------------------------- #

    def trata_str_emp(string):
        nova_str = str(string).replace("[", "").replace("'", "").replace("]", "").replace("{", "").replace("}", "").replace(")", "").replace("(", "").replace(",", "").strip()

        return nova_str


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


    def abrir_mensagem_emp(event):
        item_id = table.focus()

        valor_coluna = table.item(item_id, option='values')[3]

        if len(dados_tabela) != len(table.get_children()):

            cur.execute("SELECT b.NOME," \
                        "       b.SETOR," \
                        "       a.UTICKER," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PRECOMEDIO," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAO as a " \
                        "inner join EMPRESA as b " \
                        "on (a.ID = b.ID)")

            dados_tabela2 = cur.fetchall()

            messagebox.showinfo('Definição de Riscos', dados_tabela2[int(str(item_id)[-1:]) - 1][4])

        else:

            messagebox.showinfo('Definição de Riscos', dados_tabela[int(str(item_id)[-1:]) - 1][4])


    canvas4 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas4.create_image(0, 0, image=bg_image_tk, anchor='nw')

    bt_Voltar = ttk.Button = Button(canvas4, font=18, background='#6A5ACD', width=30, text='Voltar', height=2, command=go_menuanterior3)
    bt_Voltar_window = canvas4.create_window(580, 80, anchor='sw', window=bt_Voltar, width=140, height=50)

    table = ttk.Treeview(canvas4, columns=('Setor', 'Ticker', 'Risco', 'Definicao', 'Valor', 'Preco', 'Papeis', 'Rentabilidade'))

    style = ttk.Style()

    style.configure("Treeview", font=("Arial", 12), padding=(0, 35, 0, 35), background='#B0C4DE')
    style.configure("Treeview.Heading", font=("Arial", 12, 'bold'), padding=(0, 5, 0, 15), foreground='#171F3D')

    table.configure(style="Treeview.Heading")
    table.configure(style="Treeview")

    table.heading('#0', text='Empresa')
    table.heading('Setor', text='Setor')
    table.heading('Ticker', text='Ticker')
    table.heading('Risco', text='Risco')
    table.heading('Definicao', text='Definição')
    table.heading('Valor', text='Valor Total')
    table.heading('Preco', text='Preço Médio')
    table.heading('Papeis', text='Papeis Totais')
    table.heading('Rentabilidade', text='Rentabilidade (%)')

    cur.execute("SELECT b.NOME," \
                "       b.SETOR," \
                "       a.UTICKER," \
                "       a.RISCO," \
                "       a.DEFINICAO," \
                "       a.VALORTOTAL," \
                "       a.PRECOMEDIO," \
                "       a.PAPEISTOTAIS " \
                "from POSICAO as a " \
                "inner join EMPRESA as b " \
                "on (a.ID = b.ID)")

    dados_tabela = cur.fetchall()

    table.column("#0", width=180)
    table.column("Ticker", width=120)
    table.column("Setor", width=150)
    table.column("Risco", width=50)
    table.column("Valor", width=95)
    table.column("Preco", width=105)
    table.column("Papeis", width=105)
    table.column("Rentabilidade", width=140)

    table.configure(padding=10)

    table_window = canvas4.create_window(170, 700, anchor='sw', window=table, width=1210, height=450)

    table.bind("<Double-1>", abrir_mensagem_emp)


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

        cur.execute('insert into COMPRATESOURO(DATA, VALOR_TIT, QUANTIDADE, TIT_ID) values(?, ?, ?, ?)', (str(inp_data_tit.get()).strip(), float(str(inp_valor_tit.get()).replace(",", ".")), int(inp_quant_tit.get()), int(id_titulo)))
        con.commit()

        cur.execute("SELECT POSICAOT_ID FROM POSICAOTESOURO where TIT_ID = " + str(id_titulo) + "")

        dado_id_posicao_tit = cur.fetchall()

        if len(dado_id_posicao_tit) > 0:
            id_posicao_tit = dado_id_posicao_tit[0]

            cur.execute("SELECT (SUM(VALOR_TIT) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE)," \
                        "       (SUM(VALOR_TIT) * SUM(QUANTIDADE)) / COUNT(QUANTIDADE) / SUM(QUANTIDADE)," \
                        "       SUM(QUANTIDADE)" \
                        " FROM COMPRATESOURO where TIT_ID = " + str(id_titulo) + " " \
                                                                       " GROUP BY ID")

            dados_posicao_tit = cur.fetchall()

            cur.execute('UPDATE POSICAOTESOURO SET RISCO = ?, DEFINICAO = ?, VALORTOTAL = ?, PAPEISTOTAIS = ? WHERE TIT_ID = ?', (inp_risco_tit.get(), inp_motivo_tit.get("1.0", "end-1c"), dados_posicao_tit[0][0], dados_posicao_tit[0][1], dados_posicao_tit[0][2], id_titulo))
            con.commit()

            texto_info = "Compra registrada com sucesso! Sua posição no título foi atualizada."
            lbl_info = messagebox.Message(title='Investify', message=texto_info)
            lbl_info.show()

        else:
            cur.execute('insert into POSICAOTESOURO(RISCO, DEFINICAO, VALORTOTAL, PAPEISTOTAIS, TIT_ID) values(?, ?, ?, ?, ?)', (inp_risco_tit.get(), inp_motivo_tit.get("1.0", "end-1c"), float(str(inp_valor_tit.get()).replace(",", ".")) * int(inp_quant_tit.get()), int(inp_quant_tit.get()), id_titulo))
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

    bt_Voltar = ttk.Button = Button(canvas5, font=18, background='#6A5ACD', width=30, text='Voltar', height=2, command=go_menuanterior4)
    bt_Voltar_window = canvas5.create_window(580, 80, anchor='sw', window=bt_Voltar, width=140, height=50)


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
        url_download = 'https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv'  # Substitua pela URL do arquivo que você deseja baixar

        # Diretório de destino para salvar o arquivo
        diretorio_destino = 'C:\\Users\\mrodr\\PycharmProjects\\pythonProject'  # Substitua pelo caminho para o diretório de destino em seu sistema

        # Efetuar o download do arquivo
        response = requests.get(url_download, stream=True)
        with open(f'{diretorio_destino}/PrecoTaxaTesouroDireto', 'wb') as arquivo:
            for chunk in response.iter_content(1024):
                arquivo.write(chunk)

        with open('PrecoTaxaTesouroDireto', 'r') as arquivo:

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

                def obter_ano(data):
                    return int(data[-4:])


                x = (datetime.date.today() - datetime.timedelta(days=dia_menos)).strftime('%d/%m/%Y')

                if list_temp[2] == (datetime.date.today() - datetime.timedelta(days=dia_menos)).strftime('%d/%m/%Y'):

                    lista_nm_titulos.append(trata_str_emp(list_temp[0]))
                    lista_venc_titulos.append(trata_str_emp(list_temp[1]))
                    lista_data_titulos.append(trata_str_emp(list_temp[2]))
                    lista_valor_titulos.append(trata_str_emp(list_temp[5]).replace(" ", ""))

                    control_atu = 1

            dia_menos = dia_menos + 1

        cur.execute("DELETE FROM TEMPTITULOS")

        for k in range (0, len(lista_nm_titulos)):

            cur.execute('insert into TEMPTITULOS(NOME, DT_VENC, DT_BASE, VALOR_TIT) values(?, ?, ?, ?)', (lista_nm_titulos[k], lista_venc_titulos[k], lista_data_titulos[k], float(str(lista_valor_titulos[k]).replace(",", "."))))
            con.commit()

        cur.execute("SELECT a.NOME," \
                    "       a.DT_VENC " \
                    "from TEMPTITULOS as a " \
                    "left join TITULO as b " \
                    "on (UPPER(a.NOME) = b.NOME and a.DT_VENC = b.DT_VENC) " \
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

        valor_coluna = table_fix.item(item_id, option='values')[3]

        if len(dados_tabela_tit) != len(table_fix.get_children()):

            cur.execute("SELECT b.NOME," \
                        "       b.DT_VENC," \
                        "       b.TIPO," \
                        "       a.RISCO," \
                        "       a.DEFINICAO," \
                        "       a.VALORTOTAL," \
                        "       a.PAPEISTOTAIS " \
                        "from POSICAOTESOURO as a " \
                        "inner join TITULO as b " \
                        "on (a.TIT_ID = b.TIT_ID)")

            dados_tabela_tit2 = cur.fetchall()

            messagebox.showinfo('Definição de Riscos', dados_tabela_tit2[int(str(item_id)[-1:]) - 1][4])

        else:

            messagebox.showinfo('Definição de Riscos', dados_tabela_tit[int(str(item_id)[-1:]) - 1][4])


    canvas6 = tk.Canvas(app, width=app.winfo_screenwidth(), height=app.winfo_screenheight())
    canvas6.create_image(0, 0, image=bg_image_tk, anchor='nw')

    bt_Voltar = ttk.Button = Button(canvas6, font=18, background='#6A5ACD', width=30, text='Voltar', height=2, command=go_menuanterior5)
    bt_Voltar_window = canvas6.create_window(580, 80, anchor='sw', window=bt_Voltar, width=140, height=50)

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

    cur.execute("SELECT b.NOME," \
                "       b.DT_VENC," \
                "       b.TIPO," \
                "       a.RISCO," \
                "       a.DEFINICAO," \
                "       a.VALORTOTAL," \
                "       a.PAPEISTOTAIS " \
                "from POSICAOTESOURO as a " \
                "inner join TITULO as b " \
                "on (a.TIT_ID = b.TIT_ID)")

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

except urllib.error.URLError:
    texto_erro = "Sem conexão com a internet. Conecte para usar o app."
    lbl_erro = messagebox.Message(title='Investify', message=texto_erro)
    lbl_erro.show()

    app.destroy()

#################
app.mainloop()

con.close()