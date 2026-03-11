---
description: Diretrizes de Desenvolvimento e Forecasting para o PMS_Hier_Forecast
---

Este arquivo serve como **contexto principal** para o agente de IA que atua no projeto de previsão hierárquica do IBGE. Estas diretrizes DEVEM ser seguidas rigorosamente em cada iteração para garantir um código sustentável, seguro e eficaz.

## 1. Contexto do Projeto e Forecasting
- **Domínio**: Previsão de séries temporais das pesquisas do IBGE, especificamente a Pesquisa Mensal de Serviços (PMS).
- **Abordagem Hierárquica**: Os dados contêm restrições hierárquicas (Setor > Divisão > Grupo). Toda abordagem de previsão deve respeitar essas restrições (ex: reconciliação *Optimal*, *Top-Down*, etc.).
- **Mentalidade de Forecasting**:
  - Evite estritamente o vazamento de dados (data leakage), respeitando rigorosamente a ordem temporal.
  - Implemente e utilize métricas válidas para séries temporais.
  - Teste a estabilidade do modelo e da reconciliação com validações robustas (ex: Backtesting, Cross-Validation contínuo no tempo).

## 2. Padrões de Código e Boas Práticas
- **Simplicidade e Limpeza**: Escreva códigos legíveis, claros, e sem overengineering (KISS). Funções devem ter um único propósito bem definido.
- **Tipagem**: Utilize hints de tipagem (Type Hints) rigorosos em todas as novas funções (`def func(x: int) -> str:`).
- **Sem Magia**: Prefira código explícito a implícito.
- **Minimização de Retrabalho**: Revise sempre as implementações pré-existentes. Não recrie funções ou fluxos (como extração e tratamento) sem uma justificativa robusta.

## 3. Ambiente de Execução (`pms_fc`)
- **Ambiente Obrigatório**: ABSOLUTAMENTE TUDO (scripts, notebooks, testes, instalações de bibliotecas via pip) deve ser rodado **exclusivamente no ambiente conda `pms_fc`**.
- Sempre certifique-se de que o ambiente `pms_fc` está ativo ao sugerir comandos.
- Exemplo: Antes de rodar python, execute `conda activate pms_fc` se necessário.

## 4. Comunicação e Alteração de Arquivos
- **Aprovação Obrigatória**: NUNCA modifique ou reescreva arquivos sem **pedir permissão explícita** com antecedência.
- Ao sugerir alterações, detalhe com clareza a mudança e pergunte proativamente: "Você me permite fazer essa modificação no arquivo `arquivo.py`?"
- Descreva detalhadamente o motivo da refatoração/implementação.
- Proponha as ideias antes de sair disparando o código, permitindo que o usuário guie o refinamento do design.
