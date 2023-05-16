from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm, fields, Textarea, EmailField, ModelMultipleChoiceField, TextInput, \
    CheckboxSelectMultiple, inlineformset_factory, ClearableFileInput
from .models import Reply, Profile, Advertisement, AdFiles, Category


class ReplyForm(ModelForm):
    text = fields.CharField(label='Написать отклик:',
                            widget=Textarea(attrs={'class': 'form-control', 'rows': 3}))

    class Meta:
        model = Reply
        fields = ('ad', 'user', 'text')


class RegistrationForm(UserCreationForm):
    email = EmailField(label="Email")

    class Meta:
        model = Profile
        fields = ('username', 'email', 'password1', 'password2')


class AdvForm(ModelForm):
    title = fields.CharField(label='Название',
                             widget=TextInput(attrs={'class': 'form-control'}))
    category = ModelMultipleChoiceField(label='Категория',
                                        queryset=Category.objects.all(),
                                        widget=CheckboxSelectMultiple(attrs={'class': 'py-sm-1'}))
    text = fields.CharField(label='Содержание',
                            widget=Textarea(attrs={'class': 'form-control'}))

    class Meta:
        model = Advertisement
        fields = ['title', 'user', 'category',  'text']


class AdFilesForm(ModelForm):
    class Meta:
        model = AdFiles
        fields = ['file']
        widgets = {'file': ClearableFileInput(attrs={'multiple': True, 'class': 'form-control my-3'})}


AdFilesFormset = inlineformset_factory(Advertisement, AdFiles, extra=1, form=AdFilesForm)