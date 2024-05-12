create database API;

use api;

  -- Cria a tabela Analises
CREATE TABLE Analises AS
SELECT
  rotas.ï»¿Emissao AS Emissao,
  rotas.Entrega,
  rotas.MÃªs AS Mes,
  rotas.Ano,
  rotas.CodFabrica,
  rotas.CodCliente,
  rotas.incoterm,
  rotas.veiculo,
  rotas.Qtdpallets,
  rotas.QtdTransp,
  rotas.VlrFrete,
  rotas.Dist,
  fabricas.MUN AS MunFabrica,
  fabricas.UF AS UFFabrica,
  clientes.MUN AS MunCliente,
  CASE
    WHEN rotas.veiculo = 'P24' THEN 3600
    WHEN rotas.veiculo = 'P12' THEN 1800
    ELSE NULL
  END AS Capacidade,
  ROUND((rotas.QtdTransp / 
    CASE
      WHEN rotas.veiculo = 'P24' THEN 3600
      WHEN rotas.veiculo = 'P12' THEN 1800
      ELSE 1 -- Evita divisão por zero
    END
  ) * 100, 2) AS Produtividade
FROM
  rotas
JOIN
  fabricas ON rotas.CodFabrica = fabricas.CodFabrica
JOIN
  clientes ON rotas.CodCliente = clientes.CodCliente;

use api;

SELECT * FROM api.analises;

select count(*) as total
from analises
where Incoterm = "FOB" and	VlrFrete >0;

SET SQL_SAFE_UPDATES = 0;

UPDATE analises
SET incoterm = 'CIF'
WHERE incoterm = 'FOB' AND VlrFrete > 0;

SET SQL_SAFE_UPDATES = 1;

select count(*) as total
from analises
where Incoterm = 'FOB';

select round(sum(QtdTransp), 2) as	Custo_Total
from analises;
  
 