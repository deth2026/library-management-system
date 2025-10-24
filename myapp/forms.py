from django import forms
from django.contrib.auth.models import User
from .models import Book, UserProfile, Category, Author

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['image', 'title', 'author', 'category', 'description', 'copies']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter book title'
            }),
            'author': forms.Select(attrs={
                'class': 'form-select'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Enter book description'
            }),
            'copies': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter category name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Enter category description (optional)'
            }),
        }

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'biography']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter author name'
            }),
            'biography': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Enter author biography (optional)'
            }),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['address', 'phone_number', 'profile_image']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class UserForm(forms.Form):
    username = forms.CharField(max_length=150, 
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Password (leave blank to keep current)"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        label="Confirm Password"
    )

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        
        if self.instance:
            self.fields['username'].initial = self.instance.username
            self.fields['email'].initial = self.instance.email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exclude(id=self.instance.id if self.instance else None).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

class SimpleRegisterForm(forms.Form):
    username = forms.CharField(max_length=150, 
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=False,
                            widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data.get('email', '')
        password = self.cleaned_data['password']
        
        user = User.objects.create_user(username=username, email=email, password=password)
        return user