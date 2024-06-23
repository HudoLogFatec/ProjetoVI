import pandas as pd
import pulp
import locale

# Definindo o formato de número desejado
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Leitura do arquivo CSV
file_path = 'C:/Users/carva/OneDrive/Área de Trabalho/API 6/Sprint 1/Analises.csv'
df = pd.read_csv(file_path, delimiter=';', decimal=',')

# Converter colunas relevantes para o tipo numérico
cols_to_convert = ['QtdTransp', 'VlrFrete']
df[cols_to_convert] = df[cols_to_convert].apply(pd.to_numeric)

# Filtrar os dados pelo incoterm CIF
df_cif = df[df['incoterm'] == 'CIF']

# Agrupar os dados por CodFabrica e CodCliente e calcular a soma de QtdTransp e VlrFrete
grouped = df_cif.groupby(['CodFabrica', 'CodCliente']).agg({'QtdTransp': 'sum', 'VlrFrete': 'sum'}).reset_index()

# Calcular o custo médio por unidade transportada
grouped['Custo Médio por Unidade'] = grouped['VlrFrete'] / grouped['QtdTransp']

# Dados de capacidade anual das fábricas
capacidades = {
    3403208: 37125900,
    3423909: 31458000,
    3424402: 46027500
}

# Dados de demanda anual dos clientes
demandas = {
    2301: 2797800, 2302: 1836600, 2303: 1274700, 2304: 2439900, 2305: 5714100, 2306: 2725500,
    2307: 2887500, 2308: 3846300, 2309: 7242300, 2310: 4028400, 2311: 6508200, 2312: 1214700,
    2313: 9900, 2314: 37200, 2315: 1094100, 2316: 939300, 2317: 19200, 2318: 1474200,
    2319: 2050200, 2320: 26400, 2321: 24000, 2322: 2151000, 2323: 18900, 2324: 1571700,
    2325: 35100, 2326: 4980600, 2327: 1449300, 2328: 5429400, 2329: 1661400, 2330: 1392300,
    2331: 5148000, 2332: 59700, 2333: 24900, 2334: 3387900, 2335: 3957000, 2336: 1605300,
    2337: 2821500, 2338: 2232600, 2339: 41400, 2340: 3410700, 2341: 2381100, 2342: 2795100,
    2343: 3715200, 2344: 2419500, 2345: 2129100, 2346: 38100, 2347: 4104300, 2348: 3446400,
    2349: 37200, 2350: 3924900, 2351: 51300
}

# Definir as fábricas que podem entregar para cada cliente
fabrica_clientes = {
    3403208: [2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2312, 2313, 2314, 2315, 2316, 2317, 2318, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2339, 2340, 2341, 2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351],
    3423909: [2305, 2308, 2309, 2310, 2311, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341, 2342, 2343, 2347, 2348, 2349, 2350, 2351],
    3424402: [2301, 2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311, 2319, 2320, 2321, 2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331, 2332, 2333, 2334, 2335, 2336, 2337, 2338, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351]
}

# Formatação dos dados para o problema de otimização
costs = {}
original_transp = {}
for i, row in grouped.iterrows():
    factory = row['CodFabrica']
    client = row['CodCliente']
    if factory in fabrica_clientes and client in fabrica_clientes[factory]:
        costs[(factory, client)] = locale.format_string('%.17f', row['Custo Médio por Unidade'], grouping=True)
        original_transp[(factory, client)] = row['QtdTransp']

# Definição do problema de otimização
prob = pulp.LpProblem("Minimizacao_Custo_Transporte", pulp.LpMinimize)

# Variáveis de decisão
transp_vars = pulp.LpVariable.dicts("Transp", costs.keys(), lowBound=0, cat='Continuous')

# Função objetivo
prob += pulp.lpSum([locale.atof(costs[(f, c)]) * transp_vars[(f, c)] for (f, c) in costs]), "Custo_Total_Transporte"

# Restrições de capacidade das fábricas
for f in capacidades:
    prob += pulp.lpSum([transp_vars[(f, c)] for c in demandas if (f, c) in costs]) <= capacidades[f], f"Capacidade_{f}"

# Restrições de demanda dos clientes
for c in demandas:
    prob += pulp.lpSum([transp_vars[(f, c)] for f in capacidades if (f, c) in costs]) == demandas[c], f"Demanda_{c}"

# Resolver o problema
prob.solve()

# Verificar o status da solução
status = pulp.LpStatus[prob.status]
print(f"Status da solução: {status}")

if status == 'Optimal':
    print("A solução encontrada é ótima.")
else:
    print("A solução encontrada não é ótima. Status:", status)

# Preparação dos resultados
results = []
for (f, c) in costs:
    qtd_transp = original_transp[(f, c)]
    qtd_transp_otimizada = pulp.value(transp_vars[(f, c)])
    custo_medio_unidade = locale.atof(costs[(f, c)])
    custo_total = qtd_transp * custo_medio_unidade
    custo_total_otimizado = qtd_transp_otimizada * custo_medio_unidade
    results.append([str(int(f)), str(int(c)), locale.format_string('%.17f', qtd_transp, grouping=True), locale.format_string('%.17f', custo_medio_unidade, grouping=True), locale.format_string('%.17f', custo_total, grouping=True), locale.format_string('%.17f', qtd_transp_otimizada, grouping=True), locale.format_string('%.17f', custo_total_otimizado, grouping=True)])

# Criação do DataFrame de resultados
result_df = pd.DataFrame(results, columns=['CodFabrica', 'CodCliente', 'QtdTranspCIF', 'Custo por Unidade', 'Custo Total', 'QtdTransp Otimizada', 'Custo Total Otimizado'])

# Exibir os resultados
print(result_df)

# Salvar os resultados em um arquivo CSV na pasta especificada
output_path = 'C:/Users/carva/OneDrive/Área de Trabalho/API 6/Sprint 3/Resultados_Otimizacao_2023.csv'
result_df.to_csv(output_path, index=False)