from django.forms.widgets import DateInput, TextInput, CheckboxSelectMultiple
from django_filters import FilterSet, DateFilter, CharFilter, MultipleChoiceFilter
from .models import Advertisement, Category


class AdvFilter(FilterSet):
    title = CharFilter(field_name='title',
                       lookup_expr='icontains',
                       label='Тема объвления',
                       widget=TextInput(attrs={'class': 'form-control',
                                               'style': 'width: 100%;'}))
    category = MultipleChoiceFilter(field_name='category__name',
                                    label='Категория',
                                    choices=[(category.name, category.name) for category in Category.objects.all()],
                                    widget=CheckboxSelectMultiple())
    text = CharFilter(field_name='text',
                       lookup_expr='icontains',
                       label='Текст',
                       widget=TextInput(attrs={'class': 'form-control',
                                               'style': 'width: 100%;'}))

    class Meta:
        model = Advertisement
        fields = ['title', 'category', 'text']