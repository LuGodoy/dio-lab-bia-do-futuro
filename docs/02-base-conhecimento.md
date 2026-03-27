# Base de Conhecimento

## Dados Utilizados

| Arquivo | Formato | Para que serve no Fia? |
|---------|---------|---------------------|
| `historico_atendimento.csv` | CSV | Contextualizar interações anteriores, ou seja, dar continuidade ao atendimento de forma mais eficiente. |
| `perfil_investidor.json` | JSON | Personalizar as explicações sobre as dúvidas e necessidades de aprendizado do cliente. |
| `produtos_financeiros.json` | JSON | Conhecer os produtos disponíveis para que eles possam ser ensinados ao cliente. |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente e usar essas informações de forma didática. |

---

## Estratégia de Integração

### Como os dados são carregados?

Os dados foram tranformados em texto e otimizados para economizar tokens.<br>
[Aqui o script de transformação](src/utils/transform_data.py)

### Como os dados são usados no prompt?

Os dados são "adicionados" no prompt, permintindo  que o Agente tenha o melhor contexto possível. 

<details>
  <summary>Clique para visualizar os Dados do DADOS DO CLIENTE E PERFIL (data/perfil_investidor.json):</summary>

  ```text
  {
    "nome": "João Silva",
    "idade": 32,
    "profissao": "Analista de Sistemas",
    "renda_mensal": 5000.00,
    "perfil_investidor": "moderado",
    "objetivo_principal": "Construir reserva de emergência",
    "patrimonio_total": 15000.00,
    "reserva_emergencia_atual": 10000.00,
    "aceita_risco": false,
    "metas": [
      {
        "meta": "Completar reserva de emergência",
        "valor_necessario": 15000.00,
        "prazo": "2026-06"
      },
      {
        "meta": "Entrada do apartamento",
        "valor_necessario": 50000.00,
        "prazo": "2027-12"
      }
    ]
  }
```
</details>

<details>
  <summary> Clique aqui para visualizar os Dados de TRANSACOES DO CLIENTE (data/transacoes.csv):</summary>

```text
data,descricao,categoria,valor,tipo
2025-10-01,Salário,receita,5000.00,entrada
2025-10-02,Aluguel,moradia,1200.00,saida
2025-10-03,Supermercado,alimentacao,450.00,saida
2025-10-05,Netflix,lazer,55.90,saida
2025-10-07,Farmácia,saude,89.00,saida
2025-10-10,Restaurante,alimentacao,120.00,saida
2025-10-12,Uber,transporte,45.00,saida
2025-10-15,Conta de Luz,moradia,180.00,saida
2025-10-20,Academia,saude,99.00,saida
2025-10-25,Combustível,transporte,250.00,saida
```
</details>

<details>
  <summary> Clique aqui para visualizar os Dados de HISTORICO DE ATENDIMENTO DO CLIENTE (data/historico_atendimento.csv):</summary>

```text
data,canal,tema,resumo,resolvido
2025-09-15,chat,CDB,Cliente perguntou sobre rentabilidade e prazos,sim
2025-09-22,telefone,Problema no app,Erro ao visualizar extrato foi corrigido,sim
2025-10-01,chat,Tesouro Selic,Cliente pediu explicação sobre o funcionamento do Tesouro Direto,sim
2025-10-12,chat,Metas financeiras,Cliente acompanhou o progresso da reserva de emergência,sim
2025-10-25,email,Atualização cadastral,Cliente atualizou e-mail e telefone,sim
```

</details>

<details>
  <summary>Clique para visualizar os Dados dos PRODUTOS DISPONIVEIS PARA ENSINO (data/produtos_financeiros.json):</summary>

  ```text
[
  {
    "nome": "Tesouro Selic",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "100% da Selic",
    "aporte_minimo": 30.00,
    "indicado_para": "Reserva de emergência e iniciantes"
  },
  {
    "nome": "CDB Liquidez Diária",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "102% do CDI",
    "aporte_minimo": 100.00,
    "indicado_para": "Quem busca segurança com rendimento diário"
  },
  {
    "nome": "LCI/LCA",
    "categoria": "renda_fixa",
    "risco": "baixo",
    "rentabilidade": "95% do CDI",
    "aporte_minimo": 1000.00,
    "indicado_para": "Quem pode esperar 90 dias (isento de IR)"
  },
  {
    "nome": "Fundo Imobiliário (FII)",
    "categoria": "fundo",
    "risco": "medio",
    "rentabilidade": "Dividend Yield (DY) costuma ficar entre 6% a 12% ao ano",
    "aporte_minimo": 100.00,
    "indicado_para": "Perfil moderado que busca diversificação e renda recorrente mensal"
  },
  {
    "nome": "Fundo de Ações",
    "categoria": "fundo",
    "risco": "alto",
    "rentabilidade": "Variável",
    "aporte_minimo": 100.00,
    "indicado_para": "Perfil arrojado com foco no longo prazo"
  }
]
```
</details>

---

### Exemplo de Contexto Montado

O contexto abaixo é uma versão sintetizada dos dados originais da base de conhecimento. Ele mantém apenas as informações mais relevantes, com o objetivo de otimizar o uso de tokens.

No entanto, mais importante do que economizar tokens é garantir que todas as informações essenciais estejam presentes, permitindo respostas mais precisas e contextualizadas.

```
DADOS DO CLIENTE:
- Nome: João Silva
- Perfil: Moderado
- Objetivo: Construir reserva de emergência
- Reserva atual: R$ 10.000 (meta: R$ 15.000)

RESUMO DE GASTOS:
- Moradia: R$ 1.380
- Alimentação: R$ 570
- Transporte: R$ 295
- Saúde: R$ 188
- Lazer: R$ 55,90
- Total de saídas: R$ 2.488,90

PRODUTOS DISPONÍVEIS PARA EXPLICAR:
- Tesouro Selic (risco baixo)
- CDB Liquidez Diária (risco baixo)
- LCI/LCA (risco baixo)
- Fundo Imobiliário - FII (risco médio)
- Fundo de Ações (risco alto)

HISTÓRICO RECENTE (Últimos 30 dias):
- CDB: Dúvida sobre rentabilidade sanada.
- APP: Erro de extrato corrigido.
- Tesouro Selic: Explicação enviada.
- Metas: Progresso da reserva de emergência consultado.
- Cadastro: E-mail e telefone atualizados.

```
