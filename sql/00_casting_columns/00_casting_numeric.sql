-- Convertendo as colunas para um tipo monetário
ALTER TABLE sales
    ALTER COLUMN price_per_unit TYPE NUMERIC(6,2) USING price_per_unit::numeric(6,2),
    ALTER COLUMN total_spent TYPE NUMERIC(8,2) USING total_spent::numeric(8,2);

-- Conferindo se as colunas foram convertidas corretamente
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'sales'
ORDER BY data_type ASC;