from django import forms
from .models import DiaryEntry, DiaryMedia,MediaChoices


class DiaryEntryForm(forms.ModelForm):
    class Meta:
        model = DiaryEntry
        fields = ['title', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required',
                'placeholder': 'Enter diary title'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'required': 'required',
                'placeholder': 'Write your notes here...',
                'rows': 5
            }),
        }



class DiaryMediaForm(forms.ModelForm):
   class Meta:
        model = DiaryMedia
        fields = ['file', 'media_type']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'required': True
                
            }),
            'media_type': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
        }