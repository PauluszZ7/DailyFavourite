from django import forms
from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'profile_image', 'genre', 'is_public']
        widgets = {
            'profile_image': forms.FileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "Beschreibung"
        self.fields['profile_image'].label = "Profilbild"