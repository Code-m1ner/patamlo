from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    """
    Create a form for any user to contact the company
    """

    class Meta:
        model = Contact
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'name': 'Full Name',
            'email': 'Email',
            'subject': 'Subject',
            'message': 'Message'
        }

        for field in self.fields:
            # Adds a asterisk to fields that are required
            placeholder = f'{placeholders[field]} *'
            # Sets the placeholder to the values outlined in the
            # placeholders dictionary
            self.fields[field].widget.attrs['placeholder'] = placeholder
            # Adds a CSS class to style the inputs
            self.fields[field].widget.attrs['class'] = 'product-style-input'
            # Removes the labels
            self.fields[field].label = False