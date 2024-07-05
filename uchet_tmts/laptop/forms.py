from django.forms import ModelForm, Textarea, TextInput#, DateInput, DateField
from django import forms 
from .models import *
import datetime
from django_select2 import forms as s2forms

# from django import forms


class Type_TMTS_Form(ModelForm):
    class Meta:
        model = Type_TMTS_Model
        fields = ('type_tmts',)
        widgets = {
            "type_tmts": TextInput(attrs={"size":60,}),
        }


class Name_TMTS_Form(ModelForm):
    class Meta:
        model = Name_TMTS_Model
        fields = ('type_TMTS', 'manufacturer', 'name_model',)
        widgets = {            
            "manufacturer": TextInput(attrs={"size":60,}),
            "name_model": TextInput(attrs={"size":60,}),            
        }


class Owner_TMTS_Form(ModelForm):
    class Meta:
        model = Owner_TMTS_Model
        fields = ('name_legal_entity',)  
        widgets = {
            "name_legal_entity": TextInput(attrs={"size":155,}),
        }      


class Responsible_TMTS_Form(ModelForm):
    class Meta:
        model = Responsible_TMTS_Model
        fields = ('account',)
        # fields = ('fio', 'account', 'email', 'distingished_name', 'legal_entity',)
        widgets = {            
            # "fio": TextInput(attrs={"size":80,}),
            "account": TextInput(attrs={"size":60,}),
            # "email": TextInput(attrs={"size":70,}),
            # "distingished_name": TextInput(attrs={"size":180,}),
            # "company": TextInput(attrs={"size":80,}),            
        }


# class Base_Search_Container_Form(ModelForm):
#     class Meta:
#         model = Base_Search_Container_Model
#         fields = ('name_container',)
#         widgets = {
#             "name_container": TextInput(attrs={"size":180,}),
#         }
     

       


# class Reestr_TMTS_Form(ModelForm):
#     class Meta:
#         model = Reestr_TMTS_Model
#         fields = '__all__'        

class DateInput(forms.DateInput):
    input_type='date'

    def __init__(self, **kwargs):
        kwargs["format"] = "%Y-%m-%d"
        super().__init__(**kwargs)


class Reestr_TMTS_Form(ModelForm):

    
    class Meta:
        model = Reestr_TMTS_Model
        fields = ('owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'location', 'comment', 'start_of_operation_TMTS', 'archived',) #'status','creator_account'                    
        widgets = {            
            "serial_number": TextInput(attrs={"size":60,}),
            "username_responsible_TMTS": TextInput(attrs={"size":60,}),
            "location": TextInput(attrs={"size":110,}),
            "creator_account": TextInput(attrs={"size":60,}),
            "comment": Textarea(attrs={'rows':3,'cols':100,}),#'style': 'height: 1em;'
            # "start_of_operation_TMTS": DateInput(format='%d/%m/%Y', attrs={      #required=False, format='%yyyy-%m-%d',                                               
            #                                         'class':'datepicker',
            #                                         'type':'date',
            #                                         'placeholder':'Select a date',
            #                                         # 'placeholder':'yyyy-mm-dd (DOB)',
            #                                         # 'class':'form-control',
            #                                             }
                                                        
            #                                     )
        }
        # start_of_operation_TMTS = DateField(
        #     initial=datetime.date(2000,1,1),
        #     required=True,
        #     widget=DateInput(attrs={'type':'date','class':'form-control','format':'%y-%m-%d',})# 'placeholder':'yyyy-mm-dd (DOB)',
        # )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_of_operation_TMTS'].widget = DateInput()
    #         attrs={'type':'date',
    #                'placeholder':'yyyy-mm-dd (DOB)',
    #                'class':'form-control',
    #                'format':'%y-%m-%d',
                   
    #                }
    #                ) 
                                                    
                                                        
                                                


# class Reestr_TMTS_Comments_Form(ModelForm):
#     class Meta:
#         model = Reestr_TMTS_Comments_Model
#         fields = ('reestr_TMTS', 'short_description', 'comment', 'creator_account',)
        

class Responsible_TMTS_repair_Form(ModelForm):
    class Meta:
        model = Responsible_TMTS_repair_Model
        fields = ('account',)
        # fields = ('fio', 'account', 'email', 'distingished_name', 'legal_entity',)
        widgets = {            
            # "fio": TextInput(attrs={"size":80,}),
            "account": TextInput(attrs={"size":60,}),
            # "email": TextInput(attrs={"size":70,}),
            # "distingished_name": TextInput(attrs={"size":180,}),
            # "company": TextInput(attrs={"size":80,}),            
        }

class Reestr_TMTS_repair_Form(ModelForm):
    class Meta:
        model = Reestr_TMTS_repair_Model
        # fields = '__all__'
        fields = ('responsible_TMTS_repair', 'comment',)        
        # readonly_fields = ['reestr_TMTS']         
        # widgets = {
            
            # "username_responsible_TMTS": TextInput(attrs={"size":60,}),
            # "responsible_TMTS_repair": TextInput(attrs={"size":175,}),

            # "creator_account": TextInput(attrs={"size":60,}),
        # }

# class Reestr_TMTS_repair_ModelForm(ModelForm):
#     class Meta:
#         model = Reestr_TMTS_repair_Model
#         fields = ('username_responsible_TMTS_repair', 'comment',)
#         # fields = '__all__'
        

class Image_Reestr_TMTS_repair_Form(ModelForm):
    class Meta:
        model = Image_Reestr_TMTS_repair_Model
        fields = ('image_comment', 'picture', )    # fields = '__all__'





# ***********************************************************************************************************************************************************
# django_select2
class CreatorAccount_Widget(s2forms.ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        # "email__icontains",
    ]

class Reestr_TMTS_Model_SearchForm(forms.ModelForm):
    class Meta:
        model = Reestr_TMTS_Model
        fields = "__all__"
        widgets = {
            "creator_account": CreatorAccount_Widget,
            
        }

# ***********************************************************************************************************************************************************
# 
class Reestr_TMTS_Model_SearchForm2(forms.ModelForm):
    class Meta:
        model = Reestr_TMTS_Model
        fields = "__all__"
        widgets = {
            "creator_account": CreatorAccount_Widget,
            
        }

