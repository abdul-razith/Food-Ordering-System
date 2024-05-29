# forms.py
from django import forms
from Food.models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['item_name', 'item_desc', 'item_price', 'sub_category', 'item_category', 'discount', 'is_trending', 'item_image']
