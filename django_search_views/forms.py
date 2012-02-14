from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(label='Search')

class CategorySearchForm(SearchForm):
    category = forms.ChoiceField(required=False)
