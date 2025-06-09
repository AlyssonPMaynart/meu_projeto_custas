from django import forms

class EscolhaRecursoForm(forms.Form):
    TIPO_RECURSO_CHOICES = [
        ('inominado', 'Recurso Inominado (Juizado Especial)'),
        ('apelacao', 'Apelação (Vara Cível Comum)'),
    ]
    tipo_recurso = forms.ChoiceField(
        choices=TIPO_RECURSO_CHOICES,
        widget=forms.RadioSelect,
        label="Selecione o tipo de recurso"
    )

class ValorCausaForm(forms.Form):
    valor_causa = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0.01,
        label="Valor da Causa/Condenação (R$)"
    )