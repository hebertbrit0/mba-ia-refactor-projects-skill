from flask import jsonify

from models import pedido_model

DESCONTOS = (
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
)


def _desconto(faturamento):
    for limite, taxa in DESCONTOS:
        if faturamento > limite:
            return faturamento * taxa
    return 0


def relatorio_vendas():
    resumo = pedido_model.resumo_vendas()
    faturamento = resumo["faturamento"] or 0
    desconto = _desconto(faturamento)
    total_pedidos = resumo["total_pedidos"]
    relatorio = {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": resumo["pendentes"],
        "pedidos_aprovados": resumo["aprovados"],
        "pedidos_cancelados": resumo["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
    return jsonify({"dados": relatorio, "sucesso": True}), 200
