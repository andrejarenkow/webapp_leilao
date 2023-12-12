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
col2.caption('Painel desenvolvido por André Jarenkow')


with st.form('Atualizar dados!'):
    st.write('Analisar leilão!')
    link_leilao = st.text_input('Cole aqui o link para o catálogo', placeholder = 'exemplo: https://www.letravivaleiloes.com.br/leilao.asp?Num=38762')

# Every form must have a submit button.
    submitted = st.form_submit_button("Analisar")
 
if submitted:
  st.write('Aqui está:')

  #criando as listas que serão os Datasets
  @st.cache_data()
  def load_data(numero):
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
   
 
   for i in range(1,20,1):
       print(i)
       url = link_leilao +'&pag=' + str(i)
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
         tamanho  = tamanho + len(lista_descricao)
   
         for i,j in zip(soup('div',{'class':'lotevendido lote-control'}), range(len(soup('div',{'class':'lotevendido lote-control'})))):
           if j % 3 == 0:
             lote_vendido.append(i.get_text().strip())
   
         for item in lista_descricao:
           descricao = item.get_text()
           descricoes.append(descricao)
   
         lista_lances = soup.findAll('strong')
         for item in lista_lances:
               lance = item.get_text()
               lances.append(lance)
   
   
         lista_visitas = soup.findAll('div',{'class':'extra-info-lance'})
         for item in lista_visitas:
           visita = item.find('span').get_text()
           visitas.append(visita)
   
   
         for link in soup.findAll('div', {'class':'product-image zoom_01'}):
           imagens.append(link.img['src'])
           links.append('https://www.letravivaleiloes.com.br/'+link.img['value'])
   
         for i,j in zip(soup('div',{'class':'product-price-bid'}), range(len(soup('div',{'class':'product-price-bid'})))):
           if j % 3 == 0:
             bids.append(i.get_text().strip().split('\r')[0])        
   
     #print(tamanho)
    leilao_catalogo.extend([catalogo]*tamanho)
   
   
       #print(len(precos))
   
   #  links = list(set(links))
   
   print(len(precos))
   print(len(descricoes))
   print(len(lote_vendido))
   print(len(visitas))
   print(len(links))
   
   df = []
   df.append(precos)
   df.append(descricoes)
   df.append(lote_vendido)
   df.append(visitas)
   df.append(links)
   df.append(imagens)
   df.append(bids)
   
   
   df_geral = pd.DataFrame(df).T
   df_geral.columns = ['preço', 'descrição','lote vendido', 'visitas', 'links', 'imagem', 'lances']
   #df_geral['Catalogo'] = leilao_catalogo
   dados = pd.concat([df_geral,dados])
   for coluna in dados.columns:
     dados[coluna] = dados[coluna].str.strip()
   
   preco_limpo = []
   for i in dados['preço']:
     try:
       limpo = float(i.split('R$ ')[1].replace(',',''))
       preco_limpo.append(limpo)
     except:
       preco_limpo.append(-1)
   
   dados['visitas'] = dados['visitas'].astype(int)
   dados['preço'] = preco_limpo
   dados['preço'] = dados['preço'].replace(r'^\s*$', np.nan, regex=True)
   dados['lote vendido'] = dados['lote vendido'].replace('None', np.nan, regex=True)
   dados = dados[dados['preço']>0].reset_index(drop=True)
  
   dados['lances'] = dados['lances'].astype(int)
   dados['lancado'] = dados['lances'].apply(lambda x: 1 if x > 0 else 0)
   dados['valor_vendido'] = dados['lancado']*dados['preço']
   dados['id'] = dados['links'].apply(lambda x: x.split('ID=')[1].split('&')[0])
   dados.sort_values([ 'valor_vendido' ], ascending=False, inplace=True)
  
   def busca_historico_lances(id_peca):
    url = 'https://www.letravivaleiloes.com.br/ajax/le_historico_peca.asp'
    data = {"id":id_peca}
    r = urlopen(Request(url, data=urlencode(data).encode()))
    html = r.read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(html, 'html.parser')
  
    try:
      data_ultima = soup.find('span').get_text()
  
    except:
      data_ultima = '-'
      
    try:
      interessados = soup.get_text().split()[0].split('|')[1]
    
    except:
      interessados = 0
      
    lance_automatico = 'AUTOMATICO' in soup.get_text()
  
  
    return lance_automatico, interessados, data_ultima
   
   #automatico = '-'
   #interessados = '-'
   #data_ultima = '-'
  
   for i in dados['id']:
          print(i)
          valores = busca_historico_lances(i)
          automatico.append(valores[0])
          interessados.append(int(valores[1]))
          data_ultima.append(valores[2])
  
   dados['automatico'] = automatico
   dados['interessados'] = interessados
   dados['data_ultima'] = data_ultima
    
  
   return dados
  
  #prg = st.progress(0) 
    
  #for i in range(100): 
  #    time.sleep(0.1) 
  #    prg.progress(i+1) 
  
  dados['lances'] = dados['lances'].astype(int)
  dados['lancado'] = dados['lances'].apply(lambda x: 1 if x > 0 else 0)
  dados['valor_vendido'] = dados['lancado']*dados['preço']
  dados['id'] = dados['links'].apply(lambda x: x.split('ID=')[1].split('&')[0])
  dados.sort_values([ 'valor_vendido' ], ascending=False, inplace=True)
  #dados['data_ultima'] = pd.to_datetime(dados['data_ultima'], errors='coerce', dayfirst=True)
  #st.success("Banco de dados atualizado!")
  
  
  col1, col2, col3 = st.columns([1,2,3])
   
  with col3:
       st.dataframe(dados[['imagem','descrição','preço','lances','visitas','links']],hide_index=True,
                    use_container_width=True,
                    height=600,
                   column_config={
                   'descrição':st.column_config.TextColumn(width='medium'),
                   'imagem':st.column_config.ImageColumn(),
                   'links':st.column_config.LinkColumn(),
                   'preço':st.column_config.NumberColumn(
                     'Preço',
                     format="R$%.2f",
                     width='small'
                   ),
                     'lances':st.column_config.NumberColumn(
                     'Lances',
                     width='small'
                   ),
                   })
   
  total_historico_valores = pd.read_csv('https://docs.google.com/spreadsheets/d/e/2PACX-1vQWwT_7xvVyE_Yu1UeBfBKm8eq-biwQ0toD94DFAwPA0cvX-HBq6SajnyEIJRkujHiQTEiiHR_Q34kq/pub?gid=0&single=true&output=csv')
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
  
  leilao_dia_1 = 166987-109694
  leilao_dia_2 = 232594 - 166987
   
  with col1:
   container = st.container(border=True)
   with container:
    st.metric('Valor vendido', f'R$ {dados["valor_vendido"].sum():,.2f}',)# delta = f'R$ {dados["valor_vendido"].sum()-valor_vendido_ontem:,.2f} em relação a ontem')
    st.metric('Incremento Dia 1', f'R$ {leilao_dia_1:,.2f}')
    st.metric('Incremento Dia 2', f'R$ {leilao_dia_2:,.2f}')
    st.metric('Comissão estimada', f'R$ {dados["valor_vendido"].sum()*0.05:,.2f}')
    #st.metric('Total de Visitas', dados['visitas'].sum())
    #st.metric('Total de Lances', dados['lances'].sum())
    st.metric('Itens com lances', f"{((dados['lances']>0).sum()/len(dados['lancado'])*100).round(1)} %")
   
   
   
  with col2:
     fig = px.line(dados_historico, x='data', y='somatorio', title="Histórico do valor total de vendas", markers=True)
     # Set x-axis title
     fig.update_xaxes(title_text="Data")
     
     # Set y-axes titles
     fig.update_yaxes(title_text="Venda total")
     st.plotly_chart(fig, use_container_width=True)



