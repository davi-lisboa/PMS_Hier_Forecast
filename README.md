# PMS_Hier_Forecast

Este projeto tem como objetivo realizar **Previsões Hierárquicas** para a **Pesquisa Mensal de Serviços (PMS)** do IBGE.

## 📁 Estrutura do Projeto

O fluxo de processamento e modelagem é dividido nos seguintes arquivos:

- `coleta.py`: Responsável por baixar os dados do índice PMS diretamente da API do SIDRA (IBGE) e ler a base de pesos.
- `tratamento.py`: Realiza a limpeza dos dados, padroniza os textos e reconstrói a estrutura hierárquica (Setor > Divisão > Grupo).
- `modelo.py`: Define o pipeline de previsão estendendo a biblioteca `sktime`, utilizando um *Ensemble* de modelos (ARIMA, ETS, CES, TBATS) junto com algoritmos de reconciliação hierárquica ótima.
- `run.py`: O script principal (orquestrador) que executa desde a coleta até a geração e exportação das projeções.
- `PMS Pesos Base 2022.xlsx`: Arquivo contendo os pesos dos componentes do índice.

## 🚀 Como Executar

1. Instale as dependências via `pip`:
```bash
pip install -r requirements.txt
```

2. Execute o orquestrador na raiz do projeto:
```bash
python run.py
```


