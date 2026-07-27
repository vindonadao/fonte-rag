"""Gera o corpus de EXEMPLO (dados 100% fictícios) para a demo pública.

    ./.venv/bin/python scripts/gen_sample_corpus.py

Cria PDFs em sample_docs/ espelhando a estrutura de um contrato/proposta reais,
mas com empresa fictícia (Aurora Comércio Ltda) e valores redondos - assim a demo
roda igual sem expor nenhum documento de cliente.
"""
from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parent.parent / "sample_docs"
OUT.mkdir(exist_ok=True)


def _cell(pdf, h, text):
    pdf.multi_cell(0, h, text, new_x="LMARGIN", new_y="NEXT")


def pdf_de(titulo: str, blocos: list[str], arquivo: str):
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(120)
    _cell(pdf, 5, "Donadao Labs | AI Software Lab | donadaolabs.com")
    pdf.ln(2)
    pdf.set_text_color(0)
    pdf.set_font("Helvetica", "B", 15)
    _cell(pdf, 8, titulo)
    pdf.ln(3)
    for b in blocos:
        primeira, *resto = b.split("\n")
        pdf.set_font("Helvetica", "B", 11)
        _cell(pdf, 6, primeira)
        if resto:
            pdf.set_font("Helvetica", "", 11)
            _cell(pdf, 6, "\n".join(resto))
        pdf.ln(2)
    pdf.output(str(OUT / arquivo))
    print("gerado:", arquivo)


CONTRATO = [
    "QUALIFICACAO DAS PARTES\n"
    "CONTRATADA: Donadao Labs (Vinicius Donadao). CONTRATANTE: Aurora Comercio Ltda "
    "(empresa ficticia de exemplo), CNPJ 12.345.678/0001-99, Rua das Flores, 100 - Centro, "
    "Cidade Exemplo/SP. Celebrado em 01/03/2026. Contrato no CT-EXEMPLO-001.",

    "CLAUSULA I - OBJETO\n"
    "Desenvolvimento de site institucional e catalogo digital em codigo proprio (Next.js, "
    "sem template), com apresentacao das marcas, catalogo de produtos, formulario de contato "
    "com triagem de leads e otimizacao tecnica para mecanismos de busca (SEO tecnico e local).",

    "CLAUSULA II - PRAZO\n"
    "O prazo-alvo de entrega para o go-live e de 15 (quinze) dias corridos a partir do inicio.",

    "CLAUSULA III - INVESTIMENTO E PAGAMENTO\n"
    "O valor total dos servicos e de R$ 10.000,00, pago no modelo 30/60/10:\n"
    "- Taxa de Adjudicacao (30%): R$ 3.000,00, paga na assinatura.\n"
    "- Entrega parcial (60%): R$ 6.000,00, quando o produto esta pronto para revisao.\n"
    "- Go-live (10%): R$ 1.000,00, antes da implantacao no dominio do cliente.\n"
    "Paragrafo 1: A Taxa de Adjudicacao e nao reembolsavel em qualquer hipotese, pois cobre "
    "a reserva de slot na agenda da Contratada e custos de ferramentas ja incorridos.\n"
    "Paragrafo 2: Formas de pagamento aceitas: PIX e transferencia bancaria.\n"
    "Paragrafo 3: O atraso no pagamento de qualquer parcela sujeita a Contratante a multa de "
    "2% sobre o valor devido, juros de mora de 1% ao mes e correcao pelo IPCA, pro rata die.",

    "CLAUSULA IV - MANUTENCAO MENSAL\n"
    "A manutencao mensal e servico a parte, de contratacao facultativa, no valor de R$ 400,00 "
    "por mes. Horas avulsas fora do escopo sao cobradas a R$ 150,00 por hora. A nao contratacao "
    "da manutencao nao afeta a entrega nem a garantia do projeto.",

    "CLAUSULA V - POSICIONAMENTO EM BUSCA (SEO)\n"
    "A Contratada garante que o site sera indexado pelo Google e apto a aparecer nos resultados "
    "para o nome da marca e os termos trabalhados. NAO garante a posicao (ranking), definida "
    "pelos algoritmos do buscador. O servico e obrigacao de meio (executar e otimizar) e nao "
    "de resultado (atingir determinada colocacao).",

    "CLAUSULA VI - GARANTIA\n"
    "A Contratada corrige, sem custo, defeitos (bugs) do produto entregue em desconformidade "
    "com o escopo, pelo prazo de 90 (noventa) dias contados do go-live. Nos 15 dias seguintes "
    "ao go-live, realiza tambem, sem custo, pequenos ajustes cosmeticos (imagens, textos, cor "
    "e espacamento), excluidas novas funcionalidades ou mudanca de layout ja aprovado.",

    "CLAUSULA VII - PROPRIEDADE INTELECTUAL\n"
    "Apos a quitacao integral do valor contratado, a propriedade intelectual do codigo-fonte e "
    "dos ativos entregues e transferida a Contratante.",

    "CLAUSULA VIII - FORO\n"
    "As partes elegem o foro da comarca de Santos, estado de SP, para dirimir duvidas ou litigios "
    "decorrentes deste contrato, nos termos do Codigo Civil Brasileiro (Lei no 10.406/2002). "
    "O contrato e assinado eletronicamente por ClickSign, com validade juridica pela MP 2.200-2/2001.",
]

PROPOSTA = [
    "PROPOSTA COMERCIAL - Presenca Digital\n"
    "Para Aurora Comercio Ltda (exemplo ficticio). Proposta no DL-EXEMPLO-002. "
    "Emissao 20/02/2026, valida ate 06/03/2026.",

    "01 - O QUE VAMOS FAZER\n"
    "Site institucional e catalogo digital que coloca a Aurora na frente de quem procura os "
    "produtos dela na regiao, com captacao de leads pelo WhatsApp e base tecnica pronta para SEO.",

    "02 - ESCOPO\n"
    "- Site institucional em codigo proprio (Next.js).\n"
    "- Catalogo de produtos com paginas por marca.\n"
    "- Formulario de contato com triagem de leads.\n"
    "- SEO tecnico e busca local.\n"
    "Nao inclui: gestao de midia paga, cadastro exaustivo de todos os SKUs, producao de fotos.",

    "03 - INVESTIMENTO\n"
    "Investimento total de R$ 10.000,00, no modelo 30/60/10 (Taxa de Adjudicacao de R$ 3.000,00 "
    "na assinatura, R$ 6.000,00 na entrega parcial e R$ 1.000,00 no go-live). Manutencao mensal "
    "opcional de R$ 400,00.",

    "04 - GARANTIAS\n"
    "Garantimos a execucao tecnica e a indexacao do site. Resultado de ranking e obrigacao de "
    "meio, nao de resultado - a posicao final depende do algoritmo do buscador e da concorrencia.",

    "05 - PROXIMOS PASSOS\n"
    "Aprovacao da proposta por e-mail ou WhatsApp, pagamento da Taxa de Adjudicacao via PIX e "
    "inicio da fase de Diagnose. Entrega-alvo em 15 dias uteis.",
]

TERMO = [
    "TERMO DE ENTREGA - Conclusao e Transferencia de Titularidade\n"
    "Documento no TE-EXEMPLO-001, referente ao Contrato CT-EXEMPLO-001. Go-live em "
    "15/03/2026, emissao em 16/03/2026. Cliente: Aurora Comercio Ltda (exemplo ficticio).",

    "01 - OBJETO\n"
    "Este termo formaliza a conclusao e entrega do projeto e registra a titularidade e a "
    "localizacao de cada ativo digital que compoe a solucao entregue.",

    "02 - O QUE FOI ENTREGUE\n"
    "Site institucional e catalogo digital em codigo proprio (Next.js), no ar e indexado em "
    "auroracomercio.com.br desde 15/03/2026, com 8 marcas representadas, home institucional, "
    "paginas por marca e formulario de captacao de leads pelo WhatsApp.",

    "03 - INVENTARIO DE ATIVOS E TITULARIDADE\n"
    "Dominio auroracomercio.com.br: registrado na conta da Contratante. Banco de dados: "
    "Supabase, em conta propria da Contratante. Hospedagem: Vercel, em conta da Contratante, "
    "operada tecnicamente pela Donadao Labs como colaboradora. Codigo-fonte: propriedade "
    "intelectual da Contratante (contrato quitado). Todos os ativos sao de titularidade da "
    "Contratante.",

    "04 - PROPRIEDADE INTELECTUAL\n"
    "O valor contratado foi integralmente quitado. Nos termos da Clausula VII do contrato, a "
    "propriedade intelectual do codigo-fonte e dos ativos foi transferida a Contratante.",

    "05 - MANUTENCAO E GARANTIA\n"
    "Manutencao mensal de R$ 400,00 (facultativa), com teto de 2h/mes para ajustes de conteudo; "
    "horas avulsas a R$ 150,00/h. Garantia de correcao de bugs sem custo por 90 dias a partir do "
    "go-live; ajuste fino cosmetico sem custo nos 15 dias seguintes.",
]

pdf_de("CONTRATO - Prestacao de Servicos de Desenvolvimento de Software",
       CONTRATO, "CONTRATO-EXEMPLO-001.pdf")
pdf_de("PROPOSTA COMERCIAL - Presenca Digital",
       PROPOSTA, "PROPOSTA-EXEMPLO-002.pdf")
pdf_de("TERMO DE ENTREGA - Titularidade dos Ativos",
       TERMO, "TERMO-EXEMPLO-003.pdf")
print("OK - corpus de exemplo em sample_docs/")
