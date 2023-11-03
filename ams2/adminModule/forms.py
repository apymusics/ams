from django import forms
from django.shortcuts import render
from django.core.exceptions import ValidationError

class ExcelImportForm(forms.Form):
    excel_file = forms.FileField(
        label='Import from Excel',
        widget=forms.ClearableFileInput(attrs={'accept': '.xls, .xlsx, .csv'})
    )

def import_excel_view(request):
    if request.method == 'POST':
        form = ExcelImportForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = form.cleaned_data['excel_file']
            
            # Check file extension
            if not excel_file.name.endswith('.xls') and not excel_file.name.endswith('.xlsx'):
                form.add_error('excel_file', 'Only .xls and .xlsx files are allowed.')
         
    else:
        form = ExcelImportForm()

 
