from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, label='Full Name')
    email = forms.EmailField(label='Email Address')
    address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Shipping Address',
    )
