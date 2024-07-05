from decimal import Decimal

from django.db.models import Q
from django.forms import TextInput
import django_filters

from .models import *


class Reestr_TMTS_Model_Filter(django_filters.FilterSet):
    serial_number = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')
    comment = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Reestr_TMTS_Model
        fields = ['status', 'owner_TMTS', 'name_TMTS', 'serial_number', 
                  'responsible_TMTS', 'location', 'creator_account', 'comment', ]
        

class Arhiv_Reestr_TMTS_Model_Filter(django_filters.FilterSet):
    id_reestr_tmts = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='icontains')
    owner_TMTS = django_filters.CharFilter(lookup_expr='icontains')
    name_TMTS = django_filters.CharFilter(lookup_expr='icontains')
    serial_number = django_filters.CharFilter(lookup_expr='icontains')
    username_responsible_TMTS = django_filters.CharFilter(lookup_expr='icontains')
    responsible_TMTS = django_filters.CharFilter(lookup_expr='icontains')
    location = django_filters.CharFilter(lookup_expr='icontains')

    # created_reestr_tmts_model_initial = django_filters.DateTimeFilter(name = 'created_reestr_tmts_model', lookup_type='gte')
    # created_reestr_tmts_model_final = django_filters.DateTimeFilter(name = 'created_reestr_tmts_model', lookup_type='lte')

    creator_account = django_filters.CharFilter(lookup_expr='icontains')
    # updated_reestr_tmts_model = django_filters.DateTimeFilter(action=filter_unix_dt)
    comment = django_filters.CharFilter(lookup_expr='icontains')
    # start_of_operation_TMTS = django_filters.DateTimeFilter(action=filter_unix_dt)
    # archived = django_filters.CharFilter(lookup_expr='icontains')
    # created = django_filters.DateTimeFilter(action=filter_unix_dt)
    action = django_filters.CharFilter(lookup_expr='icontains')
    creator_action = django_filters.CharFilter(lookup_expr='icontains')



    class Meta:
        model = Arhiv_Reestr_TMTS_Model
        fields = ['id_reestr_tmts', 'status', 'owner_TMTS', 'name_TMTS', 
                  'serial_number', 'username_responsible_TMTS', 'responsible_TMTS', 'location', 
                #   'created_reestr_tmts_model_initial', 'created_reestr_tmts_model_final',
                  'creator_account', 
                #   'updated_reestr_tmts_model', 
                  'comment', 
                #   'start_of_operation_TMTS', 
                  'archived', 
                #   'created', 
                  'action', 'creator_action', ]
        # fields = {
        #             'id_reestr_tmts':['exact',],
        #             'status':['exact',],
        #             'owner_TMTS':['icontains',],
        #             'name_TMTS':['icontains',],
        #             'serial_number':['icontains',],
        #             'username_responsible_TMTS':['icontains',],
        #             'responsible_TMTS':['icontains',],
        #             'location':['icontains',],
        #             'created_reestr_tmts_model':['exact',],
        #             'creator_account':['icontains',],
        #             'updated_reestr_tmts_model':['icontains',],
        #             'comment':['icontains',],
        #             'start_of_operation_TMTS':['icontains',],
        #             'archived':['icontains',],
        #             'created':['icontains',],
        #             'action':['icontains',],
        #             'creator_action':['icontains',],
        #           }


# class Reestr_TMTS_Model_Filter(django_filters.FilterSet):


#     status = models.ForeignKey('Status_TMTS_Model', default=1, on_delete=models.PROTECT, verbose_name='Статус', related_name='status_tmts_fk')
#     owner_TMTS = models.ForeignKey('Owner_TMTS_Model', on_delete=models.PROTECT, verbose_name='Владелец ТМЦ')
#     name_TMTS = models.ForeignKey('Name_TMTS_Model', on_delete=models.PROTECT, verbose_name='Тип оборудования | Производитель | Модель')
#     serial_number = models.CharField(max_length=50, blank=True, verbose_name='S/N', db_index=True)
#     username_responsible_TMTS = models.CharField(max_length=50, blank=True, verbose_name='Учетная запись ответственного за ТМЦ')
#     responsible_TMTS = models.ForeignKey('Responsible_TMTS_Model', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Ответственный за ТМЦ')
#     location = models.CharField(max_length=100, blank=True, verbose_name='Локация/Кабинет')
#     created = models.DateTimeField(auto_now_add=True, db_index=True)    
#     creator_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Кем изменено/создано')
#     updated = models.DateTimeField(auto_now=True)
#     comment = django_filters.CharFilter(label="", lookup_expr="istartswith")
#     archived = models.BooleanField(default=False, verbose_name='Переведен в архив')


    
#     id = django_filters.NumberFilter(label="")
#     name = django_filters.CharFilter(label="", lookup_expr="istartswith")
#     category = django_filters.CharFilter(label="", lookup_expr="istartswith")
#     price = django_filters.NumberFilter(label="", method="filter_decimal")
#     cost = django_filters.NumberFilter(label="", method="filter_decimal")
#     status = django_filters.ChoiceFilter(label="", choices=Product.Status.choices)

#     class Meta:
#         model = Reestr_TMTS_Model
#         fields = ["id", "name", "category", "price", "cost", "status"]

#     def filter_decimal(self, queryset, name, value):
#         # For price and cost, filter based on
#         # the following property:
#         # value <= result < floor(value) + 1

#         lower_bound = "__".join([name, "gte"])
#         upper_bound = "__".join([name, "lt"])

#         upper_value = math.floor(value) + Decimal(1)

#         return queryset.filter(**{lower_bound: value,
#                                   upper_bound: upper_value})