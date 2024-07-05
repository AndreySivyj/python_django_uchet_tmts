from django.urls import path, include
from .views import *

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # path('', index, name='index'),
    path('', reestr_tmts_list_view, name='index'),
    
    # Name_TMTS_Model
    path('name_tmts_create/', name_tmts_create_view, name='name_tmts_create'),
    path('name_tmts_list/', name_tmts_list_view, name='name_tmts_list'),
    path('name_tmts/<int:id>/', name_tmts_detail_view, name='name_tmts_detail'),
    path('name_tmts_update/<int:id>/', name_tmts_update_view, name='name_tmts_update'),
    path('name_tmts_delete/<int:id>/', name_tmts_delete_view, name='name_tmts_delete'),

    # Type_TMTS_Model
    path('type_tmts_create/', type_tmts_create_view, name='type_tmts_create'),
    path('type_tmts_list/', type_tmts_list_view, name='type_tmts_list'),
    path('type_tmts/<int:id>/', type_tmts_detail_view, name='type_tmts_detail'),
    path('type_tmts_update/<int:id>/', type_tmts_update_view, name='type_tmts_update'),
    path('type_tmts_delete/<int:id>/', type_tmts_delete_view, name='type_tmts_delete'),

    # Owner_TMTS_Model
    path('owner_tmts_create/', owner_tmts_create_view, name='owner_tmts_create'),
    path('owner_tmts_list/', owner_tmts_list_view, name='owner_tmts_list'),
    path('owner_tmts/<int:id>/', owner_tmts_detail_view, name='owner_tmts_detail'),
    path('owner_tmts_update/<int:id>/', owner_tmts_update_view, name='owner_tmts_update'),
    path('owner_tmts_delete/<int:id>/', owner_tmts_delete_view, name='owner_tmts_delete'),

    # Responsible_TMTS_Model
    # path('responsible_tmts_create/', responsible_tmts_create_view, name='responsible_tmts_create'),
    path('responsible_tmts_list/', responsible_tmts_list_view, name='responsible_tmts_list'),
    path('responsible_tmts_search_list/', responsible_tmts_search_list_view, name='responsible_tmts_search_list'),# search
    
    path('responsible_tmts_get_reestr_tmts/<int:id>/', responsible_tmts_get_reestr_tmts, name='responsible_tmts_get_reestr_tmts'),#get_reestr_tmts

    # path('responsible_tmts/<int:id>/', responsible_tmts_detail_view, name='responsible_tmts_detail'),
    # path('responsible_tmts_update/<int:id>/', responsible_tmts_update_view, name='responsible_tmts_update'),
    # path('responsible_tmts_delete/<int:id>/', responsible_tmts_delete_view, name='responsible_tmts_delete'),

    # Reestr_TMTS_Model
    path('reestr_tmts_create/', reestr_tmts_create_view, name='reestr_tmts_create'),
    path('reestr_tmts_list/', reestr_tmts_list_view, name='reestr_tmts_list'),

    path('reestr_tmts_list_filter/', reestr_tmts_list_view_filter, name='reestr_tmts_list_filter'),
    
    path('reestr_tmts_archived_list/', reestr_tmts_archived_list_view, name='reestr_tmts_archived_list'),#_archived_
    path('reestr_tmts_/<int:id>/', reestr_tmts_detail_view, name='reestr_tmts_detail'),
    path('reestr_tmts_update/<int:id>/', reestr_tmts_update_view, name='reestr_tmts_update'),
    path('reestr_tmts_delete/<int:id>/', reestr_tmts_delete_view, name='reestr_tmts_delete'),
    path('export_reestr_tmts_xls/', export_reestr_tmts_xls, name='export_reestr_tmts_xls'),# export_xls
    
    path('export_reestr_tmts_xls_filter/', export_reestr_tmts_xls_filter, name='export_reestr_tmts_xls_filter'),# export_xls
    
    path('export_reestr_tmts_archived_xls/', export_reestr_tmts_archived_xls, name='export_reestr_tmts_archived_xls'),# export_xls_archived_
    path('reestr_tmts_search_list/', reestr_tmts_search_list_view, name='reestr_tmts_search_list'),# search
    path('reestr_tmts_archived_search_list/', reestr_tmts_archived_search_list_view, name='reestr_tmts_archived_search_list'),# search_archived_
    path('reestr_tmts_return_to_sklad/<int:id>/', reestr_tmts_return_to_sklad, name='reestr_tmts_return_to_sklad'),# 'на склад'



    # path('reestr_tmts_list_new/', Reestr_TMTS_Model_List.as_view(), name='reestr_tmts_list_new'),
    path('reestr_tmts_list_new/', reestr_TMTS_list_new, name='reestr_tmts_list_new'),
    path('reestr_tmts_list_universal/', reestr_TMTS_list_universal, name='reestr_tmts_list_universal'),




    # Arhiv_Reestr_TMTS_Model
    # path('reestr_arhiv_tmts_list/', reestr_arhiv_tmts_list_view, name='reestr_arhiv_tmts_list'),    # только последние 100 записей
    path('reestr_arhiv_tmts_list/', reestr_arhiv_tmts_list_view_filter, name='reestr_arhiv_tmts_list'),
    path('export_reestr_arhiv_tmts_xls/', export_reestr_arhiv_tmts_xls, name='export_reestr_arhiv_tmts_xls'),# export_xls
    path('reestr_arhiv_tmts_search_list/', reestr_arhiv_tmts_search_list_view, name='reestr_arhiv_tmts_search_list'),# search (отдельный шаблон, т.к. в listview только последние 100 записей)

    # Responsible_TMTS_repair_Model
    path('responsible_tmts_repair_list/', responsible_tmts_repair_list_view, name='responsible_tmts_repair_list'),
    path('responsible_tmts_repair_search_list/', responsible_tmts_repair_search_list_view, name='responsible_tmts_repair_search_list'),# search (не добавлял область поиска)
    path('responsible_tmts_repair_create/', responsible_tmts_repair_create_view, name='responsible_tmts_repair_create'),    
    # path('responsible_tmts_repair_/<int:id>/', responsible_tmts_repair_detail_view, name='responsible_tmts_repair_detail'),
    # path('responsible_tmts_repair_update/<int:id>/', responsible_tmts_repair_update_view, name='responsible_tmts_repair_update'),
    path('responsible_tmts_repair_delete/<int:id>/', responsible_tmts_repair_delete_view, name='responsible_tmts_repair_delete'),
    
    
    # Reestr_TMTS_repair_Model    
    path('reestr_tmts_repair_add_entry/<tmts_id>/', reestr_tmts_repair_add_entry, name='reestr_tmts_repair_add_entry'),  # записи Reestr_TMTS_Model в статус "в ремонте"  
    path('reestr_tmts_repair_create/<tmts_id>/', reestr_tmts_repair_create_view, name='reestr_tmts_repair_create'),
    path('reestr_tmts_repair_list/', reestr_tmts_repair_list_view, name='reestr_tmts_repair_list'),
    path('reestr_tmts_repair_completed/<int:id>/', reestr_tmts_repair_completed_entry, name='reestr_tmts_repair_completed'),    # возврат (удаление) записи Reestr_TMTS_Model из статуса "в ремонте"    
    path('reestr_tmts_repair/<int:id>/', reestr_tmts_repair_detail_view, name='reestr_tmts_repair_detail'),
    path('reestr_tmts_repair_update/<int:id>/', reestr_tmts_repair_update_view, name='reestr_tmts_repair_update'),
    path('export_reestr_tmts_repair_xls/', export_reestr_tmts_repair_xls, name='export_reestr_tmts_repair_xls'),# export_xls
    path('reestr_tmts_repair_search_list/', reestr_tmts_repair_search_list_view, name='reestr_tmts_repair_search_list'),# search


    # Arhiv_Reestr_TMTS_repair_Model
    path('reestr_arhiv_tmts_repair_list/', reestr_arhiv_tmts_repair_list_view, name='reestr_arhiv_tmts_repair_list'),    # только последние 100 записей
    path('export_reestr_arhiv_tmts_repair_xls/', export_reestr_arhiv_tmts_repair_xls, name='export_reestr_arhiv_tmts_repair_xls'),# export_xls
    path('reestr_arhiv_tmts_repair_search_list/', reestr_arhiv_tmts_repair_search_list_view, name='reestr_arhiv_tmts_repair_search_list'),# search (отдельный шаблон, т.к. в listview только последние 100 записей)
    path('reestr_arhiv_tmts_repair_get_by_id/<int:id>/', reestr_arhiv_tmts_repair_get_by_id, name='reestr_arhiv_tmts_repair_get_by_id'),# Получаем записи по-определенному id


    # Image_Reestr_TMTS_repair_Model
    path('reestr_image_tmts_repair_get_by_id/<int:id>/', reestr_image_tmts_repair_get_by_id, name='reestr_image_tmts_repair_get_by_id'),# Получаем записи по-определенному id
    path('reestr_image_tmts_repair_create/<int:id>/', reestr_image_tmts_repair_create_view, name='reestr_image_tmts_repair_create'),
    
    # path('reestr_tmts_repair_create/<tmts_id>/', reestr_tmts_repair_create_view, name='reestr_tmts_repair_create'),
    # path('reestr_image_tmts_repair_list_view/', reestr_image_tmts_repair_list_view, name='reestr_image_tmts_repair_list_view')


    # path('select2/', include('django_select2.urls')),
    # path("reestr_tmts-create/", Reestr_TMTS_Model_View.as_view(), name="reestr_tmts-create"),
    path("reestr_tmts-create-test/", reestr_TMTS_Model_testSearch, name="reestr_tmts_test_search"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




# path('reestr_tmts_repair_/<int:id>/', Reestr_TMTS_repair_Model_Detail.as_view(), name='reestr_tmts_repair_detail'),
# path('reestr_tmts_repair_update/<int:id>/', Reestr_TMTS_repair_Model_Update.as_view(), name='reestr_tmts_repair_update'),
# path('reestr_tmts_repair_list/', Reestr_TMTS_repair_Model_List.as_view(), name='reestr_tmts_repair_list'),
# path('reestr_tmts_repair_create/<tmts_id>/', Reestr_TMTS_repair_Model_Create.as_view(), name='reestr_tmts_repair_create'), # r'^reestr_tmts_repair_create/(?P<tmts_id>\d+)/$'
# path('reestr_tmts_repair_add_entry/<int:id>/', reestr_tmts_repair_add_entry, name='reestr_tmts_repair_add_entry'),  # записи Reestr_TMTS_Model в статус "в ремонте"    
# path('reestr_tmts_repair_create/<int:id>/', reestr_tmts_repair_create_view, name='reestr_tmts_repair_create'),
    

# path('reestr_arhiv_tmts_repair_list/', reestr_arhiv_tmts_repair_list_view, name='reestr_arhiv_tmts_repair_list'),    # только последние 100 записей



"""
    # Base_Search_Container_Model
    path('base_search_container_create/', base_search_container_create_view, name='base_search_container_create'),
    path('base_search_container_list/', base_search_container_list_view, name='base_search_container_list'),
    path('base_search_container/<int:id>/', base_search_container_detail_view, name='base_search_container_detail'),
    path('base_search_container_update/<int:id>/', base_search_container_update_view, name='base_search_container_update'),
    path('base_search_container_delete/<int:id>/', base_search_container_delete_view, name='base_search_container_delete'),
"""