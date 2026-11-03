# Decisões de Limpeza

Registro das decisões tomadas no tratamento da base de vendas da cafeteria, com o motivo e o impacto de cada uma. O código está em [`notebooks/02_data_preparation.ipynb`](../notebooks/02_data_preparation.ipynb).

**Resultado:** a base bruta tinha 10.000 vendas, e a base limpa tem **9.974** (26 linhas removidas, cerca de 0.26%). O que não pôde ser recuperado por uma regra foi marcado como "Not Specified" ou mantido ausente. O arquivo final está em [clean_cafe_sales.parquet](../data/processed/clean_cafe_sales.parquet).

## Visão geral por coluna

Contagens de valores ausentes depois de `ERROR` e `UNKNOWN` virarem `NaN`.

| Coluna           | Ausentes | Tratamento                                                                    |
| :--------------- | -------: | :---------------------------------------------------------------------------- |
| item             |      969 | 489 itens recuperados pelo preço, o restante foi marcado com "Not Specified"  |
| quantity         |      479 | 456 quantidades recuperadas por `total_spent ÷ price_per_unit`                 |
| price_per_unit   |      533 | 479 preços unitários recuperados pelo item, e 48 por `total_spent ÷ quantity` |
| total_spent      |      502 | 479 preços totais recuperados por `quantity × price_per_unit`                 |
| payment_method   |    3.178 | 3.168 métodos de pagamento marcados como "Not Specified"                      |
| location         |    3.961 | 3.952 localizações marcadas como "Not Specified"                              |
| transaction_date |      460 | 460 datas de transação mantidas como ausente (`NaT`)                          |

Foram descartadas 26 linhas, por não ser possível recuperar usando regras de tratamento envolvendo `quantity`, `price_per_unit` e `total_spent`.

## Decisões

### 1. `ERROR` e `UNKNOWN` viram `NaN`

- **Problema:** a base usa três formas de dizer que o valor falta: vazio, `ERROR` e `UNKNOWN`. No total: 10.082 de 80.000 células, cerca de 12.6% estavam sujas, e só 30.89% das linhas não tinham nenhuma coluna suja.
- **Decisão:** converter `ERROR` e `UNKNOWN` para `NaN`, com uma máscara construída por [dirty_mask](../src/quality.py), e conferir por `assert` que nenhum valor sujo sobrou.
- **Motivo:** os três casos significam a mesma coisa: valor ausente ou inválido. Com um único representante, o resto do tratamento fica simples.
- **Verificação adicional:** em `location` e `payment_method`, o `NaN` é de 8 a 10 vezes mais frequente que `ERROR` ou `UNKNOWN`. Nas outras colunas, os três tipos têm peso parecido.

### 2. Tipos e nomes das colunas

- **Decisão:** nomes das colunas no padrão _snake_case_. Quanto aos tipos, optei por: `item`, `payment_method` e `location` como category, `quantity` como Int64, `price_per_unit` e `total_spent` como float64, `transaction_date` como datetime e `transaction_id` como str.
- **Motivo:** o tipo certo evita erros de cálculo e economiza memória. `Int64` aceita `NaN` na quantidade, o que `int64` não faz. A conversão tem um `assert` comprovando que não foi criado `NaN` a mais.
- **Valores monetários no SQL**: Converti colunas que envolve moedas para o tipo NUMERIC do PostgreSQL, facilitando o arredondamento dos valores. É possível verificar o DDL em [casting_numeric.sql](../sql/00_casting_columns/00_casting_numeric.sql).

### 3. Duplicatas

- **Problema:** 255 linhas se repetem quando o ID é ignorado.
- **Decisão:** nenhuma ação.
- **Motivo:** os `transaction_id` são únicos, então cada linha é uma venda distinta. Duas vendas com o mesmo item, quantidade, valor, pagamento, local e data podem acontecer de verdade.

### 4. Recuperação de valores por regra

- **Regra:** `quantity × price_per_unit = total_spent`. Foi validada nas 8.544 linhas em que as três colunas estavam preenchidas, sem nenhuma divergência.
- **Tabela item → preço:** cada item tem um único preço: Cookie $1.00, Tea $1.50, Coffee $2.00, Cake e Juice $3.00, Sandwich e Smoothie $4.00, Salad $5.00. Foi construída a partir dos próprios dados, com um `assert` de que nenhum item tem dois preços.
- **Ordem aplicada:** preço pelo item, preço por `total_spent ÷ quantity`, item pelo preço, quantidade por `total_spent ÷ price_per_unit` e total por `quantity × price_per_unit`. Cada etapa produz o que a seguinte usa.
- **Item pelo preço:** só os preços $1.00, $1.50, $2.00 e $5.00 apontam para um único item. Os preços $3.00, com Cake ou Juice e $4.00, com Sandwich ou Smoothie são ambíguos, então esses itens não são recuperados.
- **Regra:** todas as recuperações são matemáticas sobre valores que já existiam.

### 5. Categoria `Not Specified` em `item`, `payment_method` e `location`

- **Problema:** nenhuma regra recupera esses valores.
- **Alternativa considerada:** imputar pela moda, mas nenhum valor tem uma vantagem clara como mais frequente.
- **Decisão:** preencher com a categoria `Not Specified`, o mesmo texto nas três colunas, para o SQL filtrar do mesmo jeito.
- **Motivo:** não inventa dado, mantém as linhas e deixa visível, em cada análise, a parcela sem informação. O nome evita `Unknown`, que seria confundido com o `UNKNOWN` original da base.
- **Impacto:** nas perguntas por canal e por pagamento, as comparações usam só as vendas com a informação.

### 6. `transaction_date` mantida ausente

- **Problema:** 460 vendas sem data, cerca de 4.6%. A data é `datetime`, e uma categoria como `Not Specified` não se aplica.
- **Alternativas consideradas:** descartar as linhas, preencher com moda, copiar a data da linha vizinha, interpolar ou sortear. Mas a base de dados não tem uma ordem cronológica, e não tem uma vantagem clara de valor mais frequente para usar a moda.
- **Decisão:** manter as linhas com `NaT`.
- **Motivo:** descartar tiraria 4.7% do faturamento das perguntas que não dependem da data. Preencher criaria datas que não existem. Como as vendas sem data são parecidas com as demais, manter não enviesa os resultados.
- **Impacto:** a coluna é a única da base final que aceita `NULL`. As perguntas por período filtram essas linhas.

### 7. Descarte das linhas sem solução numérica

- **Problema:** as linhas com duas das três colunas numéricas ausentes têm duas incógnitas e uma equação.
- **Decisão:** descartar essas linhas, depois de todas as recuperações.
- **Impacto:** 26 linhas, cerca de 0.26% da base.

### 8. Feature engineering

- **Decisão:** criar `month`, `quarter` e `weekday` a partir de `transaction_date`. O dia da semana é o nome em inglês.
- **Motivo:** as perguntas por período ficam mais simples em SQL com as colunas prontas.

### 9. Formato de saída

- **Decisão:** salvar em Parquet, e carregar no PostgreSQL.
- **Motivo:** o Parquet preserva os tipos (`category`, `Int64`, `datetime`), o que o CSV não faz.

## Validação final

O notebook termina com `assert` para as regras que a limpeza promete:

- O único ausente na base é `transaction_date`.
- Os `transaction_id` são únicos.
- A relação `quantity × price_per_unit = total_spent` vale em todas as linhas.
