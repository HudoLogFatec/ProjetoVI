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