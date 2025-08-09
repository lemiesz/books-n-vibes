from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Mix
import json


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ProfileForm(forms.ModelForm):
    socials_json = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Profile
        fields = ('display_name', 'bio', 'avatar', 'socials_json')

    def clean_socials_json(self):
        data = self.cleaned_data.get('socials_json')
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError('Invalid JSON')
        return None


class MixForm(forms.ModelForm):
    class Meta:
        model = Mix
        fields = ('title', 'description', 'audio', 'cover', 'bpm', 'genres_csv', 'visibility')

    def clean_audio(self):
        audio = self.cleaned_data.get('audio')
        if audio:
            if audio.size > 300 * 1024 * 1024:
                raise forms.ValidationError('File too large (max 300MB)')
            if audio.content_type not in ['audio/mpeg', 'audio/mp4', 'audio/aac', 'audio/wav']:
                raise forms.ValidationError('Unsupported audio type')
        return audio

    def clean_cover(self):
        cover = self.cleaned_data.get('cover')
        if cover and cover.size > 300 * 1024 * 1024:
            raise forms.ValidationError('File too large (max 300MB)')
        return cover


class FeaturedForm(forms.Form):
    username = forms.CharField(max_length=150)
