from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils.timezone import now

from quiz.base.forms import AlunoForm
from quiz.base.models import Pergunta, Aluno, Resposta


# Create your views here.

def home(requisicao):
    if requisicao.method == 'POST':
        formulario = AlunoForm(requisicao.POST)
        # Usuário já existe
        email = requisicao.POST['email']

        try:
            aluno = Aluno.objects.get(email=email)
        except Aluno.DoesNotExist:
            # Usuário não existe
            if formulario.is_valid():
                aluno = formulario.save()
                requisicao.session['aluno_id'] = aluno.id
                return redirect('/perguntas/1')
            else:
                contexto = {'formulario': formulario}
                return render(requisicao, 'base/home.html', contexto)
        else:
            requisicao.session['aluno_id'] = aluno.id
            return redirect('/perguntas/1')

    return render(requisicao, 'base/home.html')


PONTUACAO_MAXIMA = 1000


def perguntas(requisicao, indice):
    try:
        aluno_id = requisicao.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:
        try:
            pergunta = Pergunta.objects.filter(disponivel=True).order_by('id')[indice - 1]
        except IndexError:
            return redirect('/classificacao')
        else:
            contexto = {'indice_da_questao': indice, 'pergunta': pergunta}

            if requisicao.method == 'POST':
                resposta_indice = int(requisicao.POST['resposta_indice'])

                if resposta_indice == pergunta.alternativa_correta:
                    # Armazenar dados da resposta
                    try:
                        data_da_primeira_resposta = \
                            Resposta.objects.filter(pergunta=pergunta).order_by('respondida_em')[0].respondida_em
                    except IndexError:
                        Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=PONTUACAO_MAXIMA).save()
                    else:
                        diferenca = now() - data_da_primeira_resposta
                        diferenca_em_segundos = int(diferenca.total_seconds())
                        pontos = max(PONTUACAO_MAXIMA - diferenca_em_segundos, 10)
                        Resposta(aluno_id=aluno_id, pergunta=pergunta, pontos=pontos).save()
                    return redirect(f'/perguntas/{indice + 1}')
                contexto['resposta_indice'] = resposta_indice
            return render(requisicao, 'base/perguntas.html', context=contexto)


def classificacao(requisicao):
    try:
        aluno_id = requisicao.session['aluno_id']
    except KeyError:
        return redirect('/')
    else:

        pontos_dct = Resposta.objects.filter(aluno_id=aluno_id).aggregate(Sum('pontos'))
        pontuacao_do_aluno = pontos_dct['pontos__sum']

        if pontuacao_do_aluno is None:
            pontuacao_do_aluno = 0

        numero_de_alunos_com_maior_pontuacao = Resposta.objects.values('aluno').annotate(Sum('pontos')).filter(
            pontos__sum__gt=pontuacao_do_aluno).count()

        if numero_de_alunos_com_maior_pontuacao is None:
            numero_de_alunos_com_maior_pontuacao = 0

        primeros_alunos_da_classificacao = list(Resposta.objects.values('aluno', 'aluno__nome').annotate(
            Sum('pontos')).order_by('-pontos__sum')[:5])

        context = {
            'pontuacao_do_aluno': pontuacao_do_aluno,
            'posicao_do_aluno': numero_de_alunos_com_maior_pontuacao + 1,
            'primeros_alunos_da_classificacao': primeros_alunos_da_classificacao,
            'length_alunos': len(primeros_alunos_da_classificacao)
        }

        return render(requisicao, 'base/classificacao.html', context)
