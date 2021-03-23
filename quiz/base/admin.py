from django.contrib import admin

# Register your models here.
from quiz.base.models import Pergunta


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ('id', 'enunciado', 'disponivel')