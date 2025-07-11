from django import forms

class EnseignantForm(forms.Form):
    code = forms.CharField(max_length=3, label="Code (3 lettres MAJ)")
    nom = forms.CharField(max_length=100, label="Nom")
    prenom = forms.CharField(max_length=100, label="Prénom")
    email = forms.EmailField(label="Adresse e-mail")
    telephone = forms.CharField(max_length=20, required=False, label="Téléphone (optionnel)")
    service = forms.IntegerField(initial=0, label="Service (heures)")
    type = forms.ChoiceField(
        choices=[("permanent", "Permanent"), ("vacataire", "Vacataire")],
        label="Type d'enseignant"
    )

    def __init__(self, *args, readonly_code=False, **kwargs):
        super().__init__(*args, **kwargs)
        if readonly_code:
            self.fields['code'].widget.attrs['readonly'] = True

    def clean_code(self):
        code = self.cleaned_data['code'].upper()
        if not self.fields['code'].widget.attrs.get('readonly'):
            from .views import lire_donnees  # éviter import circulaire
            data = lire_donnees()
            if code in data:
                raise forms.ValidationError("Ce code existe déjà.")
        return code


