from django import forms

class EmailForm(forms.Form):
    client_id = forms.CharField(max_length=100)
    from_email = forms.EmailField()
    to_email = forms.EmailField()
    subject = forms.CharField(max_length=255)
    text_body = forms.CharField(required=False)
    html_body = forms.CharField(required=False)
    unsubscribe_url = forms.URLField(required=False)

    def clean(self):
        data = self.cleaned_data
        if not data.get('text_body') and not data.get('html_body'):
            raise forms.ValidationError("Either text_body or html_body must be provided.")
        return data

