import subprocess
import time
import json
import pandas as pd
import matplotlib.pyplot as plt

SERVER_URL = "https://server:443"
REPETICOES = 10

def rodar_teste(protocolo, endpoint):
    format_str = (
        '{"time_namelookup": %{time_namelookup}, '
        '"time_connect": %{time_connect}, '
        '"time_appconnect": %{time_appconnect}, '
        '"time_starttransfer": %{time_starttransfer}, '
        '"time_total": %{time_total}, '
        '"size_download": %{size_download}}'
    )
    
    cmd = [
        "curl", "-k", "-s", 
        f"--http{protocolo}", 
        "-w", format_str, 
        "-o", "/dev/null", 
        f"{SERVER_URL}{endpoint}"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    try:
        metrics = json.loads(result.stdout)
        metrics["protocolo"] = f"HTTP/{protocolo}"
        metrics["cenario"] = "Navegação" if endpoint == "/texto" else "Streaming"
        return metrics
    except Exception as e:
        print(f"Erro ao processar resultado do HTTP/{protocolo}: {result.stderr}")
        return None

resultados = []

print("A aguardar 3 segundos para o servidor iniciar completamente...")
time.sleep(3)

print("Iniciando testes...")
for i in range(REPETICOES):
    print(f"Rodada {i+1}/{REPETICOES}")
    resultados.append(rodar_teste("1.1", "/texto"))
    resultados.append(rodar_teste("3", "/texto"))
    resultados.append(rodar_teste("1.1", "/streaming"))
    resultados.append(rodar_teste("3", "/streaming"))
    time.sleep(0.2)

resultados = [r for r in resultados if r is not None]

df = pd.DataFrame(resultados)
df.to_csv("resultado_experimento.csv", index=False)
print("Resultados salvos em 'resultado_experimento.csv'")

df_grouped = df.groupby(["cenario", "protocolo"])["time_total"].mean().unstack()
ax = df_grouped.plot(kind="bar", figsize=(10, 6))
plt.title("Comparação de Tempo Total de Carregamento (Média)")
plt.ylabel("Tempo (segundos)")
plt.xlabel("Cenário")
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.savefig("grafico_desempenho.png")
print("Gráfico gerado com sucesso: 'grafico_desempenho.png'")