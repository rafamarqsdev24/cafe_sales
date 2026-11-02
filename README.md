# Recuperação da Confiabilidade dos Dados de Vendas

![](images/cafe_sales.png)

Análise de vendas de uma cafeteria: da investigação e preparação de uma base com dados sujos até a resposta de perguntas de negócio em SQL e a divulgação dos insights obtidos.

> Dataset utilizado: [Cafe Sales - Dirty Data for Cleaning Training](https://www.kaggle.com/datasets/ahmedmohamed2003/cafe-sales-dirty-data-for-cleaning-training).

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)

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

A operação de vendas da cafeteria registra suas transações em um sistema único, que gera uma base com 10.000 registros e 8 campos por transação. Essa base é utilizada por diferentes áreas da empresa para tomada de decisão.

Uma auditoria inicial revelou que os dados não estão prontos para uso analítico: 10.082 de 80.000 células, cerca de 12.6% estão ausentes ou inválidas, e só 30.89% das linhas não têm nenhuma coluna suja. A liderança da cafeteria não consegue confiar nos relatórios de vendas gerados a partir da base atual. Abaixo, o significado de cada coluna da base:

|  #  | Coluna           | Descrição                          |
| :-: | :--------------- | :--------------------------------- |
|  1  | transaction_id   | Identificador único de cada venda  |
|  2  | item             | Produto vendido                    |
|  3  | quantity         | Quantidade vendida                 |
|  4  | price_per_unit   | Preço unitário do produto          |
|  5  | total_spent      | Valor total da venda               |
|  6  | payment_method   | Forma de pagamento                 |
|  7  | location         | Local onde o produto foi consumido |
|  8  | transaction_date | Data da venda                      |

## 2. Objetivo do Projeto

Transformar a base bruta de vendas da cafeteria em um conjunto de dados limpo, documentado e auditável, que permita responder com confiança às perguntas centrais de negócio para ajudar a liderança a tomar decisões orientadas a dados.

## 3. Arquitetura do Projeto

O projeto segue um pipeline linear, onde cada etapa consome a saída da anterior: os dados brutos são tratados com Pandas, carregados no PostgreSQL, e a partir do banco se ramificam em duas frentes de consumo: as consultas SQL, que respondem às perguntas de negócio, e o Streamlit, que consolida os resultados em um data app.

![](images/project_architecture.png)

## 4. Etapas da Análise

1. [Exploração Inicial](notebooks/01_initial_exploration.ipynb): investigação da estrutura da tabela para entender como pode ser feita a limpeza dos dados.
2. [Preparação dos Dados](notebooks/02_data_preparation.ipynb): conversão dos tipos corretos das colunas para análises, padronização das linhas sujas em NaN, tratamento dos valores ausentes e criação de novas colunas para análises em SQL.
3. [Conexão ao PostgreSQL](notebooks/03_connection_postgres.ipynb): carga do dataset tratado numa tabela `sales`, via SQLAlchemy.
4. [Análise com SQL](sql/01_performance_2023/01_overall_performance.sql): respostas de perguntas de negócio utilizando um Banco de Dados.
5. [Visualização no Streamlit](streamlit/app.py): data app para visualização dos insights.

## 5. Principais Decisões de Limpeza

A limpeza seguiu três regras: a base bruta nunca é alterada, um valor só é recuperado quando uma regra o calcula a partir de outros da mesma linha, e o que não pode ser calculado não é estimado. A base passou de 10.000 para 9.974 linhas, cerca de 0.26% removida.

> O detalhamento de cada decisão está no arquivo [cleaning_decisions](docs/cleaning_decisions.md).

- **Padronização de valores ausentes:** Os registros preenchidos como `ERROR` e `UNKNOWN` foram convertidos para `NaN` por representarem o mesmo problema de dado inválido. Essa unificação facilitou o tratamento e impactou 10.082 células, cerca de 12.6% da base.
- **Recuperação matemática de dados:** Valores numéricos foram recalculados com base na regra lógica `quantity × price_per_unit = total_spent`, aproveitando que os preços por item são fixos e as linhas completas não possuíam divergências.
- **Preenchimento com categoria "Not Specified":** Campos vazios de produto, forma de pagamento e canal receberam a categoria `Not Specified`.
- **Preservação de datas ausentes:** Vendas com datas nulas foram mantidas como `NaT`, pois não havia regras para deduzi-las e inventar períodos geraria dados falsos.
- **Descarte de linhas sem solução:** Foram descartadas apenas as linhas que apresentavam duas ou mais colunas numéricas ausentes de forma simultânea, situação que inviabilizava qualquer cálculo por gerar equações com duas incógnitas.

## 6. Perguntas de Negócio

> As respostas serão calculadas em SQL, sobre o dataset limpo. As consultas ficarão em `sql/`. Cada resposta informa a parcela de vendas que ficou fora da conta por falta de informação.

> Você pode encontrar um maior detalhamento no arquivo [_insights_](docs/insights.md).

### Faturamento e sazonalidade

1. **Qual foi o desempenho geral de 2023?**

No ano de 2023, a cafeteria teve um total de 9974 vendas, com faturamento de $89,042.00, ticket médio de $8.93 e uma média de 3,02 unidades por venda.

Já no recorte trimestral, a cafeteria teve um desempenho bastante linear: o 2º trimestre teve o melhor resultado em faturamento, com $21,464.50; enquanto o pior foi o 3º trimestre, com $20,841.00, uma diferença de 2.90%.

2. **Como o faturamento varia mês a mês e o que explica os melhores e piores meses?**

O faturamento varia pouco, de $6,644.00 (fevereiro) a $7,353.00 (junho). O que explica os melhores e piores meses é o número de vendas, não o ticket médio, que fica entre 8,72 e 9,31.

3. **Como as vendas se distribuem pela semana, e isso muda entre In-store e Takeaway?**

Somando os dois canais, a quinta fatura mais, com $7,700.00 e a quarta menos $6,852.50. O melhor dia muda de canal: quinta tem o melhor faturamento na loja (In-store), com $4,013.00 e domingo no para viagem (Takeaway), com $3,844.50.

Cada dia e canal tem cerca de 400 vendas, então as diferenças são pequenas e não sustentam mudar a escala.

### Produtos e preço

4. **Quais itens mais faturam, e quanto os 3 primeiros representam do total?**

Os itens que mais faturam são: Salad, com $19,095.00; Sandwich, com $13,716.00 e Smoothie, com $13,344.00. Juntos, correspondem a exatos 51.84% do faturamento total.

Isso significa que dos 8 produtos vendidos pela cafeteria, mais de metade do faturamento se concentra nesses 3 itens, que são os mais caros do estabelecimento.

5. **O faturamento de cada item vem de volume ou de preço?**

Salad é o item que mais fatura e o 2º em quantidade vendida, com 3.819 unidades. Já Sandwich e Smoothie, o 2º e o 3º em faturamento, são os dois que menos vendem em quantidades, com 3.429 e 3.336 unidades, respectivamente.

Isso mostra que o faturamento de cada item depende mais do preço unitário do que do volume vendido: os três itens que mais faturam são os mais caros ($5.00, $4.00 e $4.00), mesmo sem estarem entre os mais vendidos em unidades.

6. **Quantas unidades o cliente leva por venda, e o ticket cresce com a quantidade?**

O cliente leva de 1 a 5 unidades, e cada quantidade representa cerca de 20% das vendas, de 1.926 a 2.108. O ticket médio cresce com a quantidade, de $2.96 para $14.86, mas é um efeito direto: já que o total é quantidade vezes preço.

O preço médio por unidade fica entre $2.91 e $2.97 em todas as quantidades, ou seja, quem leva mais não escolhe itens diferentes.

### Canais e pagamento

7. **In-store e Takeaway são negócios diferentes?**

Não parecem ser. Vendas na loja faturam $27,140.00 e para viagem $26,552.50, uma diferença de 2.2%, com um número de vendas quase igual, com 3.006 e 3.016 vendas, respectivamente. Já o ticket médio na loja é $9.03 e para viagem é $8.80.

Salad, Sandwich e Smoothie são os três itens que mais faturam nos dois canais, na mesma ordem. A diferença está na 4ª e 5ª posições: Juice vem antes de Cake no In-store, e o contrário no Takeaway.

8. **Como os clientes pagam, e a forma de pagamento está ligada ao valor da compra?**

As três formas pesam quase o mesmo. Credit Card fatura $20,446.00, Digital Wallet fatura $20,405.00 e Cash fatura $20,402.50, uma diferença de 0.2%. O número de vendas varia só 30 entre elas, de 2.254 a 2.284.

Por canal, o ticket médio de Digital Wallet é $9.46 na loja e $8.49 para viagem. O de Cash é $9.13 na loja e $8.90 para viagem. Credit Card fica igual nos dois, com $8.85.

## 7. Estrutura do Projeto

```text
cafe-sales/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── images/
├── notebooks/
│   ├── 01_initial_exploration.ipynb
│   ├── 02_data_preparation.ipynb
│   └── 03_connection_postgres.ipynb
├── sql/
├── src/
├── streamlit/
├── .env.example → vira .env
├── LICENSE
├── pixi.toml / pixi.lock / pyproject.toml
└── README.md
```

## 8. Como Reproduzir

### 8.1 Instalar o gerenciador de pacotes Pixi

**Requisito:** [Pixi](https://pixi.prefix.dev/latest/installation/) instalado. Ele cria o ambiente (Python 3.13 e as bibliotecas) a partir do `pixi.lock`, em Windows, Linux ou macOS.

> Instale de acordo com o seu sistema operacional. Para a instalação via terminal:

**Windows:**

```bash
powershell -ExecutionPolicy Bypass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

**Linux ou MacOS:**

```bash
curl -fsSL https://pixi.sh/install.sh | sh
```

### 8.2 Clonar o projeto e instalar as dependências

Você pode baixar o [repositório](https://github.com/rafamarqsdev24/cafe_sales) como ZIP na interface web do GitHub:

![](images/clone_repository.png)

Você também pode clonar via terminal, pelo HTTPS ou SSH:

**HTTPS:**

```bash
git clone https://github.com/rafamarqsdev24/cafe_sales.git
```

**SSH:**

> Você deve criar uma chave [SSH](https://github.com/settings/ssh/new).

```bash
git clone git@github.com:rafamarqsdev24/cafe_sales.git
```

Após isso, você precisará criar o ambiente Pixi no projeto:

> O pixi cria o ambiente isolado do projeto com as dependências listadas no [pixi.toml](pixi.toml). Ele precisa ser executado dentro da pasta `cafe_sales`.

```bash
cd cafe_sales
pixi install
```

Agora será preciso usar uma IDE, eu recomendo o [VS Code](https://code.visualstudio.com/?_exp_home=e855cfac50).

```bash
code .
```

Com o projeto aberto no VS Code, abra cada notebook da pasta `notebooks/` e escolha o ambiente do projeto como kernel:

> Será preciso ter as extensões [Python](vscode:extension/ms-python.python) e [Jupyter](vscode:extension/ms-toolsai.jupyter) instaladas.

1. Clique em **Select Kernel**, no canto superior direito do notebook.
2. Escolha **Python Environments** e selecione o ambiente dentro de `.pixi/envs/default`.
3. Execute as células. Se o ambiente não aparecer na lista, use **Enter interpreter path** e informe `.pixi\envs\default\python.exe` (Windows) ou `.pixi/envs/default/bin/python` (Linux e MacOS).

### 8.3 Criar o banco de dados no PostgreSQL

Antes de executar os `notebooks`, é preciso de um banco já criado no seu PostgreSQL local para receber os dados. 

> Será necessário instalar duas extensões: [SQLTools](vscode:extension/mtxr.sqltools) e [SQLTools PostgreSQL/Cockroach Driver](vscode:extension/mtxr.sqltools-driver-pg)

Com as extensões instaladas, abra o `SQLTools` e selecione a opção do `PostgreSQL`. Nomeei a conexão em **Connection name**:

```text
postgres-cafe_sales
```

![](images/sqltools_vscode.png)

Após isso, selecione a opção Connection String na seção **Connect using**, e cole o comando abaixo alterando com as suas credenciais.

> Geralmente o username será `postgres`, o host será `localhost` e a port será `5432`. Mas é interessante verificar suas credenciais no pgAdmin.

```bash
postgresql://username:password@host:port/cafe_sales
```

Navegue até o final da página, e selecione **SAVE CONNECTION**. Vai abrir um arquivo `.sql`, mas você não precisa salvá-lo.

Caso você queira utilizar a interface gráfica oficial do PostgreSQL, você deve instalar o [pgAdmin](https://www.pgadmin.org/). Siga esse passo a passo para criar o banco de dados:

#### Opção A: Usando o pgAdmin (interface gráfica)

1. Abra o **pgAdmin** e conecte-se ao seu servidor local.
2. Clique com o botão direito em **Databases** → **Create** → **Database...**
3. Preencha:
   - **Database**: `cafe_sales`
   - **Encoding**: `UTF8`
4. Clique em **Save**.

#### Opção B: Usando o terminal (`psql`)

Se você tiver o `psql` configurado nas variáveis de ambiente, basta rodar:

```bash
psql -U postgres -c "CREATE DATABASE cafe_sales ENCODING 'UTF8';"
```

### 8.4 Configurar as variáveis de ambiente do banco

O notebook [03_connection_postgres.ipynb](notebooks/03_connection_postgres.ipynb) carrega a base limpa no PostgreSQL. Para isso, crie um arquivo .env na raiz do projeto, copiando o modelo disponível:

```bash
cp .env.example .env
```

> Em seguida, edite o .env com as suas credenciais no `PostgreSQL`, da mesma forma que fizemos na conexão com string pelo SQLTools.

### 8.5 Executar os notebooks em ordem

Execute os notebooks na seguinte ordem:

| Ordem | Notebook                     | O que ele faz                                        |
| :---: | :--------------------------- | :--------------------------------------------------- |
|   1   | 01_initial_exploration.ipynb | Diagnóstico da base bruta                            |
|   2   | 02_data_preparation.ipynb    | Limpeza, feature engineering e exportação do Parquet |
|   3   | 03_connection_postgres.ipynb | Carga da base limpa no PostgreSQL                    |

> Atenção ao caminho relativo: os notebooks leem o CSV bruto com `../data/raw/`. Por isso, execute-os a partir da pasta notebooks/, que é o comportamento padrão do Jupyter Notebook.

### 8.6 Rodar as queries SQL

#### Opção A: VS Code com SQLTools

Navegue até o arquivo [00_casting_numeric.sql](sql/00_casting_columns/00_casting_numeric.sql) para alterar as colunas com representações monetárias para o tipo `NUMERIC`, facilitando o uso do ROUND em outras queries.

Considere selecionar as queries a serem executadas arrastando o mouse e usando o atalho de **Run Selected Query**, que no meu caso é o atalho `Ctrl + E Ctrl + E`. Caso você não consiga, é só apertar o botão direito do mouse e selecionar o comando indicado.

Finalizada a etapa de tipagem das colunas no SQL: você pode executar os arquivos na ordem que preferir, visto que as análises não tem uma ordem obrigatória.

#### Opção B: pgAdmin

1. Abra o **Query Tool**.
2. Cole o conteúdo de cada `.sql` em apenas um arquivo utilizando o terminal, dentro da pasta `sql/`:

**Windows:**

```bash
(for /R . %f in (*.sql) do @(type "%f" & echo.)) > all_queries.sql
```

**Linux ou MacOS:**

```bash
find . -name "*.sql" | sort | while read -r f; do cat "$f"; echo -e "\n"; done > all_queries.sql
```

3. Selecione a query com o mouse e execute com `F5`.

## 9. Tecnologias

- **Python 3.13:** Pandas, NumPy, Matplotlib e Seaborn
- **pixi:** para o ambiente reproduzível (`pixi.lock`)
- **PyArrow:** para o dataset limpo em Parquet.
- **PostgreSQL:** com `SQLAlchemy` para as análises de negócio
- **Streamlit:** data app para visualização dos insights

## 10. Autor

**Rafael Marques** Estudante de Análise e Desenvolvimento de Sistemas, FAETERJ Paracambi

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rafamarques12/) [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rafamarqsdev24) [![Email](https://img.shields.io/badge/Email-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:rafaelmarques.dev24@gmail.com)
