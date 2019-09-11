from django import forms
from knowledgebase.models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ['id', 'page_title', 'page_content']
        
class SpaceForm(forms.ModelForm):
    class Meta:
        model = Space
        fields = ['space_id', 'space_title', 'space_description']

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    class Meta:
        model = User
        fields = ['username', 'password']

#    def __init__(self, *args, **kwargs):
#        self.request = kwargs.pop('request', None)
#        super(UserForm, self).__init__(*args, **kwargs)

class SignupForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Username'}),
        min_length = 4)
    email = forms.EmailField(
        widget=forms.TextInput(attrs={'placeholder': 'Email'}), required = True)
    password1 = forms.CharField(label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(label='Confirm Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class ProfileForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(), required = True)
    password1 = forms.CharField(label='Password',required=False,
        widget=forms.PasswordInput())
    password2 = forms.CharField(label='Confirm Password', required=False,
        widget=forms.PasswordInput())
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        
    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
        
    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class ProfileExtendedForm(forms.ModelForm):
    user_avatar = forms.FileField(
        widget=forms.FileInput(attrs={'hidden':True}), required = False)
    class Meta:
        model = UserExtended
        fields = ['user_desc', 'user_phone', 'user_address', 'user_city',
                  'user_postal', 'user_prov', 'user_country']
        
#    def save(self, commit=True):
#        user_ext = super(ProfileExtendedForm, self).save(commit=False)
#        user_ext.user_avatar = self.cleaned_data.get('user_avatar')
#        if commit:
#            user_ext.save()
#        return user_ext
