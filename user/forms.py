from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from multiupload.fields import MultiFileField

from .models import User, City, Municipality, News


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'patronymic', 'sex', 'username', 'date_of_birth', 'phone', 'address_street',
                  'address_house', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class LoginForm(AuthenticationForm):
    username = forms.EmailField(required=True, label='Почта')

    class Meta:
        model = User
        fields = ['username']


class CreateAppealForm(forms.Form):
    title = forms.CharField(max_length=100)
    text = forms.CharField(widget=forms.Textarea)
    photos = MultiFileField(max_num=10, max_file_size=1024 * 1024 * 5)  # Adjust max_num and max_file_size as needed
    municipality = forms.ModelChoiceField(queryset=Municipality.objects.all(), required=False,
                                          label='Выберите муниципалитет из списка')


class CreateNewsForm(forms.Form):
    title = forms.CharField(max_length=100)
    short_description = forms.CharField(widget=forms.Textarea, max_length=200)
    text = forms.CharField(widget=forms.Textarea)
    photos = MultiFileField(max_num=10, max_file_size=1024 * 1024 * 5)
    category = forms.ChoiceField(choices=list(map(lambda x: (x[0], x[0]), News.NewsCategory.choices)),
                                 label='Категория')


class ProfileEditForm(forms.Form):
    address_street = forms.CharField(max_length=100)
    address_house = forms.CharField(max_length=100)


class NewsFilterForm(forms.Form):
    categories = News.NewsCategory.values

    def __init__(self, *args, **kwargs):
        super(NewsFilterForm, self).__init__(*args, **kwargs)

        for category in self.categories:
            self.fields[category] = forms.BooleanField(
                required=False,
                initial=True,
                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            )

    def get_not_selected_categories(self):
        return [category for category in self.categories if not self.cleaned_data.get(category)]


class AnswerAppealForm(forms.Form):
    answer = forms.CharField(label='Ваш ответ')
    appeal_id = forms.IntegerField(required=False)


