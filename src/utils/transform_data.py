import os
import csv
import json
import logging

# ============ LOGGER ============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============ CLASSE ============
class DataOptimizer:
    def __init__(self, pasta_origem, pasta_destino):
        self.origem = pasta_origem
        self.destino = pasta_destino

        if not os.path.exists(self.destino):
            os.makedirs(self.destino)

    # 🔹 estimativa simples de tokens
    def estimar_tokens(self, texto):
        return len(texto) // 4

    # 🔹 manter data padrão ISO (melhor pro modelo)
    def _limpar_data(self, data_str):
        return data_str  # mantém "2025-10-02"

    # 🔹 formatação BR
    def _formatar_real(self, valor):
        try:
            valor = float(valor)
            return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except:
            return valor

    # ================= TRANSAÇÕES =================
    def processar_transacoes(self, linha):
        try:
            valor = float(linha['valor(R$)'])
        except:
            valor = 0.0

        return {
            "data": linha['data'],  # ISO: melhor para IA
            "descricao": linha['descricao'],
            "categoria": linha['categoria'].strip().lower(),
            "valor": valor,  # número → cálculo
            "valor_formatado": f"R$ {self._formatar_real(valor)}",  # exibição
            "tipo": linha['tipo'].strip().lower()
        }

    # ================= ATENDIMENTO =================
    def processar_atendimento(self, linha):
        return {
            "data": linha['data'],
            "canal": linha['canal'],
            "tema": linha['tema'],
            "status": linha.get('resolvido', 'U')[0].upper() if linha.get('resolvido') else 'U'
        }

    # ================= CONVERSÃO =================
    def converter(self):
        total_tokens_geral = 0
        arquivos_processados = 0

        for arquivo in os.listdir(self.origem):
            caminho_in = os.path.join(self.origem, arquivo)

            if os.path.isdir(caminho_in):
                continue

            conteudo_saida = None

            # 🔹 JSON → compactar
            if arquivo.endswith('.json'):
                with open(caminho_in, 'r', encoding='utf-8') as f:
                    dados = json.load(f)

                conteudo_saida = json.dumps(
                    dados,
                    separators=(',', ':'),
                    ensure_ascii=False
                )

            # 🔹 CSV → JSON estruturado
            elif arquivo.endswith('.csv'):
                dados_lista = []

                with open(caminho_in, 'r', encoding='utf-8') as f:
                    leitor = csv.DictReader(f)

                    for linha in leitor:
                        if 'transacoes' in arquivo:
                            dados_lista.append(self.processar_transacoes(linha))

                        elif 'atendimento' in arquivo:
                            dados_lista.append(self.processar_atendimento(linha))

                if dados_lista:
                    conteudo_saida = json.dumps(
                        dados_lista,
                        separators=(',', ':'),
                        ensure_ascii=False
                    )

            # 🔹 salvar
            if conteudo_saida:
                tokens = self.estimar_tokens(conteudo_saida)
                total_tokens_geral += tokens
                arquivos_processados += 1

                logger.info(f"✅ {arquivo.upper()}: {len(conteudo_saida)} chars | ~{tokens} tokens")

                nome_saida = os.path.splitext(arquivo)[0] + ".txt"

                with open(os.path.join(self.destino, nome_saida), 'w', encoding='utf-8') as f_out:
                    f_out.write(conteudo_saida)

        logger.info(f"🚀 FIM: {arquivos_processados} arquivos otimizados. Total ~{total_tokens_geral} tokens")


# ============ EXECUÇÃO ============
if __name__ == "__main__":
    optimizer = DataOptimizer(
        pasta_origem='./data/data_csv_json',
        pasta_destino='./data/txt_otimizado'
    )
    optimizer.converter()