from django.shortcuts import render

from quiz.base.models import Pergunta


# Create your views here.

def home(requisicao):
    return render(requisicao, 'base/home.html')


def perguntas(requisicao, indice):
    pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
    contexto = {'indice_da_questao': indice, 'pergunta': pergunta}
    return render(requisicao, 'base/perguntas.html', context=contexto)


def classificacao(requisicao):
    return render(requisicao, 'base/classificacao.html')
