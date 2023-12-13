#Importação das bibliotecas 
import numpy as np
import pandas as pd
import plotly
from plotly.graph_objs import Scatter, Layout, Heatmap
import plotly.graph_objs as go
import streamlit as st
import matplotlib
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import plotly.figure_factory as ff
import plotly.express as px
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import datetime
 
# Configurações da página
st.set_page_config(
    page_title="Leilao",
    page_icon="	:book:",
    layout="wide",
    initial_sidebar_state='collapsed'
) 
col1, col2, col3 = st.columns([2,12,1])

col2.title('Monitoramento de Leilão')
col2.caption('aplicação desenvolvida por André Jarenkow')


with st.form('Atualizar dados!'):
 st.write('Analisar leilão!')
 link_leilao = st.text_input('Cole aqui o link para o catálogo', placeholder = 'exemplo: https://www.letravivaleiloes.com.br/leilao.asp?Num=38762')


# Every form must have a submit button.
 submitted = st.form_submit_button("Analisar")
 
if submitted:
  st.write('Aguarde um pouco enquanto analisamos o leilão.')
 

  #criando as listas que serão os Datasets
  @st.cache_data(persist =True)
  def load_data(link_leilao):
   # Título do leilão
   url = link_leilao
   response = urlopen(url)
   html = response.read()
   soup = BeautifulSoup(html, 'html.parser')
   nome_leilao = soup.find_all('h2')[0].get_text()
  
   precos = []
   descricoes = []
   lances = []
   visitas = []
   links = []
   leilao_catalogo = []
   lote_vendido = []
   imagens = []
   bids = []
   
   dados = pd.DataFrame()
   
   page = 0
   #for i in range(1,100,1):
   while len(soup('p',{'class':'price-bid'}))>0:
       page += 1
       print(page)
       num_leilao = link_leilao.split('Num=')[1]
       leiloeiro = link_leilao.split('www.')[1].split('.com.br')[0]
       url = f'https://www.{leiloeiro}.com.br/catalogo.asp?Num='+ str(num_leilao) +'&pag=' + str(page)
       response = urlopen(url)
       html = response.read()
       soup = BeautifulSoup(html, 'html.parser')
   
       #print(i)
   
       if len(soup('p',{'class':'price-bid'}))>0:
         #print('contém esta página')
         lista_precos = soup('p',{'class':'price-bid'})
         for numero in range(len(lista_precos)):
           if (numero % 2) == 0:
             preco = lista_precos[numero].get_text()
   
             precos.append(preco)
   
         lista_descricao = soup.findAll('div', {'class':'twelve columns product-description'})
         
   
         #for i,j in zip(soup('div',{'class':'lotevendido lote-control'}), range(len(soup('div',{'class':'lotevendido lote-control'})))):
         #  if j % 3 == 0:
         #    lote_vendido.append(i.get_text().strip())
   
         for item in lista_descricao:
           descricao = item.get_text()
           descricoes.append(descricao)
   
         #lista_lances = soup.findAll('strong')
         #for item in lista_lances:
         #      lance = item.get_text()
         #      lances.append(lance)
   
   
         lista_visitas = soup.findAll('div',{'class':'extra-info-lance'})
         for item in lista_visitas:
           visita = item.find('span').get_text()
           visitas.append(visita)
   
   
         for link in soup.findAll('div', {'class':'product-image zoom_01'}):
           imagens.append(link.img['src'])
           links.append(f'https://www.{leiloeiro}.com.br/'+link.img['value'])
   
         #for i,j in zip(soup('div',{'class':'product-price-bid'}), range(len(soup('div',{'class':'product-price-bid'})))):
         #  if j % 3 == 0:
         #    bids.append(i.get_text().strip().split('\r')[0])     

         
   
     #print(tamanho)
   
   
   
       #print(len(precos))
   
   #  links = list(set(links))
   
   print(len(precos))
   print(len(descricoes))
   print(len(lote_vendido))
   print(len(visitas))
   print(len(links))
   
   df = []
   #df.append(precos)
   df.append(descricoes)
   #df.append(lote_vendido)
   df.append(visitas)
   df.append(links)
   df.append(imagens)
   #df.append(bids)
   
   
   df_geral = pd.DataFrame(df).T
   df_geral.columns = ['descrição', 'visitas', 'links', 'imagem']
   #df_geral['Catalogo'] = leilao_catalogo
   dados = pd.concat([df_geral,dados])
   #for coluna in dados.columns:
   #  dados[coluna] = dados[coluna].str.strip()
   
   #preco_limpo = []
   #for i in dados['preço']:
   #  try:
   #    limpo = float(i.split('R$ ')[1].replace(',',''))
   #    preco_limpo.append(limpo)
   #  except:
   #    preco_limpo.append(-1)
   
   dados['visitas'] = dados['visitas'].astype(int)
   #dados['preço'] = preco_limpo
   #dados['preço'] = dados['preço'].replace(r'^\s*$', np.nan, regex=True)
   #dados['lote vendido'] = dados['lote vendido'].replace('None', np.nan, regex=True)
   #dados = dados[dados['preço']>0].reset_index(drop=True)
  
   #dados['lances'] = dados['lances'].astype(int)
   #dados['lancado'] = 1#dados['lances'].apply(lambda x: 1 if x > 0 else 0)
   #dados['valor_vendido'] = dados['lancado']*dados['preço']
   dados['id'] = dados['links'].apply(lambda x: x.split('ID=')[1].split('&')[0])
   #dados.sort_values([ 'valor_vendido' ], ascending=False, inplace=True)
  
   def busca_valores(id, leilo):
    url = f'https://www.{leilo}.com.br/ajax/le_historico_peca.asp'
    data = {"id":id}
    r = urlopen(Request(url, data=urlencode(data).encode()))
    html = r.read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(html, 'html.parser')
    try:
      info = []
      for i in soup.find_all('li'):
        info.append((i.get_text(),id))
  
      dados_historico_preco = pd.DataFrame(info, columns=['info','peca'])
      dados_historico_preco['data'] = pd.to_datetime(dados_historico_preco['info'].str.replace('R$ ','-', regex=False).str.replace('.00','-', regex=False).str.split('-', expand=True)[0],dayfirst=True, errors='coerce')
      dados_historico_preco['valor'] = pd.to_numeric(dados_historico_preco['info'].str.replace(',','').str.replace('R$ ','-', regex=False).str.replace('.00','-', regex=False).str.split('-', expand=True)[1], errors='coerce')
  
    except:
      dados_historico_preco = pd.DataFrame(columns=['info','peca','data','valor'])
  
    return dados_historico_preco

   total_historico_valores = pd.DataFrame()

   for i in dados['id']:
     print(i)
     dados_individual_valores = busca_valores(i, leiloeiro)
     total_historico_valores = pd.concat([total_historico_valores,dados_individual_valores])
   
   
   
  
   return dados, total_historico_valores, nome_leilao
  
  #prg = st.progress(0) 
    
  #for i in range(100): 
  #    time.sleep(0.1) 
  #    prg.progress(i+1) 
  tempo_inicial = time.time()
  dados, total_historico_valores, nome_leilao = load_data(link_leilao)
 # Registra o tempo final
  tempo_final = time.time()
  # Calcula o tempo decorrido
  tempo_decorrido = tempo_final - tempo_inicial
 #Escreve quanto tempo demorou
  st.subheader(nome_leilao)
  st.write(f'Demorou {round(tempo_decorrido, 0)} segundos para rodar analisar.')
 
  #dados['lances'] = dados['lances'].astype(int)
  #dados['lancado'] = dados['lances'].apply(lambda x: 1 if x > 0 else 0)
  
  dados['id'] = dados['links'].apply(lambda x: x.split('ID=')[1].split('&')[0])
  
  #dados['data_ultima'] = pd.to_datetime(dados['data_ultima'], errors='coerce', dayfirst=True)
  #st.success("Banco de dados atualizado!")
  dados_precos = pd.pivot_table(total_historico_valores, index='peca', values='valor', aggfunc=['max', 'count']).T.reset_index().T.reset_index().drop([0,1])
  dados_precos.columns = ['peca', 'valor', 'lancess']
  dados = dados.merge(dados_precos, left_on='id', right_on='peca', how='left')
  dados['lancado'] = dados['lancess'].apply(lambda x: 1 if x > 0 else 0)
  dados['valor_vendido'] = dados['lancado']*dados['valor']
  dados.sort_values([ 'valor_vendido' ], ascending=False, inplace=True)

  
  
  col1, col2, col3 = st.columns([1,2,3])
   
  with col3:
       st.dataframe(dados[['imagem','descrição','valor','lancess','visitas','links']].fillna('Lote nào vendido'),hide_index=True,
                    use_container_width=True,
                    height=600,
                   column_config={
                   'descrição':st.column_config.TextColumn(width='medium'),
                   'imagem':st.column_config.ImageColumn(),
                   'links':st.column_config.LinkColumn(),
                   'valor':st.column_config.NumberColumn(
                     'Preço vendido',
                     format="R$%.2f",
                     width='small'
                   ),
                     'lancess':st.column_config.NumberColumn(
                     'Lances',
                     width='small'
                   ),
                   })
   
  
  dados_historico = pd.pivot_table(total_historico_valores, index='peca', columns='data', values='valor', aggfunc='max')
  dados_historico = dados_historico.T.ffill().fillna(0)
  dados_historico['somatorio'] = dados_historico.sum(axis=1)
  dados_historico = dados_historico.reset_index()
  
  try:
   ontem = (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
   valor_vendido_ontem = historico_limpo[historico_limpo['data']==ontem]['somatorio'].values[0]
  
  except:
   ontem = (datetime.datetime.today() - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
   valor_vendido_ontem = 0#historico_limpo[historico_limpo['data']==ontem]['somatorio'].values[0]
  
  
  with col1:
   container = st.container(border=True)
   with container:
    st.metric('Valor vendido', f'R$ {dados["valor_vendido"].sum():,.2f}',)
    st.metric('Total de Visitas', dados['visitas'].sum())
    st.metric('Total de Lances', dados_precos['lancess'].sum())
    st.metric('Itens com lances', f"{((dados_precos['lancess']>0).sum()/len(dados)*100).round(1)} %")
   
   
   
  with col2:
     fig = px.line(dados_historico, x='data', y='somatorio', title="Histórico do valor total de vendas", markers=True)
     # Set x-axis title
     fig.update_xaxes(title_text="Data")
     
     # Set y-axes titles
     fig.update_yaxes(title_text="Venda total")
     st.plotly_chart(fig, use_container_width=True)



