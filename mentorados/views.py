from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .models import Mentorados, Navigators, DisponibilidadeHorarios, Reuniao, Tarefa, Upload
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from .auth import valida_token
from django.db.models.functions import TruncDate
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


@login_required
def mentorados(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'GET':
        navigators = Navigators.objects.filter(user=request.user)
        mentorados = Mentorados.objects.filter(user=request.user)
        
        estagios_flat = [estagio[1] for estagio in Mentorados.estagio_choices]
        qtd_estagios = []
        
        for estagio in Mentorados.estagio_choices:
            count = Mentorados.objects.filter(estagio=estagio[0], user=request.user).count()
            qtd_estagios.append(count)

        return render(request, 'mentorados.html', {
            'estagios': Mentorados.estagio_choices, 
            'navigators': navigators, 
            'mentorados': mentorados, 
            'estagios_flat': estagios_flat, 
            'qtd_estagios': qtd_estagios
        })
    
    elif request.method == 'POST':
        nome = request.POST.get('nome')
        foto = request.FILES.get('foto')
        estagio = request.POST.get("estagio")
        navigator = request.POST.get('navigator')

        mentorado = Mentorados(
            nome=nome,
            foto=foto,
            estagio=estagio,
            navigator_id=navigator,
            user=request.user
        )

        mentorado.save()

        messages.add_message(request, constants.SUCCESS, 'Mentorado cadastrado com sucesso.')
        return redirect('mentorados')
    
def reunioes(request):
    if request.method == 'GET':
        reunioes = Reuniao.objects.filter(data__mentor=request.user)
        return render(request, 'reunioes.html',{'reunioes': reunioes})
    elif request.method == 'POST':
        data_str = request.POST.get('data')
        try:
            data = datetime.strptime(data_str, '%Y-%m-%dT%H:%M')
            
            disponibilidades = DisponibilidadeHorarios.objects.filter(mentor=request.user).filter(
                data_inicial__gte=(data - timedelta(minutes=50)),
                data_inicial__lte=(data + timedelta(minutes=50))
            )

            if disponibilidades.exists():
                messages.add_message(request, constants.ERROR, 'Você já possui uma reunião em aberto nesse horário.')
                return redirect('reunioes')

            disponibilidade = DisponibilidadeHorarios(
                data_inicial=data,
                mentor=request.user
            )
            disponibilidade.save()

            messages.add_message(request, constants.SUCCESS, 'Horário disponibilizado com sucesso!')
            
            return redirect('reunioes')
        except ValueError as e:
            return HttpResponse(f"Erro no formato da data: {e}", status=400)

def auth(request):
    if request.method == 'GET':
        return render(request, 'auth_mentorado.html')
    elif request.method == 'POST':
        token = request.POST.get('token')

        if not Mentorados.objects.filter(token=token).exists():
            messages.add_message(request, constants.ERROR, 'Token inválido')
            return redirect('auth_mentorado')

        response = redirect('escolher_dia')
        response.set_cookie('auth_token', token, max_age=3600)

        return response
        

def escolher_dia(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')

    if request.method == 'GET':
        mentorado = valida_token(request.COOKIES.get('auth_token'))
        
        disponibilidades = DisponibilidadeHorarios.objects.filter(
            data_inicial__gte=datetime.now(),
            agendado=False,
            mentor=mentorado.user
        ).annotate(
            data_agrupada=TruncDate('data_inicial')
        ).order_by('data_agrupada')
        
        # Filtra dias únicos manualmente
        dias_unicos = {}
        for disp in disponibilidades:
            data_str = disp.data_inicial.strftime('%Y-%m-%d')
            if data_str not in dias_unicos:
                dias_unicos[data_str] = disp
        
        return render(request, 'escolher_dia.html', {
            'horarios': dias_unicos.values(),  # Apenas um horário por dia
            'datas_formatadas': [d.data_inicial.strftime('%d-%m-%Y') for d in dias_unicos.values()]
        })


def agendar_reuniao(request):
    if not valida_token(request.COOKIES.get('auth_token')):
        return redirect('auth_mentorado')
    valida_token(request.COOKIES.get('auth_token'))
    if request.method == 'GET':
        data = request.GET.get("data")
        data = datetime.strptime(data, '%d-%m-%Y')

        horarios = DisponibilidadeHorarios.objects.filter(
        data_inicial__gte=data,
        data_inicial__lt=data + timedelta(days=1),
        agendado=False,
        )

        return render(request, 'agendar_reuniao.html', {'horarios': horarios, 'tags': Reuniao.tag_choices})
    
    else:
        horario_id = request.POST.get('horario')
        tag = request.POST.get('tag')
        descricao = request.POST.get('descricao')

    mentorado = valida_token(request.COOKIES.get('auth_token'))

    try:
        horario = DisponibilidadeHorarios.objects.get(id=horario_id)
    except DisponibilidadeHorarios.DoesNotExist:
        messages.error(request, "Horário inválido.")
        return redirect('escolher_dia')

    # Validação: o mentor do horário deve ser o mesmo usuário do mentorado
    if horario.mentor != mentorado.user:
        messages.error(request, "Este horário não pertence ao seu mentor.")
        return redirect('escolher_dia')

    #Criação da reunião
    reuniao = Reuniao(
        data=horario,
        mentorado=mentorado,
        tag=tag,
        descricao=descricao
    )
    reuniao.save()

    horario.agendado = True
    horario.save()

    messages.add_message(request, constants.SUCCESS, 'Reunião agendada com sucesso!')
    return redirect('escolher_dia')


def tarefa(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()

    if request.method == 'GET':
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        videos = Upload.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa.html', {'mentorado': mentorado, 'tarefas': tarefas, 'videos': videos})
    else:
        tarefa_texto = request.POST.get('tarefa')
        
        if not tarefa_texto:
            messages.error(request, "O campo tarefa não pode estar vazio")
            return redirect(f'/mentorados/tarefa/{id}')
            
        tarefa = Tarefa(
            mentorado=mentorado,
            tarefa=tarefa_texto
        )
        tarefa.save()
        messages.success(request, "Tarefa adicionada com sucesso!")
        return redirect(f'/mentorados/tarefa/{id}')

def upload(request, id):
    mentorado = Mentorados.objects.get(id=id)
    if mentorado.user != request.user:
        raise Http404()
    video = request.FILES.get('video')
    upload = Upload(
        mentorado=mentorado,
        video=video
    )
    upload.save()
    return redirect(f'/mentorados/tarefa/{id}')


def tarefa_mentorado(request):
    mentorado = valida_token(request.COOKIES.get('auth_token'))
    if not mentorado:
        return redirect('auth_mentorado')

    if request.method == 'GET':
        videos = Upload.objects.filter(mentorado=mentorado)
        tarefas = Tarefa.objects.filter(mentorado=mentorado)
        return render(request, 'tarefa_mentorado.html', {'mentorado': mentorado, 'videos': videos, 'tarefas':tarefas})

from django.shortcuts import redirect

def tarefa_alterar(request, id):
    if request.method == 'POST':
        tarefa = Tarefa.objects.get(id=id)
        tarefa.realizada = not tarefa.realizada  # Alterna o estado
        tarefa.save()
        mentorado_id = request.POST.get('mentorado_id')
        return redirect('tarefa', id=mentorado_id)
    return redirect('mentorados')
    