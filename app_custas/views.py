from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import EscolhaRecursoForm, ValorCausaForm
from .models import CUSTAS_CAUSAS_GERAL_TJBA, CUSTAS_RECURSO_INOMINADO_TJBA, CUSTAS_APELACAO_TJBA, FUNSEG_PERCENTUAL
import decimal # Para lidar com valores monetários

def get_taxa(valor, tabela_custas):
    """
    Função auxiliar para encontrar a taxa correspondente a um valor em uma tabela de custas.
    """
    for faixa in tabela_custas:
        if faixa["min_value"] <= valor <= faixa["max_value"]:
            return faixa["taxa"]
    return 0.0 # Retorna 0 se não encontrar a faixa (erro ou valor fora das tabelas)

def calcular_funseg(custas_judiciais):
    """Calcula o valor do FUNSEG e arredonda para 2 casas decimais."""
    funseg = custas_judiciais * decimal.Decimal(str(FUNSEG_PERCENTUAL))
    return funseg.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP)

def escolha_recurso_view(request):
    if request.method == 'POST':
        form = EscolhaRecursoForm(request.POST)
        if form.is_valid():
            tipo_recurso = form.cleaned_data['tipo_recurso']
            # Redireciona para a próxima etapa, passando o tipo de recurso
            return redirect(reverse('calcular_custas', args=[tipo_recurso]))
    else:
        form = EscolhaRecursoForm()
    return render(request, 'app_custas/escolha_recurso.html', {'form': form})

def calcular_custas_view(request, tipo_recurso):
    valor_total_preparo = decimal.Decimal('0.00')
    detalhes_calculo = []
    erro_msg = None

    if request.method == 'POST':
        form = ValorCausaForm(request.POST)
        if form.is_valid():
            valor_causa = form.cleaned_data['valor_causa']

            if tipo_recurso == 'inominado':
                # DAJE 1: Custas Processuais
                custas_processuais = decimal.Decimal(str(get_taxa(valor_causa, CUSTAS_CAUSAS_GERAL_TJBA)))
                funseg_processuais = calcular_funseg(custas_processuais)
                total_daje1 = custas_processuais + funseg_processuais
                valor_total_preparo += total_daje1
                detalhes_calculo.append({
                    'titulo': 'DAJE 1 - Custas Processuais (Causas em Geral)',
                    'custas_judiciais': custas_processuais,
                    'funseg': funseg_processuais,
                    'total': total_daje1
                })

                # DAJE 2: Taxa do Recurso Inominado
                custas_recurso_inominado = decimal.Decimal(str(get_taxa(valor_causa, CUSTAS_RECURSO_INOMINADO_TJBA)))
                funseg_recurso_inominado = calcular_funseg(custas_recurso_inominado)
                total_daje2 = custas_recurso_inominado + funseg_recurso_inominado
                valor_total_preparo += total_daje2
                detalhes_calculo.append({
                    'titulo': 'DAJE 2 - Taxa Recurso Inominado',
                    'custas_judiciais': custas_recurso_inominado,
                    'funseg': funseg_recurso_inominado,
                    'total': total_daje2
                })
            elif tipo_recurso == 'apelacao':
                # Taxa da Apelação
                custas_apelacao = decimal.Decimal(str(get_taxa(valor_causa, CUSTAS_APELACAO_TJBA)))
                funseg_apelacao = calcular_funseg(custas_apelacao)
                total_daje_apelacao = custas_apelacao + funseg_apelacao
                valor_total_preparo += total_daje_apelacao
                detalhes_calculo.append({
                    'titulo': 'Custas da Apelação (Taxa Recursal)',
                    'custas_judiciais': custas_apelacao,
                    'funseg': funseg_apelacao,
                    'total': total_daje_apelacao
                })
                # IMPORTANTE: Aqui poderiam ser adicionadas as custas iniciais se fosse o caso de não terem sido pagas,
                # mas para simplificar e focar na taxa recursal, consideramos que já foram.
                # Se necessário, adicionar lógica para custas iniciais (Item I da Tabela I)
                # com base na necessidade de verificar se já foram pagas.
            else:
                erro_msg = "Tipo de recurso inválido."

            # Redireciona para a página de resultados
            return render(request, 'app_custas/resultado_custas.html', {
                'tipo_recurso': tipo_recurso,
                'valor_causa': valor_causa,
                'detalhes_calculo': detalhes_calculo,
                'valor_total_preparo': valor_total_preparo,
                'erro_msg': erro_msg
            })

    else: # GET request
        form = ValorCausaForm()

    context = {
        'form': form,
        'tipo_recurso': tipo_recurso,
        'erro_msg': erro_msg
    }
    return render(request, 'app_custas/calcular_custas.html', context)
