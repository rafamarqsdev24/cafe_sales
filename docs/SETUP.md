# Setup do repositório `cafe_sales`

Esse arquivo é um tutorial para quem tiver interesse em executar os notebooks e a as consultas em SQL presentes no projeto.

**Requisito:** você deve já deve ter o ambiente `pixi` instalado e configurado em sua máquina. O passo a passo está em [## 8. Como Reproduzir](../README.md/#8-como-reproduzir)

Para os próximos passos, será preciso usar uma IDE, eu recomendo o [VS Code](https://code.visualstudio.com/?_exp_home=e855cfac50).

```bash
code .
```

## 1. Executar os notebooks

Com o projeto aberto no VS Code, abra cada notebook da pasta `notebooks/` e escolha o ambiente do projeto como kernel:

> Será preciso ter as extensões [Python](vscode:extension/ms-python.python) e [Jupyter](vscode:extension/ms-toolsai.jupyter) instaladas.

1. Clique em **Select Kernel**, no canto superior direito do notebook.
2. Escolha **Python Environments** e selecione o ambiente dentro de `.pixi/envs/default`.
3. Execute as células. Se o ambiente não aparecer na lista, use **Enter interpreter path** e informe `.pixi\envs\default\python.exe` (Windows) ou `.pixi/envs/default/bin/python` (Linux e MacOS).

## 2. Criar o banco de dados no PostgreSQL

Antes de executar os `notebooks`, é preciso de um banco já criado no seu PostgreSQL local para receber os dados.

> Será necessário instalar duas extensões: [SQLTools](vscode:extension/mtxr.sqltools) e [SQLTools PostgreSQL/Cockroach Driver](vscode:extension/mtxr.sqltools-driver-pg)

Com as extensões instaladas, abra o `SQLTools` e selecione a opção do `PostgreSQL`. Nomeei a conexão em **Connection name**:

```text
postgres-cafe_sales
```

![](../images/sqltools_vscode.png)

Após isso, selecione a opção Connection String na seção **Connect using**, e cole o comando abaixo alterando com as suas credenciais.

> Geralmente o username será `postgres`, o host será `localhost` e a port será `5432`. Mas é interessante verificar suas credenciais no pgAdmin.

```bash
postgresql://username:password@host:port/cafe_sales
```

Navegue até o final da página, e selecione **SAVE CONNECTION**. Vai abrir um arquivo `.sql`, mas você não precisa salvá-lo.

Caso você queira utilizar a interface gráfica oficial do PostgreSQL, você deve instalar o [pgAdmin](https://www.pgadmin.org/). Siga esse passo a passo para criar o banco de dados:

### Opção A: Usando o pgAdmin (interface gráfica)

1. Abra o **pgAdmin** e conecte-se ao seu servidor local.
2. Clique com o botão direito em **Databases** → **Create** → **Database...**
3. Preencha:
   - **Database**: `cafe_sales`
   - **Encoding**: `UTF8`
4. Clique em **Save**.

### Opção B: Usando o terminal (`psql`)

Se você tiver o `psql` configurado nas variáveis de ambiente, basta rodar:

```bash
psql -U postgres -c "CREATE DATABASE cafe_sales ENCODING 'UTF8';"
```

## 3. Configurar as variáveis de ambiente do banco

O notebook [03_connection_postgres.ipynb](../notebooks/03_connection_postgres.ipynb) carrega a base limpa no PostgreSQL. Para isso, crie um arquivo .env na raiz do projeto, copiando o modelo disponível:

```bash
cp .env.example .env
```

> Em seguida, edite o .env com as suas credenciais no `PostgreSQL`, da mesma forma que fizemos na conexão com string pelo SQLTools.

## 4. Executar os notebooks em ordem

Execute os notebooks na seguinte ordem:

| Ordem | Notebook                     | O que ele faz                                        |
| :---: | :--------------------------- | :--------------------------------------------------- |
|   1   | 01_initial_exploration.ipynb | Diagnóstico da base bruta                            |
|   2   | 02_data_preparation.ipynb    | Limpeza, feature engineering e exportação do Parquet |
|   3   | 03_connection_postgres.ipynb | Carga da base limpa no PostgreSQL                    |

> Atenção ao caminho relativo: os notebooks leem o CSV bruto com `../data/raw/`. Por isso, execute-os a partir da pasta notebooks/, que é o comportamento padrão do Jupyter Notebook.

## 4 Rodar as queries SQL

### Opção A: VS Code com SQLTools

Navegue até o arquivo [00_casting_numeric.sql](../sql/00_casting_columns/00_casting_numeric.sql) para alterar as colunas com representações monetárias para o tipo `NUMERIC`, facilitando o uso do ROUND em outras queries.

Considere selecionar as queries a serem executadas arrastando o mouse e usando o atalho de **Run Selected Query**, que no meu caso é o atalho `Ctrl + E Ctrl + E`. Caso você não consiga, é só apertar o botão direito do mouse e selecionar o comando indicado.

Finalizada a etapa de tipagem das colunas no SQL: você pode executar os arquivos na ordem que preferir, visto que as análises não tem uma ordem obrigatória.

### Opção B: pgAdmin

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
