from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from .models import *
from .admin_mixins import ExportAsCSVMixin


@admin.register(Name_TMTS_Model)
class Name_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'type_TMTS', 'manufacturer', 'name_model',)
    list_display_links = ('type_TMTS', 'manufacturer', 'name_model',)
    list_filter = ['type_TMTS__type_tmts', 'manufacturer', 'name_model',]
    search_fields = ('type_TMTS__type_tmts', 'manufacturer', 'name_model',)
    ordering = ('type_TMTS__type_tmts', 'manufacturer', 'name_model',)


@admin.register(Type_TMTS_Model)
class Type_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'type_tmts',)
    list_display_links = ('type_tmts',)
    list_filter = ['type_tmts',]
    search_fields = ('type_tmts',)
    ordering = ('type_tmts',)


@admin.register(Owner_TMTS_Model)
class Owner_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'name_legal_entity',)
    list_display_links = ('name_legal_entity',)
    list_filter = ['name_legal_entity',]
    search_fields = ('name_legal_entity',)
    ordering = ('name_legal_entity',)


@admin.register(Responsible_TMTS_Model)
class Responsible_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'fio', 'account', 'email', 'distingished_name', 'company', 'company_position', 'mobile', 'telephone_number')
    list_display_links = ('fio', 'account',)
    list_filter = ['fio', 'account', 'company', 'company_position']
    search_fields = ('fio', 'account', 'company', 'company_position', 'mobile', 'telephone_number')
    ordering = ('fio', 'account',)


# @admin.register(Base_Search_Container_Model)
# class Base_Search_Container_Admin(admin.ModelAdmin, ExportAsCSVMixin):
#     actions = [        
#         'export_csv',
#     ]

#     list_display = ('id', 'name_container',)
#     list_display_links = ('name_container',)
#     list_filter = ['name_container',]
#     search_fields = ('name_container',)
#     ordering = ('name_container',)


# ---------------------------------------------------------------
# Reestr_TMTS_Model

@admin.action(description='Архивировать записи')
def TMTS_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)

@admin.action(description='Вернуть записи из архива')
def TMTS_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)

# class Reestr_TMTS_Comments_Inline(admin.TabularInline):   # добавляем в Reestr_TMTS_Admin поля из Reestr_TMTS_Comments
#     model = Reestr_TMTS_Comments_Model
#     readonly_fields = ('id', 'created', 'updated')    
#     extra = 1 # Это определяет, сколько еще форм, в дополнение к начальным формам, отображается в наборе форм. по умолчанию до 3
#     # # fk_name = 'printers_comments'


@admin.register(Status_TMTS_Model)
class Status_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'status',)
    list_display_links = ('status',)
    list_filter = ['status',]
    search_fields = ('id', 'status',)
    ordering = ('status',)


@admin.register(Reestr_TMTS_Model)
class Reestr_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        TMTS_archived,
        TMTS_unarchived,
        'export_csv',

    ]
    # inlines = [Reestr_TMTS_Comments_Inline,]   # добавляем в Reestr_TMTS_Admin поля из Reestr_TMTS_Comments

    list_display = ('id', 'status', 'owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'responsible_TMTS', 'location',
                    'created', 'creator_account', 'updated', 'comment', 'start_of_operation_TMTS', 'archived',)
    list_display_links = ('name_TMTS','serial_number',)
    list_filter = ['status__status', 'owner_TMTS__name_legal_entity', 'name_TMTS__type_TMTS__type_tmts', 'username_responsible_TMTS', 'location','creator_account', ]
    # filters = ['service_object', 'print_server__print_server', 'status_printer__status', 'location', 'printers__name',]

    search_fields = ('status__status', 'serial_number', 'owner_TMTS__name_legal_entity', 'name_TMTS__type_TMTS__type_tmts', 
                     'username_responsible_TMTS', 'location','creator_account__username', 'comment', 'updated',) #
    
    ordering = ('status__status', 'owner_TMTS__name_legal_entity', 'name_TMTS__type_TMTS__type_tmts', 'username_responsible_TMTS',)

    def queryset(self, request):
        # return Reestr_TMTS_Model.objects.select_related('Owner_TMTS_Model', 'Type_TMTS_Model', 'Name_TMTS_Model', 'Responsible_TMTS_Model').prefetch_related('Reestr_TMTS_Comments_Model')
        return Reestr_TMTS_Model.objects.select_related('Owner_TMTS_Model', 'Type_TMTS_Model', 'Name_TMTS_Model', 'Responsible_TMTS_Model')

    # # группировка полей в админке
    # fieldsets = [
    #     ('Namesection1', {"fields":('serial_number', 'printers',)}),
    #     ('Namesection2', 
    #         {"fields": ('status_printer', 'print_server', 'name_on_print_server', 'ip_address', 'location',),
    #          'classes': ('wide', 'collapse',),}),  # параметр 'collapse' позволяет скрывать секцию, 'wide' - смещение полей
    #     ('Extra options', {
    #         "fields": ('archived',),
    #         'classes': ('collapse',),
    #         'description': 'Extra options. Field "archived" is for soft delete',
    #     }),             
    # ]
    

    # '_short_comments'

    # def _cartridges(self, row):
    #     return ', '.join([x.name for x in row.cartridges.all()])

    # def _short_comments(self, obj:Printers_in_service_comments) -> str:
    #     if len(obj.printers_comments) < 55:
    #         return obj.printers_comments
    #     return obj.printers_comments[:55] + "..."


@admin.register(Arhiv_Reestr_TMTS_Model)
class Arhiv_Reestr_TMTS_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',

    ]    

    list_display = ('id','id_reestr_tmts', 'status', 'owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'responsible_TMTS', 'location',
                    'created_reestr_tmts_model', 'creator_account', 'updated_reestr_tmts_model', 'comment', 'start_of_operation_TMTS', 'archived', 'created', 'action', 'creator_action')
    list_display_links = ('name_TMTS','serial_number',)
    list_filter = ['id_reestr_tmts', 'status', 'owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'created_reestr_tmts_model', 
                   'updated_reestr_tmts_model', 'created', 'action', 'creator_action']    
    search_fields = ('id_reestr_tmts', 'status', 'owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'responsible_TMTS', 'location',
                    'created_reestr_tmts_model', 'creator_account', 'updated_reestr_tmts_model', 'comment', 'created', 'action', 'creator_action')
    ordering = ('created',)    
    
    
# @admin.register(Reestr_TMTS_Comments_Model)
# class Reestr_TMTS_Comments_Admin(admin.ModelAdmin, ExportAsCSVMixin):
#     actions = [        
#         'export_csv',
#     ]

#     list_display = ('reestr_TMTS', 'short_description', '_short_comment', 'created', 'updated',)
#     list_display_links = ('reestr_TMTS', 'short_description',)
#     search_fields = ('reestr_TMTS__responsible_TMTS__account', 'short_description', 'comment', 'created', 'updated',)
#     ordering = ('-created',)

#     def _short_comment(self, obj:Reestr_TMTS_Comments_Model) -> str:
#         if len(obj.comment) < 15:
#             return obj.comment
#         return obj.comment[:15] + "..."




@admin.register(Reestr_TMTS_repair_Model)
class Reestr_TMTS_repair_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [
        TMTS_archived,
        TMTS_unarchived,
        'export_csv',

    ]
    # inlines = [Reestr_TMTS_Comments_Inline,]   # добавляем в Reestr_TMTS_Admin поля из Reestr_TMTS_Comments

    list_display = ('id', 'reestr_TMTS', 'username_responsible_TMTS_repair', 'responsible_TMTS_repair', 
                    'created', 'creator_account', 'updated', 'comment', 'archived')    
    list_display_links = ('reestr_TMTS',)


    list_filter = ['reestr_TMTS__owner_TMTS__name_legal_entity', 'reestr_TMTS__name_TMTS__type_TMTS__type_tmts', 'responsible_TMTS_repair__fio', ]   


    search_fields = ('reestr_TMTS__serial_number', 'reestr_TMTS__owner_TMTS__name_legal_entity', 'reestr_TMTS__name_TMTS__type_TMTS__type_tmts', 
                     'username_responsible_TMTS_repair', 'creator_account__username', 'created', 'comment', 'updated',)
    ordering = ('created','username_responsible_TMTS_repair',)

    def queryset(self, request):        
        return Reestr_TMTS_repair_Model.objects.select_related('Reestr_TMTS_Model', 'Responsible_TMTS_repair_Model',)


@admin.register(Responsible_TMTS_repair_Model)
class Responsible_TMTS_repair_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',
    ]

    list_display = ('id', 'fio', 'account', 'email', 'distingished_name', 'company', 'company_position', 'mobile', 'telephone_number')
    list_display_links = ('fio', 'account',)
    list_filter = ['fio', 'account', 'company', 'company_position']
    search_fields = ('fio', 'account', 'company', 'company_position', 'mobile', 'telephone_number')
    ordering = ('fio', 'account',)


@admin.register(Arhiv_Reestr_TMTS_repair_Model)
class Arhiv_Reestr_TMTS_repair_Admin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [        
        'export_csv',

    ]    

    list_display = ('id', 'id_reestr_tmts_repair', 'id_reestr_tmts', 'reestr_TMTS', 'username_responsible_TMTS_repair', 'responsible_TMTS_repair',
                    'created_reestr_tmts_repair', 'creator_account', 'updated_reestr_tmts_repair', 'comment', 'archived', 'created', 'action', 'creator_action')
    list_display_links = ('reestr_TMTS','username_responsible_TMTS_repair',)
    list_filter = ['id', 'id_reestr_tmts_repair', 'id_reestr_tmts', 'username_responsible_TMTS_repair', 
                    'updated_reestr_tmts_repair', 'archived', 'created', 'action', 'creator_action']    
    search_fields = ('id', 'id_reestr_tmts_repair', 'id_reestr_tmts', 'reestr_TMTS', 'username_responsible_TMTS_repair', 'responsible_TMTS_repair',
                    'created_reestr_tmts_repair', 'creator_account', 'updated_reestr_tmts_repair', 'comment', 'archived', 'created', 'action', 'creator_action')
    ordering = ('created',)  


@admin.register(Image_Reestr_TMTS_repair_Model)
class Image_Reestr_TMTS_repair_Admin(admin.ModelAdmin):     

    list_display = ('id', 'image_comment', 'picture', 'created', 'reestr_repair_TMTS')
    list_display_links = ('id',)
    list_filter = ['created',]#'reestr_repair_TMTS__reestr_TMTS__serial_number'    
    search_fields = ('id', 'created',)#'reestr_repair_TMTS__reestr_TMTS__serial_number'
    ordering = ('-created',)





# @admin.register(PrintersModel)
# class PrintersAdmin(admin.ModelAdmin, ExportAsCSVMixin):
#     actions = [        
#         'export_csv',
#     ]

#     model = CartridgesModel
#     filter_horizontal = ('cartridges',)
#     list_display = ('id', 'name', '_cartridges', 'sn_oid', 'printed_pages_all_oid',)
#     list_display_links = ('name',)
#     list_filter = ['name', 'cartridges', 'printed_pages_all_oid',]
#     search_fields = ('id', 'name', 'cartridges__name', 'sn_oid__oid', 'printed_pages_all_oid__oid',)
#     ordering = ('name',)
    
#     def _cartridges(self, row):
#         return ', '.join([x.name for x in row.cartridges.all()])
    
#     def queryset(self, request):
#         return PrintersModel.objects.select_related("Cartridges")
