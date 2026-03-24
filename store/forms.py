from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=200, label='Full Name')
    email = forms.EmailField(label='Email Address')
    address_line1 = forms.CharField(max_length=200, label='Address Line 1')
    address_line2 = forms.CharField(max_length=200, label='Address Line 2', required=False)
    city = forms.CharField(max_length=120, label='City')
    state = forms.CharField(max_length=120, label='State/Province')
    postal_code = forms.CharField(max_length=20, label='Postal Code')
    country = forms.CharField(max_length=2, label='Country', initial='US')
