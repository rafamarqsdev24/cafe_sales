# Recuperação da Confiabilidade dos Dados de Vendas

Análise de vendas de uma cafeteria: da investigação e preparação de uma base com dados sujos até a resposta de perguntas de negócio em SQL e a divulgação dos insights obtidos.

> Dataset utilizado: [Cafe Sales - Dirty Data for Cleaning Training](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training).

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)

## Índice

1. [Problema de Negócio](#1-problema-de-negócio)
2. [Objetivo do Projeto](#2-objetivo-do-projeto)
3. [Arquitetura do Projeto](#3-arquitetura-do-projeto)
4. [Etapas da Análise](#4-etapas-da-análise)
5. [Principais Decisões de Limpeza](#5-principais-decisões-de-limpeza)
6. [Perguntas de Negócio](#6-perguntas-de-negócio)
7. [Estrutura do Projeto](#7-estrutura-do-projeto)
8. [Como Reproduzir](#8-como-reproduzir)
9. [Tecnologias](#9-tecnologias)
10. [Autor](#10-autor)

## 1. Problema de Negócio

A operação de vendas do café registra suas transações em um sistema único, que gera uma base com 10.000 registros e 8 campos por transação. Essa base é utilizada por diferentes áreas da empresa para tomada de decisão.

Uma auditoria inicial revelou que os dados não estão prontos para uso analítico: 10.082 de 80.000 células, cerca de 12,6% estão ausentes ou inválidas, e só 30,89% das linhas não têm nenhuma coluna suja. A liderança do café não consegue confiar nos relatórios de vendas gerados a partir da base atual. Abaixo, o significado de cada coluna da base:

|  #  | Coluna             | Descrição                          |
| :-: | :----------------- | :--------------------------------- |
|  1  | `transaction_id`   | Identificador único de cada venda  |
|  2  | `item`             | Produto vendido                    |
|  3  | `quantity`         | Quantidade vendida                 |
|  4  | `price_per_unit`   | Preço unitário do produto          |
|  5  | `total_spent`      | Valor total da venda               |
|  6  | `payment_method`   | Forma de pagamento                 |
|  7  | `location`         | Local onde o produto foi consumido |
|  8  | `transaction_date` | Data da venda strikethrough text   |

## 2. Objetivo do Projeto

Transformar a base bruta de vendas do café em um conjunto de dados limpo, documentado e auditável, que permita responder com confiança às perguntas centrais de negócio para ajudar a liderança a tomar decisões orientadas a dados.

## 3. Arquitetura do Projeto

O projeto segue um pipeline linear, onde cada etapa consome a saída da anterior: os dados brutos são tratados com Pandas, carregados no PostgreSQL, e a partir do banco se ramificam em duas frentes de consumo: as consultas SQL, que respondem às perguntas de negócio, e o Streamlit, que consolida os resultados em um data app.

## 4. Etapas da Análise

1. [Exploração Inicial](notebooks/01_initial-exploration.ipynb): investigação da estrutura da tabela para entender como pode ser feita a limpeza dos dados.
2. [Preparação dos Dados](notebooks/02_data-preparation.ipynb): conversão dos tipos corretos das colunas para análises, padronização das linhas sujas em NaN, tratamento dos valores ausentes e criação de novas colunas para análises em SQL.
3. [Conexão ao PostgreSQL](notebooks/03_connection_postgres.ipynb): carga do dataset tratado numa tabela `sales`, via SQLAlchemy.
4. [Análise com SQL](sql/01_performance_2023/01_overall_performance.sql): respostas de perguntas de negócio utilizando um Banco de Dados.
5. [Visualização no Streamlit](streamlit/app.py): data app para visualização dos insights.

## 5. Principais Decisões de Limpeza

A limpeza seguiu três regras: a base bruta nunca é alterada, um valor só é recuperado quando uma regra o calcula a partir de outros da mesma linha, e o que não pode ser calculado não é estimado. A base passou de 10.000 para 9.974 linhas, cerca de 0.26% removida.

> O detalhamento de cada decisão está no arquivo [cleaning_decisions](docs/cleaning_decisions.md).

- **Padronização de valores ausentes:** Os registros preenchidos como `ERROR` e `UNKNOWN` foram convertidos para `NaN` por representarem o mesmo problema de dado inválido. Essa unificação facilitou o tratamento e impactou 10.082 células, cerca de 12.6% da base.
- **Recuperação matemática de dados:** Valores numéricos foram recalculados com base na regra lógica `quantity × price_per_unit = total_spent`, aproveitando que os preços por item são fixos e as linhas completas não possuíam divergências.
- **Preenchimento com categoria "Not Specified":** Campos vazios de produto, forma de pagamento e canal receberam a categória `Not Specified`.
- **Preservação de datas ausentes:** Vendas com datas em nulas foram mantidas como `NaT`, pois não havia regras para deduzi-las e inventar períodos geraria dados falsos.
- **Descarte de linhas sem solução:** Foram descartadas apenas as linhas que apresentavam duas ou mais colunas numéricas ausentes de forma simultânea, situação que inviabilizava qualquer cálculo por gerar equações com duas incógnitas.

## 6. Perguntas de Negócio

> As respostas serão calculadas em SQL, sobre o dataset limpo. As consultas ficarão em `sql/`. Cada resposta informa a parcela de vendas que ficou fora da conta por falta de informação. Você pode encontrar um maior detalhamento no arquivo [_insights_](docs/insights.md).

### Faturamento e sazonalidade

1. **Qual foi o desempenho geral de 2023?**

2. **Como o faturamento varia mês a mês e o que explica os melhores e piores meses?**

3. **Como as vendas se distribuem pela semana, e isso muda entre In-store e Takeaway?**

### Produtos e preço

4. **Quais itens mais faturam, e quanto os 3 primeiros representam do total?**

5. **O faturamento de cada item vem de volume ou de preço?**

6. **Quantas unidades o cliente leva por venda, e o ticket cresce com a quantidade?**

### Canais e pagamento

7. **In-store e Takeaway são negócios diferentes?**

8. **Como os clientes pagam, e a forma de pagamento está ligada ao valor da compra?**

## 7. Estrutura do Projeto

```text
cafe-sales/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── notebooks/
│   ├── 01_initial-exploration.ipynb
│   ├── 02_data-preparation.ipynb
│   └── 03_connection_postgres.ipynb
├── sql/
├── src/
├── streamlit/
├── .env
├── LICENSE
├── pixi.toml / pixi.lock / pyproject.toml
├── LICENSE
└── README.md
```

## 8. Como Reproduzir

**Requisito:** [pixi](https://pixi.sh/) instalado. Ele cria o ambiente (Python 3.13 e as bibliotecas) a partir do `pixi.lock`, em Windows, Linux ou MacOS.

```bash
git clone https://github.com/rafaelmarquesdev24/cafe-sales.git
cd cafe-sales
pixi install
pixi run lab
```

Com o JupyterLab aberto, execute os notebooks em ordem. A base bruta já está em `data/raw/`, então não é preciso baixar nada.

- Os notebooks `01` e `02` rodam sem banco de dados.
- O notebook `03` precisa de um PostgreSQL em execução. Altere `.env.example` para `.env` e preencha as credenciais de conexão.

> Os notebooks leem o CSV com caminho relativo (`../data/raw/`). Execute-os a partir da pasta `notebooks/`, que é o comportamento padrão do JupyterLab.

## 9. Tecnologias

- **Python 3.13:** Pandas, NumPy, Matplotlib e Seaborn
- **pixi:** para o ambiente reproduzível (`pixi.lock`)
- **PyArrow:** para o dataset limpo em Parquet.
- **PostgreSQL:** com `SQLAlchemy` para as análises de negócio
- **Streamlit:** data app para visualização dos insights

## 10. Autor

**Rafael Marques** Estudante de Análise e Desenvolvimento de Sistemas, FAETERJ Paracambi

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rafamarques12/) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rafamarqsdev24) [![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:rafaelmarques.dev24@gmail.com)
