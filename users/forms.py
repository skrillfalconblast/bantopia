from django import forms


class EditPasswordForm(forms.Form):

    old_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class' : 'edit-text-input'}))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class' : 'edit-text-input'}))
    confirm_new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class' : 'edit-text-input'}))