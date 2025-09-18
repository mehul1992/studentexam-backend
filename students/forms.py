from django import forms
from django.forms import PasswordInput
from .models import Student


class StudentAdminForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=PasswordInput(render_value=False),
        required=False,
        help_text='Leave blank to keep existing password.'
    )

    class Meta:
        model = Student
        fields = '__all__'

    def clean_password(self):
        # Return raw password; model.save() will hash it if provided
        password = self.cleaned_data.get('password')
        if password is None:
            return ''
        return password


