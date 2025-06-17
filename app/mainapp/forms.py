from django import forms
from .models import Group


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = [
            'name',
            'description',
            'profile_image',
            'genre',
            'is_public',
            'max_posts_per_day',
            'post_permission',
            'read_permission'
        ]
        widgets = {
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'genre': forms.Select(attrs={'class': 'form-select'}),
            'max_posts_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 100
            }),
            'post_permission': forms.Select(attrs={'class': 'form-select'}),
            'read_permission': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].label = "Beschreibung"
        self.fields['profile_image'].label = "Profilbild"
        self.fields['max_posts_per_day'].label = "Maximale Posts pro Tag"
        self.fields['post_permission'].label = "Post-Berechtigung"
        self.fields['read_permission'].label = "Lese-Berechtigung"

        # Hilfetexte hinzufügen
        self.fields['max_posts_per_day'].help_text = "Maximale Anzahl an Posts pro Mitglied pro Tag"
        self.fields['post_permission'].help_text = "Wer darf Posts in dieser Gruppe erstellen?"
        self.fields['read_permission'].help_text = "Wer darf die Posts in dieser Gruppe lesen?"

        # Initialwerte setzen
        self.fields['max_posts_per_day'].initial = 1
        self.fields['post_permission'].initial = 'all'
        self.fields['read_permission'].initial = 'all'