# -*- coding: UTF-8 -*-

from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView
from django.http import Http404, HttpResponse, HttpRequest
from .models import *
from .forms import *
import datetime
import codecs
import csv

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import xlwt

import ldap
from django_auth_ldap.backend import LDAPBackend #, populate_user

from django.contrib import messages

from django.db.models import Q
from django.db.models.functions import Lower

from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
from .tables import Reestr_TMTS_Model_Table

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page

from django.contrib.auth.decorators import login_required, permission_required

from django.core.files.storage import FileSystemStorage

import django_tables2

from .filters import *

from django_filters.views import FilterView


# ***********************************************************************************************************************************************************
# Index

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def index(request):    
    
    title_text = "Index"
    context = {
            'user_login': request.user,
            # 'form': form,
            'title_text':title_text,
            # 'url_return_to_the_list':'status_printers_list',
        }    
    
    return render(request, 'base_project.html', context)



def select_user_data_ldap(user_name):

    try:
        lconn = ldap.initialize('ldap://site.ru')   # домен
        lconn.protocol_version = ldap.VERSION3  # версия протокола
        lconn.set_option(ldap.OPT_REFERRALS, 0) # не используем рефералы
        lconn.simple_bind_s('ldap@site.ru','password')  # учетные данные
        # print('Connect to AD succesfull')

        base = "dc=site,dc=ru"  # начальный контейнер, с которого начинаем поиск объектов
       
        scope = ldap.SCOPE_SUBTREE  # область поиска, SCOPE_SUBTREE - ищем в дочерних объектах
        
        filter = "(&(sAMAccountName=%s))" % user_name  # фильтр, ищем объекты
        
        # filter = "(&(objectcategory=person))"   # фильтр, ищем объекты "person" (пользователи)
        # filter = "(&(mail=*))"   # фильтр, ищем объекты
        # attrs = ['displayname','title']     # атрибуты искомых объектов        
        # attrs = ['mail','proxyAddresses']     # атрибуты искомых объектов
        attrs = ['displayname','title','mail','sAMAccountName','givenName', 'company', 'extensionAttribute2', 'mobile', 'telephoneNumber']     # атрибуты искомых объектов ('displayname','title','mail','sAMAccountName','givenName')

        result_set = []     # массив с полученным результатом

        ldap_result_id = lconn.search_ext(base, scope, filter, attrs)   # идентификатор поиска объектов в каталоге

        try:
            while 1:
                result_type, result_data = lconn.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:                        
                        # result_set.append(result_data)

                        # print("*"*55)
                        # print(result_data)
                        # print("*"*55)

                        fio = result_data[0][0].split(',')[0].split('=')[1] 
                        login = result_data[0][1].get('sAMAccountName')[0].decode("utf-8")
                        mail =  "" if result_data[0][1].get('mail', "") == "" else result_data[0][1].get('mail')[0].decode("utf-8")
                        distinguishedName = result_data[0][0]
                        company = "" if result_data[0][1].get('company', "") == "" else result_data[0][1].get('company')[0].decode("utf-8")
                        company_position = "" if result_data[0][1].get('extensionAttribute2', "") == "" else result_data[0][1].get('extensionAttribute2')[0].decode("utf-8")
                        mobile = "" if result_data[0][1].get('mobile', "") == "" else result_data[0][1].get('mobile')[0].decode("utf-8")
                        telephoneNumber = "" if result_data[0][1].get('telephoneNumber', "") == "" else result_data[0][1].get('telephoneNumber')[0].decode("utf-8")
                        
                        result_set.append({"fio":fio, "login":login, "mail":mail, "distinguishedName":distinguishedName,
                                           "company":company, "company_position":company_position,
                                           "mobile":mobile, "telephoneNumber":telephoneNumber,})

        except ldap.SIZELIMIT_EXCEEDED:
            print("ldap.SIZELIMIT_EXCEEDED")


        # for item in result_set:
        #     print(item)
        
        return result_set
    
    except ldap.SERVER_DOWN:
        print('Error connection to AD')

    



# ***********************************************************************************************************************************************************
# Type_TMTS_Model / Тип оборудования

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_type_tmts_model', raise_exception=True)
def type_tmts_create_view(request):
    title_text = "Тип оборудования (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Type_TMTS_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('type_tmts_list')
    else:
        form =Type_TMTS_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'type_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_type_tmts_model', raise_exception=True)
def type_tmts_list_view(request):
    form = Type_TMTS_Form()

    # Получаем все записи
    dataset = Type_TMTS_Model.objects.all()    

    title_text = "Тип оборудования (список записей)"

    context = {
            'user_login': request.user,
            'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/type_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_type_tmts_model', raise_exception=True)
def type_tmts_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Type_TMTS_Model.objects.get(id=id)
        title_text = "Тип оборудования"
    except Type_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/type_tmts_detailview.html', {'data': data, 'title_text': title_text,'user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_type_tmts_model', raise_exception=True)
def type_tmts_update_view(request, id):
    try:
        old_data = get_object_or_404(Type_TMTS_Model, id=id)
        title_text = "Тип оборудования (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Type_TMTS_Form(request.POST, instance=old_data)
        if form.is_valid():
            form.save()
            return redirect(f'/laptop/type_tmts/{id}')
    else:
        form = Type_TMTS_Form(instance = old_data)
    context ={
            'user_login': request.user,
            'form':form,
            'title_text':title_text,
            'url_return_to_the_list':'type_tmts_list',
        }
    return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_type_tmts_model', raise_exception=True)
def type_tmts_delete_view(request, id):
    try:
        data = get_object_or_404(Type_TMTS_Model, id=id)
        title_text = "Тип оборудования (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('type_tmts_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'type_tmts_list','user_login': request.user,})


# ***********************************************************************************************************************************************************
# Name_TMTS_Model / Модели ТМЦ

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_name_tmts_model', raise_exception=True)    
def name_tmts_create_view(request):
    title_text = "Модели ТМЦ (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Name_TMTS_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('name_tmts_list')
    else:
        form =Name_TMTS_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'name_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_name_tmts_model', raise_exception=True)
def name_tmts_list_view(request):
    form = Name_TMTS_Form()

    # Получаем все записи
    dataset = Name_TMTS_Model.objects.all().select_related("type_TMTS",)

    # dataset_nameCol = Name_TMTS_Model._meta.get_fields()  
    # dataset_nameCol = [f.name for f in Name_TMTS_Model._meta.fields]  

    title_text = "Модели ТМЦ (список записей)"

    # user_login = request.user
    # print(user_login)

    context = {
            'user_login': request.user,
            'form': form,
            'dataset': dataset,
            # 'dataset_nameCol': dataset_nameCol,
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/name_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_name_tmts_model', raise_exception=True)
def name_tmts_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Name_TMTS_Model.objects.get(id=id)
        title_text = "Модель ТМЦ"
    except Name_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/name_tmts_detailview.html', {'data': data, 'title_text': title_text,'user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_name_tmts_model', raise_exception=True)
def name_tmts_update_view(request, id):
    try:
        old_data = get_object_or_404(Name_TMTS_Model, id=id)
        title_text = "Модели ТМЦ (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Name_TMTS_Form(request.POST, instance=old_data)
        if form.is_valid():
            form.save()
            return redirect(f'/laptop/name_tmts/{id}')
    else:
        form = Name_TMTS_Form(instance = old_data)
    context ={
            'user_login': request.user,
            'form':form,
            'title_text':title_text,
            'url_return_to_the_list':'name_tmts_list',
        }
    return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_name_tmts_model', raise_exception=True)
def name_tmts_delete_view(request, id):
    try:
        data = get_object_or_404(Name_TMTS_Model, id=id)
        title_text = "Модели ТМЦ (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('name_tmts_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'name_tmts_list','user_login': request.user,})
    


# ***********************************************************************************************************************************************************
# Owner_TMTS_Model / Владелецы ТМЦ

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_owner_tmts_model', raise_exception=True)
def owner_tmts_create_view(request):
    title_text = "Владелецы ТМЦ (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Owner_TMTS_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('owner_tmts_list')
    else:
        form =Owner_TMTS_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'owner_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_owner_tmts_model', raise_exception=True)
def owner_tmts_list_view(request):
    form = Owner_TMTS_Form()

    # Получаем все записи
    dataset = Owner_TMTS_Model.objects.all()    

    title_text = "Владелецы ТМЦ (список записей)"

    context = {
            'user_login': request.user,
            'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/owner_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_owner_tmts_model', raise_exception=True)
def owner_tmts_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Owner_TMTS_Model.objects.get(id=id)
        title_text = "Владелец ТМЦ"
    except Owner_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/owner_tmts_detailview.html', {'data': data, 'title_text': title_text,'user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_owner_tmts_model', raise_exception=True)
def owner_tmts_update_view(request, id):
    try:
        old_data = get_object_or_404(Owner_TMTS_Model, id=id)
        title_text = "Владелецы ТМЦ (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Owner_TMTS_Form(request.POST, instance=old_data)
        if form.is_valid():
            form.save()
            return redirect(f'/laptop/owner_tmts/{id}')
    else:
        form = Owner_TMTS_Form(instance = old_data)
    context ={
            'form':form,
            'user_login': request.user,
            'title_text':title_text,
            'url_return_to_the_list':'owner_tmts_list',
        }
    return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_owner_tmts_model', raise_exception=True)
def owner_tmts_delete_view(request, id):
    try:
        data = get_object_or_404(Owner_TMTS_Model, id=id)
        title_text = "Владелецы ТМЦ (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('owner_tmts_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'owner_tmts_list','user_login': request.user,})
    

# ***********************************************************************************************************************************************************
# Responsible_TMTS_Model / Ответственные за ТМЦ

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_responsible_tmts_model', raise_exception=True)
def responsible_tmts_create_view(request):
    title_text = "Ответственные за ТМЦ (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Responsible_TMTS_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('responsible_tmts_list')
    else:
        form =Responsible_TMTS_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'responsible_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_responsible_tmts_model', raise_exception=True)
def responsible_tmts_list_view(request):
    form = Responsible_TMTS_Form()

    # Получаем все записи
    dataset = Responsible_TMTS_Model.objects.all()    

    count_dataset = dataset.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages) 

    title_text = "Ответственные за ТМЦ (список записей)"

    context = {
            'user_login': request.user,
            'form': form,
            'dataset': dataset,   
            'count_dataset': count_dataset,         
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/responsible_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_responsible_tmts_model', raise_exception=True)
def responsible_tmts_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')

        # lower_name = Reestr_TMTS_Model.objects.annotate(lower_name=Lower('owner_TMTS__name_legal_entity'))
        # lower_name.filter(lower_name__icontains=query)       
        # dataset = lower_name.filter(lower_name__icontains=query)
        
        dataset = Responsible_TMTS_Model.objects.filter(
                                                    Q(fio__icontains=query)|
                                                    Q(account__icontains=query)|                                                    
                                                    Q(email__icontains=query)|
                                                    Q(distingished_name__icontains=query)|
                                                    Q(company__icontains=query)|
                                                    Q(company_position__icontains=query)|
                                                    Q(mobile__icontains=query)|
                                                    Q(telephone_number__icontains=query)
                                                   )
        
        count_dataset = dataset.count()

        # page = request.GET.get('page', 1)
        # paginator = Paginator(dataset, 5)  #  paginate_by 5
        # try:
        #     dataset = paginator.page(page)
        # except PageNotAnInteger:
        #     dataset = paginator.page(1)
        # except EmptyPage:
        #     dataset = paginator.page(paginator.num_pages) 
        
    title_text = "Ответственные за ТМЦ (поиск записей)"

    context = {
            'user_login': request.user,
            'dataset': dataset,       
            'count_dataset': count_dataset,       
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/responsible_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_responsible_tmts_model', raise_exception=True)
def responsible_tmts_get_reestr_tmts(request, id):    

    try:
        data_responsible_tmts = get_object_or_404(Responsible_TMTS_Model, id=id)
        # Получаем записи по-определенному id
        dataset = Reestr_TMTS_Model.objects.filter(responsible_TMTS=data_responsible_tmts).exclude(archived=True)
        
        count_dataset = dataset.count()

        page = request.GET.get('page', 1)
        paginator = Paginator(dataset, 5)  #  paginate_by 5
        try:
            dataset = paginator.page(page)
        except PageNotAnInteger:
            dataset = paginator.page(1)
        except EmptyPage:
            dataset = paginator.page(paginator.num_pages) 

    except Responsible_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует')

    title_text = data_responsible_tmts.fio + " ("+ data_responsible_tmts.account +")"

    context = {
            'user_login': request.user,
            'dataset': dataset,   
            'count_dataset': count_dataset,          
            'title_text':title_text,
            'url_return_to_the_list': 'responsible_tmts_list',
            
        }    
    return render(request, 'laptop/responsible_tmts__reestr_tmts_listview.html', context)



# def responsible_tmts_get_reestr_tmts(request, id):
#     dataset=[]

#     if request.method =='GET':
#         try:
#             data_responsible_tmts = get_object_or_404(Responsible_TMTS_Model, id=id)
#             # Получаем записи по-определенному id
#             dataset = Reestr_TMTS_Model.objects.filter(responsible_TMTS=data_responsible_tmts).exclude(archived=True)
            
#             print(dataset)        

#             # return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')    
            
#         except Responsible_TMTS_Model.DoesNotExist:
#             raise Http404('Такой записи не существует') 
    

#     title_text = "Реестр ТМЦ (список записей)"
#     context = {       
#             'user_login': request.user,     
#             'dataset': dataset,            
#             'title_text':title_text,            
#         }     
#     return render(request, 'laptop/reestr_tmts_list_view.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_responsible_tmts_model', raise_exception=True)
def responsible_tmts_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Responsible_TMTS_Model.objects.get(id=id)
        title_text = "Ответственный за ТМЦ"
    except Responsible_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/responsible_tmts_detailview.html', {'data': data, 'title_text': title_text,'user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_responsible_tmts_model', raise_exception=True)
def responsible_tmts_update_view(request, id):
    try:
        old_data = get_object_or_404(Responsible_TMTS_Model, id=id)
        title_text = "Ответственные за ТМЦ (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Responsible_TMTS_Form(request.POST, instance=old_data)
        if form.is_valid():
            form.save()
            return redirect(f'/laptop/responsible_tmts/{id}')
    else:
        form = Responsible_TMTS_Form(instance = old_data)
    context ={
            'user_login': request.user,
            'form':form,
            'title_text':title_text,
            'url_return_to_the_list':'responsible_tmts_list',
        }
    return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_responsible_tmts_model', raise_exception=True)
def responsible_tmts_delete_view(request, id):
    try:
        data = get_object_or_404(Responsible_TMTS_Model, id=id)
        title_text = "Ответственные за ТМЦ (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('responsible_tmts_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'responsible_tmts_list','user_login': request.user,})
    

# ***********************************************************************************************************************************************************
# Reestr_TMTS_Model / Учет ТМЦ

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_reestr_tmts_model', raise_exception=True)
def reestr_tmts_create_view(request):
    title_text = "Учет ТМЦ (добавление записи)"
    # user_login = request.user

    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Reestr_TMTS_Form(request.POST)

        # Проверяем правильность введенных данных и сохраняем в базу        
        if form.is_valid():

            form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)

            # print(form.instance.username_responsible_TMTS)

            if form.instance.username_responsible_TMTS != '': # пустое поле "username_responsible_TMTS"
            
                result_user_data = select_user_data_ldap(form.instance.username_responsible_TMTS)   # получаем информацию из AD по имени пользователя
                
                # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
                if result_user_data != []:

                    # добавляемые данные (Производитель|Модель, S/N) присутствуют в БД                       
                    if Reestr_TMTS_Model.objects.filter(serial_number=request.POST['serial_number'], name_TMTS=request.POST['name_TMTS']).exists(): 
                        
                        form =Reestr_TMTS_Form(request.POST)
                        messages.error(request, 'Ошибка! Уже существует запись в БД с такими же значениями в полях "Производитель|Модель" и "S/N". \
                                    Проверьте за кем закреплено данное ТМЦ и, при необходимости, внесите требуемые изменения.')
                        messages.error(request, form.errors)


                    else: # добавляемые данные (Производитель|Модель, S/N) отсутствуют в БД
                        
                        # если 'Ответственный за ТМЦ' уже существует
                        if Responsible_TMTS_Model.objects.filter(account__iexact=form.instance.username_responsible_TMTS.lower()).exists():
                            try:
                                # обновляем запись (возможна смена фамилии/должности)                        
                                responsible_tmts = get_object_or_404(Responsible_TMTS_Model, account__iexact=form.instance.username_responsible_TMTS.lower())                            

                                responsible_tmts.fio = result_user_data[0]['fio']
                                # responsible_tmts.account = result_user_data[0]['login']
                                responsible_tmts.email = result_user_data[0]['mail']
                                responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                                responsible_tmts.company = result_user_data[0]['company']
                                responsible_tmts.company_position = result_user_data[0]['company_position']
                                responsible_tmts.mobile = result_user_data[0]['mobile']
                                responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                                responsible_tmts.save()
                            except Responsible_TMTS_Model.DoesNotExist:
                                raise Http404('Такой записи не существует')
                            
                        else:   # 'Ответственный за ТМЦ' не существует в БД
                            # создаем объект Responsible_TMTS_Model 
                            responsible_tmts = Responsible_TMTS_Model()

                            responsible_tmts.fio = result_user_data[0]['fio']
                            responsible_tmts.account = result_user_data[0]['login']
                            responsible_tmts.email = result_user_data[0]['mail']
                            responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                            responsible_tmts.company = result_user_data[0]['company']
                            responsible_tmts.company_position = result_user_data[0]['company_position']
                            responsible_tmts.mobile = result_user_data[0]['mobile']
                            responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                            responsible_tmts.save()
                
                        form.instance.responsible_TMTS = responsible_tmts   # сохраняем полученный объект Responsible_TMTS_Model
                        
                        result_object = form.save()

                        # ---------------------------------------------------------------------------
                        # логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
                        # created_dateTime=datetime.datetime.now()
                        # updated_dateTime=datetime.datetime.now()
                        action = 'создание'                    
                        create_user = request.user
                        # reestr_tmts_logging_CRUD_operations(result_object, created_dateTime, updated_dateTime, action, create_user)
                        reestr_tmts_logging_CRUD_operations(result_object, action, create_user)
                        # ---------------------------------------------------------------------------

                        # messages.success(request, "Запись успешно записана в БД.")

                        # переадресуем на главную страницу
                        return redirect('reestr_tmts_list')            
                    
                else:
                    # form.add_error('__all__', 'Ошибка! Проверьте правильность логина и пароля.')
                    form =Reestr_TMTS_Form(request.POST)
                    messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                    messages.error(request, form.errors)
                    # print('Ошибка! Проверьте правильность учетной записи.')
            
            # заведение на склад, пустое поле "username_responsible_TMTS"
            else:
                
                # добавляемые данные (Производитель|Модель, S/N) присутствуют в БД                       
                if Reestr_TMTS_Model.objects.filter(serial_number=request.POST['serial_number'], name_TMTS=request.POST['name_TMTS']).exists():
                    form =Reestr_TMTS_Form(request.POST)
                    messages.error(request, 'Ошибка! Уже существует запись в БД с такими же значениями в полях "Производитель|Модель" и "S/N". \
                                    Проверьте за кем закреплено данное ТМЦ и, при необходимости, внесите требуемые изменения.')
                    messages.error(request, form.errors)

                else: # добавляемые данные (Производитель|Модель, S/N) отсутствуют в БД

                    data_tmts_status_sklad = get_object_or_404(Status_TMTS_Model, id=3)
                    form.instance.status = data_tmts_status_sklad # меняем статус на "на складе"

                    result_object = form.save()

                    # ---------------------------------------------------------------------------
                    # логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model                        
                    action = 'создание'                    
                    create_user = request.user                        
                    reestr_tmts_logging_CRUD_operations(result_object, action, create_user)
                    # ---------------------------------------------------------------------------
                    # messages.success(request, "Запись успешно записана в БД.")

                    # переадресуем на главную страницу
                    return redirect('reestr_tmts_list')
                    
        else:
            form =Reestr_TMTS_Form(request.POST)
            # messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
            messages.error(request, form.errors)

    else:
        form =Reestr_TMTS_Form()
    
    context = {
            'user_login': request.user,          
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# @login_required
# @permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_list_view(request):
    # form = Reestr_TMTS_Form()

    # Получаем все записи
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account").exclude(archived=True)
    
    count_dataset = dataset.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages) 

    title_text = "Учет ТМЦ (список записей)"

    # for row in dataset:
    #     print("---")
    #     print(row.status)

    context = {
            # 'form': form,
            'user_login': request.user,
            'dataset': dataset,
            'count_dataset': count_dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/reestr_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_list_view_filter(request):
    # form = Reestr_TMTS_Form()

    # Получаем все записи
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account").exclude(archived=True)

    dataset_filter = Reestr_TMTS_Model_Filter(request.GET, queryset=dataset)
    
    count_dataset = dataset_filter.qs.count()    

    title_text = "Учет ТМЦ (список записей)"

    dataset = dataset_filter.qs    
    paginator = Paginator(dataset_filter.qs, 5)  #  paginate_by 5

    # page = request.GET.get('page', 1)
    page_number = request.GET.get('page')

    try:
        dataset = paginator.page(page_number)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages)         
 

    context = {
            # 'form': form,
            'user_login': request.user,
            'dataset': dataset,
            'count_dataset': count_dataset,            
            'title_text':title_text,
            'filter': dataset_filter,            
        }
    return render(request, 'laptop/reestr_tmts_listview_filter.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_archived_list_view(request):

    # Получаем все архивные записи
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account").exclude(archived=False)  

    count_dataset = dataset.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages) 

    title_text = "Утилизация ТМЦ (список записей)"   

    context = {  
            'user_login': request.user,          
            'dataset': dataset, 
            'count_dataset': count_dataset,           
            'title_text':title_text,            
        }    
    return render(request, 'laptop/reestr_tmts_archived_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Reestr_TMTS_Model.objects.get(id=id)
        title_text = "Учет ТМЦ"
    except Reestr_TMTS_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/reestr_tmts_detailview.html', {'data': data, 'title_text': title_text,'user_login': request.user,})
   

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_reestr_tmts_model', raise_exception=True)
def reestr_tmts_delete_view(request, id):
    try:
        data = get_object_or_404(Reestr_TMTS_Model, id=id)
        title_text = "Учет ТМЦ (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':




        try:
            data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)               

            # если статус не равен "в ремонте"
            if data.status != data_tmts_status_repair:


                # ---------------------------------------------------------------------------
                # логируем операцию удаления записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
                # created_dateTime=datetime.datetime.now()
                # updated_dateTime=datetime.datetime.now()
                action = 'удаление'        
                delete_user = request.user
                # reestr_tmts_logging_CRUD_operations(data, created_dateTime, updated_dateTime, action, delete_user)
                reestr_tmts_logging_CRUD_operations(data, action, delete_user)
                # ---------------------------------------------------------------------------

                data.delete()
                return redirect('reestr_tmts_list')            
            else:
                messages.error(request, 'Ошибка! Данная запись в статусе "в ремонте". Удаление возможно записей в статусах "в работе" и "на складе".')               
                # переадресуем на страницу
                return redirect('reestr_tmts_list')
            
        except Exception:
            raise Http404('Статуса "в ремонте" не существует')        
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'reestr_tmts_list','user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_reestr_tmts_model', raise_exception=True)
def reestr_tmts_update_view(request, id):
    try:
        old_data = get_object_or_404(Reestr_TMTS_Model, id=id)
        title_text = "Учет ТМЦ (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Reestr_TMTS_Form(request.POST, instance=old_data)

        # if form.is_valid():
        #     form.save()
        #     return redirect(f'/laptop/reestr_tmts_/{id}')       



        # Проверяем правильность введенных данных и сохраняем в базу        
        if form.is_valid():

            form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)



            # добавляемые данные (Производитель|Модель, S/N) присутствуют в БД                       
            if Reestr_TMTS_Model.objects.filter(serial_number=request.POST['serial_number'], name_TMTS=request.POST['name_TMTS']).exclude(id=id).exists():
                # print("if Reestr_TMTS_Model.objects.filter(serial_number=request.POST['serial_number'], name_TMTS=request.POST['name_TMTS']).exclude(id=request.POST['id']).exists():")
                        
                form =Reestr_TMTS_Form(request.POST, instance=old_data)
                messages.error(request, 'Ошибка! Уже существует запись в БД с такими же значениями в полях "Производитель|Модель" и "S/N". \
                                   Проверьте за кем закреплено данное ТМЦ и, при необходимости, внесите требуемые изменения.')
                messages.error(request, form.errors)

            else: # добавляемые данные (Производитель|Модель, S/N) отсутствуют в БД

                

                if form.instance.username_responsible_TMTS != '': 
                    # print("if form.instance.username_responsible_TMTS != "":")
                    result_user_data = select_user_data_ldap(form.instance.username_responsible_TMTS)   # получаем информацию из AD по имени пользователя
                
                    # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
                    if result_user_data != []:
                        # print("if result_user_data != []:")                        

                        # если 'Ответственный за ТМЦ' уже существует
                        if Responsible_TMTS_Model.objects.filter(account__iexact=form.instance.username_responsible_TMTS.lower()).exists():
                            # print("if Responsible_TMTS_Model.objects.filter(account=form.instance.username_responsible_TMTS).exists()")
                                
                            try:
                                # обновляем запись (возможна смена фамилии/должности)                        
                                responsible_tmts = get_object_or_404(Responsible_TMTS_Model, account__iexact=form.instance.username_responsible_TMTS.lower())

                                responsible_tmts.fio = result_user_data[0]['fio']
                                # responsible_tmts.account = result_user_data[0]['login']
                                responsible_tmts.email = result_user_data[0]['mail']
                                responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                                responsible_tmts.company = result_user_data[0]['company']
                                responsible_tmts.company_position = result_user_data[0]['company_position']
                                responsible_tmts.mobile = result_user_data[0]['mobile']
                                responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                                responsible_tmts.save()
                            except Responsible_TMTS_Model.DoesNotExist:
                                raise Http404('Такой записи не существует')
                                    
                        else:   # 'Ответственный за ТМЦ' не существует в БД
                            # print("else:   # 'Ответственный за ТМЦ' не существует в БД")
                                
                            # создаем объект Responsible_TMTS_Model 
                            responsible_tmts = Responsible_TMTS_Model()

                            responsible_tmts.fio = result_user_data[0]['fio']
                            responsible_tmts.account = result_user_data[0]['login']
                            responsible_tmts.email = result_user_data[0]['mail']
                            responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                            responsible_tmts.company = result_user_data[0]['company']
                            responsible_tmts.company_position = result_user_data[0]['company_position']
                            responsible_tmts.mobile = result_user_data[0]['mobile']
                            responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                            responsible_tmts.save()
                        
                        form.instance.responsible_TMTS = responsible_tmts   # сохраняем полученный объект Responsible_TMTS_Model
                        
                        # меняем статус, если "на складе"
                        try:
                            data_tmts_status_sklad = get_object_or_404(Status_TMTS_Model, id=3)
                            data_tmts_status_job = get_object_or_404(Status_TMTS_Model, id=1)            
                        
                            if form.instance.status == data_tmts_status_sklad:
                                form.instance.status = data_tmts_status_job
                        except Exception:
                            raise Http404('Статуса "на складе" или "в работе" не существует')
                        

                                
                        result_data = form.save()

                        # ---------------------------------------------------------------------------
                        # логируем операцию   
                        action = 'изменение'
                        update_user = request.user
                        reestr_tmts_logging_CRUD_operations(result_data, action, update_user)
                        # ---------------------------------------------------------------------------
                                
                        # messages.success(request, "Запись успешно записана в БД.")

                        # переадресуем на страницу
                        return redirect(f'/laptop/reestr_tmts_/{id}') 

                    else:
                        # print("else1")
                        
                        form =Reestr_TMTS_Form(request.POST, instance=old_data)
                        messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                        messages.error(request, form.errors)

                else:
                    # print("else2")
                    
                    try:
                        data_tmts_status_job = get_object_or_404(Status_TMTS_Model, id=1) # в работе
                        data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2) # "в ремонте"
                        data_tmts_status_sklad = get_object_or_404(Status_TMTS_Model, id=3) # "на складе"
                        
                        if form.instance.status == data_tmts_status_job: # если в работе, то на склад
                            form.instance.status = data_tmts_status_sklad                        
                        
                    except Exception:
                        raise Http404('Статуса "в работе" не существует') 



                    
                    # "снимаем" с пользователя данное ТМЦ
                    form.instance.responsible_TMTS=None


                    result_data = form.save()       

                    # ---------------------------------------------------------------------------
                    # логируем операцию 
                    action = 'изменение'                        
                    update_user = request.user
                    reestr_tmts_logging_CRUD_operations(result_data, action, update_user)
                    # ---------------------------------------------------------------------------

                    # messages.success(request, "Запись успешно записана в БД.")
                    # переадресуем на страницу
                    return redirect(f'/laptop/reestr_tmts_/{id}')
            
        
        else:
            # print("else3")
            
            form =Reestr_TMTS_Form(request.POST, instance=old_data)   
            # messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')         
            messages.error(request, form.errors)

    else:
        form = Reestr_TMTS_Form(instance = old_data)
    context ={
            'form':form,
            'user_login': request.user,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_list',
        }
    return render(request, 'laptop/update.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_reestr_tmts_model', raise_exception=True)
def reestr_tmts_return_to_sklad(request, id):

    try:
        data = get_object_or_404(Reestr_TMTS_Model, id=id)
        title_text = "Учет ТМЦ (возврат на склад)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':

        try:
            data_tmts_status_sklad = get_object_or_404(Status_TMTS_Model, id=3) 
            data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)
            data_tmts_status_job = get_object_or_404(Status_TMTS_Model, id=1)           

            # если статус равен "в работе"
            if data.status == data_tmts_status_job:
                # # ---------------------------------------------------------------------------
                # # логируем операцию смены статуса на "на складе" и добавления ее в Arhiv_Reestr_TMTS_Model        
                # action = 'на склад'                        
                # update_user = request.user
                # reestr_tmts_logging_CRUD_operations(data, action, update_user)
                # # ---------------------------------------------------------------------------                
                
                data.status = data_tmts_status_sklad # меняем статус на "на складе"

                data.username_responsible_TMTS='' # "снимаем" с пользователя данное ТМЦ
                data.responsible_TMTS=None # "снимаем" с пользователя данное ТМЦ                
                    
                data.save()

                # ---------------------------------------------------------------------------
                # логируем операцию смены статуса на "на складе" и добавления ее в Arhiv_Reestr_TMTS_Model        
                action = 'на склад'                        
                update_user = request.user
                reestr_tmts_logging_CRUD_operations(data, action, update_user)
                # ---------------------------------------------------------------------------

                return redirect(f'/laptop/reestr_tmts_/{id}')
            
            elif data.status == data_tmts_status_repair:
                messages.error(request, 'Ошибка! Данная запись в статусе "в ремонте" и может быть возвращена на склад только из реестра "Ремонт/обслуживание ТМЦ".')               
                # переадресуем на страницу
                return redirect('reestr_tmts_list')
                        
            else:
                messages.error(request, 'Ошибка! Данная запись уже в статусе "на складе".')               
                # переадресуем на страницу
                return redirect('reestr_tmts_list')
            
        except Exception:
            raise Http404('Статуса "на складе" не существует')                
        
    else:
        return render(request, 'laptop/return_tmts_to_sklad.html', {'title_text':title_text,'url_return_to_the_list':'reestr_tmts_list','user_login': request.user,})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')

        # lower_name = Reestr_TMTS_Model.objects.annotate(lower_name=Lower('owner_TMTS__name_legal_entity'))
        # lower_name.filter(lower_name__icontains=query)       
        # dataset = lower_name.filter(lower_name__icontains=query)
        
        dataset = Reestr_TMTS_Model.objects.filter(
                                                    Q(status__status__icontains=query)|
                                                    Q(owner_TMTS__name_legal_entity__icontains=query)|
                                                    # Q(owner_TMTS__name_legal_entity__istartswith=query)|
                                                    # Q(owner_TMTS__name_legal_entity__iexact=query)|                                                                                                        
                                                    # Q((lower_owner_TMTS__name_legal_entity__icontains=query).extra(select={'lower_owner_TMTS__name_legal_entity':Lower('owner_TMTS__name_legal_entity')}))|
                                                    Q(name_TMTS__type_TMTS__type_tmts__icontains=query)|
                                                    Q(name_TMTS__manufacturer__icontains=query)|
                                                    Q(name_TMTS__name_model__icontains=query)|
                                                    Q(serial_number__icontains=query)|
                                                    Q(responsible_TMTS__fio__icontains=query)|
                                                    Q(responsible_TMTS__account__icontains=query)|
                                                    Q(responsible_TMTS__company__icontains=query)|
                                                    Q(responsible_TMTS__company_position__icontains=query)|
                                                    #    Q(responsible_TMTS__mobile__icontains=query)|
                                                    #    Q(responsible_TMTS__telephone_number__icontains=query)|                                                   
                                                    Q(location__icontains=query)|
                                                    Q(creator_account__username__icontains=query)|
                                                    Q(comment__icontains=query)|
                                                    Q(start_of_operation_TMTS__icontains=query)
                                                   ).select_related("status","owner_TMTS","name_TMTS","responsible_TMTS").exclude(archived = True)
        
        count_dataset = dataset.count()
        
    title_text = "Учет ТМЦ (поиск записей)"

    context = {
            'user_login': request.user,
            'dataset': dataset,
            'count_dataset': count_dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/reestr_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def reestr_tmts_archived_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')

        # lower_name = Reestr_TMTS_Model.objects.annotate(lower_name=Lower('owner_TMTS__name_legal_entity'))
        # lower_name.filter(lower_name__icontains=query)       
        # dataset = lower_name.filter(lower_name__icontains=query)
        
        dataset = Reestr_TMTS_Model.objects.filter(
                                                    Q(status__status__icontains=query)|
                                                    Q(owner_TMTS__name_legal_entity__icontains=query)|
                                                    # Q(owner_TMTS__name_legal_entity__istartswith=query)|
                                                    # Q(owner_TMTS__name_legal_entity__iexact=query)|                                                                                                        
                                                    # Q((lower_owner_TMTS__name_legal_entity__icontains=query).extra(select={'lower_owner_TMTS__name_legal_entity':Lower('owner_TMTS__name_legal_entity')}))|
                                                    Q(name_TMTS__type_TMTS__type_tmts__icontains=query)|
                                                    Q(name_TMTS__manufacturer__icontains=query)|
                                                    Q(name_TMTS__name_model__icontains=query)|
                                                    Q(serial_number__icontains=query)|
                                                    Q(responsible_TMTS__fio__icontains=query)|
                                                    Q(responsible_TMTS__account__icontains=query)|
                                                    Q(responsible_TMTS__company__icontains=query)|
                                                    Q(responsible_TMTS__company_position__icontains=query)|
                                                    #    Q(responsible_TMTS__mobile__icontains=query)|
                                                    #    Q(responsible_TMTS__telephone_number__icontains=query)|                                                   
                                                    Q(location__icontains=query)|
                                                    Q(creator_account__username__icontains=query)|
                                                    Q(comment__icontains=query)|
                                                    Q(start_of_operation_TMTS__icontains=query)
                                                   ).select_related("status","owner_TMTS","name_TMTS","responsible_TMTS").exclude(archived=False)
        
        count_dataset = dataset.count()
        
    title_text = "Утилизация ТМЦ (поиск записей)"

    context = {
            'user_login': request.user,
            'dataset': dataset,
            'count_dataset': count_dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/reestr_tmts_archived_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# export all reestr (Reestr_TMTS_Model)
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def export_reestr_tmts_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_tmts.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('reestr_tmts')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
 
    columns = ['Статус','Владелец ТМЦ','Тип оборудования | Производитель | Модель','S/N','Учетная запись ответственного за ТМЦ',
               'Ответственный за ТМЦ','Локация/Кабинет', 'Дата создания записи','Кем изменено/создано','Дата изменения записи',
               'Комментарий','Дата начала эксплуатации ТМЦ', ]#'Утилизация'
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS").exclude(archived=True)
    for row in dataset:
        rows.append(
            [
            str(row.status),
            str(row.owner_TMTS),    
            str(row.name_TMTS),
            row.serial_number,
            row.username_responsible_TMTS,
            str(row.responsible_TMTS),
            row.location,
            row.created,
            str(row.creator_account),
            row.updated,
            row.comment,
            row.start_of_operation_TMTS,
            # row.archived,            
            ]
        )
    
 
    # rows = Printed_pagesModel.objects.all().values_list('printers_in_service.service_object.service_object_name', 
    #                                                     'printers_in_service.printers.name', 
    #                                                     'printers_in_service.serial_number',
    #                                                     'printers_in_service.ip_address',
    #                                                     'created',
    #                                                     'printed_pages')
    
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# export_reestr_tmts_xls_filter
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def export_reestr_tmts_xls_filter(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_tmts.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('reestr_tmts')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
 
    columns = ['Статус','Владелец ТМЦ','Тип оборудования | Производитель | Модель','S/N','Учетная запись ответственного за ТМЦ',
               'Ответственный за ТМЦ','Локация/Кабинет', 'Дата создания записи','Кем изменено/создано','Дата изменения записи',
               'Комментарий','Дата начала эксплуатации ТМЦ', ]#'Утилизация'
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []

    # dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS").exclude(archived=True)
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account").exclude(archived=True)
    dataset_filter = Reestr_TMTS_Model_Filter(request.GET, queryset=dataset).qs

    print(dataset_filter.count())

    for row in dataset_filter:
        rows.append(
            [
            str(row.status),
            str(row.owner_TMTS),    
            str(row.name_TMTS),
            row.serial_number,
            row.username_responsible_TMTS,
            str(row.responsible_TMTS),
            row.location,
            row.created,
            str(row.creator_account),
            row.updated,
            row.comment,
            row.start_of_operation_TMTS,
            # row.archived,            
            ]
        )
    
 
    # rows = Printed_pagesModel.objects.all().values_list('printers_in_service.service_object.service_object_name', 
    #                                                     'printers_in_service.printers.name', 
    #                                                     'printers_in_service.serial_number',
    #                                                     'printers_in_service.ip_address',
    #                                                     'created',
    #                                                     'printed_pages')
    
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# export all reestr (Reestr_TMTS_Model) _archived_ (Утилизация)
@login_required
@permission_required(perm='laptop.view_reestr_tmts_model', raise_exception=True)
def export_reestr_tmts_archived_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_tmts_utilizacia.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('reestr_tmts')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
 
    columns = ['Статус','Владелец ТМЦ','Тип оборудования | Производитель | Модель','S/N','Учетная запись ответственного за ТМЦ',
               'Ответственный за ТМЦ','Локация/Кабинет', 'Дата создания записи','Кем изменено/создано','Дата изменения записи',
               'Комментарий','Дата начала эксплуатации ТМЦ','Утилизация']
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []
    dataset = Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS").exclude(archived=False)
    for row in dataset:
        rows.append(
            [
            str(row.status),
            str(row.owner_TMTS),    
            str(row.name_TMTS),
            row.serial_number,
            row.username_responsible_TMTS,
            str(row.responsible_TMTS),
            row.location,
            row.created,
            str(row.creator_account),
            row.updated,
            row.comment,
            row.start_of_operation_TMTS,
            row.archived,            
            ]
        )
    
 
    # rows = Printed_pagesModel.objects.all().values_list('printers_in_service.service_object.service_object_name', 
    #                                                     'printers_in_service.printers.name', 
    #                                                     'printers_in_service.serial_number',
    #                                                     'printers_in_service.ip_address',
    #                                                     'created',
    #                                                     'printed_pages')
    
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
# def reestr_tmts_logging_CRUD_operations(data_reestr_TMTS, created_dateTime, updated_dateTime, action, action_user):
def reestr_tmts_logging_CRUD_operations(data_reestr_TMTS, action, action_user):
                            
    # создаем объект Responsible_TMTS_Model 
    arhiv_tmts = Arhiv_Reestr_TMTS_Model()

    # arhiv_tmts.id_reestr_tmts = 'id_' + str(data_reestr_TMTS.id)
    arhiv_tmts.id_reestr_tmts = data_reestr_TMTS.id
    arhiv_tmts.status = str(data_reestr_TMTS.status)
    arhiv_tmts.owner_TMTS = str(data_reestr_TMTS.owner_TMTS)
    arhiv_tmts.name_TMTS = str(data_reestr_TMTS.name_TMTS)
    arhiv_tmts.serial_number = str(data_reestr_TMTS.serial_number)
    arhiv_tmts.username_responsible_TMTS = str(data_reestr_TMTS.username_responsible_TMTS)
    arhiv_tmts.responsible_TMTS = "" if str(data_reestr_TMTS.responsible_TMTS)=="None" else str(data_reestr_TMTS.responsible_TMTS)
    arhiv_tmts.location = str(data_reestr_TMTS.location)
    arhiv_tmts.created_reestr_tmts_model = data_reestr_TMTS.created    
    arhiv_tmts.creator_account = str(data_reestr_TMTS.creator_account)
    arhiv_tmts.updated_reestr_tmts_model = data_reestr_TMTS.updated
    arhiv_tmts.comment = str(data_reestr_TMTS.comment)
    arhiv_tmts.start_of_operation_TMTS = data_reestr_TMTS.start_of_operation_TMTS
    arhiv_tmts.archived = str(data_reestr_TMTS.archived)        
    arhiv_tmts.action = action
    arhiv_tmts.creator_action = str(action_user) #'Кем выполнено'

    arhiv_tmts.save()
    
    
    
    """
    if action=='создание':
        # arhiv_tmts.id_reestr_tmts = str(data_reestr_TMTS.instance.)
        arhiv_tmts.status = str(data_reestr_TMTS.instance.status)
        arhiv_tmts.owner_TMTS = str(data_reestr_TMTS.instance.owner_TMTS)
        arhiv_tmts.name_TMTS = str(data_reestr_TMTS.instance.name_TMTS)
        arhiv_tmts.serial_number = str(data_reestr_TMTS.instance.serial_number)
        arhiv_tmts.username_responsible_TMTS = str(data_reestr_TMTS.instance.username_responsible_TMTS)
        arhiv_tmts.responsible_TMTS = str(data_reestr_TMTS.instance.responsible_TMTS)
        arhiv_tmts.location = str(data_reestr_TMTS.instance.location)
        arhiv_tmts.created_reestr_tmts_model = created_dateTime #item.created    
        arhiv_tmts.creator_account = str(data_reestr_TMTS.instance.creator_account)
        arhiv_tmts.updated_reestr_tmts_model = updated_dateTime #item.updated
        arhiv_tmts.comment = str(data_reestr_TMTS.instance.comment)
        arhiv_tmts.archived = str(data_reestr_TMTS.instance.archived)
        arhiv_tmts.action = action
        arhiv_tmts.creator_action = str(action_user) #'Кем выполнено'
    
    # elif action=='удаление':        
    

    else: # action == 'изменение'/'удаление'
        # arhiv_tmts.status = str(data_reestr_TMTS.instance.status)
        # arhiv_tmts.status = str(data_reestr_TMTS.cleaned_data['status'])
        # arhiv_tmts.status = str(data_reestr_TMTS.get_status_display())
        arhiv_tmts.status = str(data_reestr_TMTS.status)
        arhiv_tmts.owner_TMTS = str(data_reestr_TMTS.owner_TMTS)
        arhiv_tmts.name_TMTS = str(data_reestr_TMTS.name_TMTS)
        arhiv_tmts.serial_number = str(data_reestr_TMTS.serial_number)
        arhiv_tmts.username_responsible_TMTS = str(data_reestr_TMTS.username_responsible_TMTS)
        arhiv_tmts.responsible_TMTS = str(data_reestr_TMTS.responsible_TMTS)
        arhiv_tmts.location = str(data_reestr_TMTS.location)
        arhiv_tmts.created_reestr_tmts_model = data_reestr_TMTS.created    
        arhiv_tmts.creator_account = str(data_reestr_TMTS.creator_account)
        arhiv_tmts.updated_reestr_tmts_model = data_reestr_TMTS.updated
        arhiv_tmts.comment = str(data_reestr_TMTS.comment)
        arhiv_tmts.archived = str(data_reestr_TMTS.archived)        
        arhiv_tmts.action = action
        arhiv_tmts.creator_action = str(action_user) #'Кем выполнено'

    arhiv_tmts.save()
    """

# ***********************************************************************************************************************************************************
# Arhiv_Reestr_TMTS_Model / Учет ТМЦ (архив)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_model', raise_exception=True)
def reestr_arhiv_tmts_list_view(request):    
    # Получаем записи    
    # dataset = Arhiv_Reestr_TMTS_Model.objects.all().order_by('-created')[:100]  

    # Получаем записи
    dataset = Arhiv_Reestr_TMTS_Model.objects.all().order_by('-created')
    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages)


    title_text = 'Учет ТМЦ (история операций)'

    context = {
            'user_login': request.user,
            # 'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_model', raise_exception=True)
def reestr_arhiv_tmts_list_view_filter(request):    
    # Получаем записи    
    # dataset = Arhiv_Reestr_TMTS_Model.objects.all().order_by('-created')[:100]  

    # Получаем записи
    dataset = Arhiv_Reestr_TMTS_Model.objects.all().order_by('-created')

    dataset_filter = Arhiv_Reestr_TMTS_Model_Filter(request.GET, queryset=dataset)    
    count_dataset = dataset_filter.qs.count()    

    dataset = dataset_filter.qs
    
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    page_number = request.GET.get('page')

    
    try:
        dataset = paginator.page(page_number)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages)


    title_text = 'Учет ТМЦ (история операций)'

    context = {
            'user_login': request.user,
            # 'form': form,
            'dataset': dataset,   
            'count_dataset': count_dataset,         
            'title_text':title_text,
            'filter': dataset_filter,
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_listview_filter.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_model', raise_exception=True)
def reestr_arhiv_tmts_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')
        dataset = Arhiv_Reestr_TMTS_Model.objects.filter(
                                                    Q(id_reestr_tmts__icontains=query)|
                                                    Q(status__icontains=query)|
                                                    Q(owner_TMTS__icontains=query)|
                                                    Q(name_TMTS__icontains=query)|
                                                    Q(serial_number__icontains=query)|
                                                    Q(username_responsible_TMTS__icontains=query)|
                                                    Q(responsible_TMTS__icontains=query)|
                                                    Q(location__icontains=query)|
                                                    Q(created_reestr_tmts_model__icontains=query)|
                                                    Q(creator_account__icontains=query)|
                                                    Q(updated_reestr_tmts_model__icontains=query)|
                                                    Q(comment__icontains=query)|
                                                    Q(start_of_operation_TMTS__icontains=query)|
                                                    Q(archived__icontains=query)|
                                                    Q(created__icontains=query)|
                                                    Q(action__icontains=query)|
                                                    Q(creator_action__icontains=query)
                                                   )

    title_text = 'Учет ТМЦ (поиск истории операций)'

    context = {
            'user_login': request.user,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_search_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# export all reestr (Arhiv_Reestr_TMTS_Model)
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_model', raise_exception=True)
def export_reestr_arhiv_tmts_xls(request: HttpRequest):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_arhiv_tmts.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('arhiv_tmts')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
 
    columns = ['№','id оборудования','Статус','Владелец ТМЦ','ТМЦ','S/N','Учетная запись ответственного за ТМЦ','Ответственный за ТМЦ','Локация/Кабинет',
 'Дата создания записи','Кем изменено/создано','Дата изменения записи','Комментарий','Дата начала эксплуатации ТМЦ',
 'Утилизация','Дата действия','Действие','Кем выполнено']
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []
    dataset = Arhiv_Reestr_TMTS_Model.objects.all()
    for row in dataset:
        rows.append(
            [
            row.id,
            row.id_reestr_tmts,
            row.status,
            row.owner_TMTS,    
            row.name_TMTS,
            row.serial_number,
            row.username_responsible_TMTS,
            row.responsible_TMTS,
            row.location,
            row.created_reestr_tmts_model,
            row.creator_account,
            row.updated_reestr_tmts_model,
            row.comment,
            row.start_of_operation_TMTS,
            row.archived,
            row.created,
            row.action,
            row.creator_action,
            ]
        )
    
 
    # rows = Printed_pagesModel.objects.all().values_list('printers_in_service.service_object.service_object_name', 
    #                                                     'printers_in_service.printers.name', 
    #                                                     'printers_in_service.serial_number',
    #                                                     'printers_in_service.ip_address',
    #                                                     'created',
    #                                                     'printed_pages')
    
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response



# ***********************************************************************************************************************************************************
# ***********************************************************************************************************************************************************

# ***********************************************************************************************************************************************************
# Responsible_TMTS_repair_Model / Ответственные за ремонт/обслуживание

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_responsible_tmts_repair_model', raise_exception=True)
def responsible_tmts_repair_list_view(request):
    
    # Получаем все записи
    dataset = Responsible_TMTS_repair_Model.objects.all()
  

    title_text = "Ответственные за ремонт/обслуживание (список записей)"

    context = {
            'user_login': request.user,
            # 'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/responsible_tmts_repair_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_responsible_tmts_repair_model', raise_exception=True)
def responsible_tmts_repair_create_view(request):
    title_text = "Ответственные за ремонт/обслуживание (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Responsible_TMTS_repair_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            result_user_data = select_user_data_ldap(form.instance.account)   # получаем информацию из AD по имени пользователя
                    
            # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
            if result_user_data != []:
                # если 'Ответственный за ремонт' уже существует
                if Responsible_TMTS_repair_Model.objects.filter(account__iexact=form.instance.account.lower()).exists():
                    try:
                        # обновляем запись (возможна смена фамилии/должности)                        
                        responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=form.instance.account.lower())                            

                        responsible_tmts.fio = result_user_data[0]['fio']
                        # responsible_tmts.account = result_user_data[0]['login']
                        responsible_tmts.email = result_user_data[0]['mail']
                        responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                        responsible_tmts.company = result_user_data[0]['company']
                        responsible_tmts.company_position = result_user_data[0]['company_position']
                        responsible_tmts.mobile = result_user_data[0]['mobile']
                        responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                        responsible_tmts.save()
                    except Responsible_TMTS_repair_Model.DoesNotExist:
                        raise Http404('Такой записи не существует')
                
                # 'Ответственный за ремонт' не существует в БД                     
                else:
                    form.instance.fio = result_user_data[0]['fio']
                    # responsible_tmts.account = result_user_data[0]['login']
                    form.instance.email = result_user_data[0]['mail']
                    form.instance.distingished_name = result_user_data[0]['distinguishedName']
                    form.instance.company = result_user_data[0]['company']
                    form.instance.company_position = result_user_data[0]['company_position']
                    form.instance.mobile = result_user_data[0]['mobile']
                    form.instance.telephone_number = result_user_data[0]['telephoneNumber']
                    result_object = form.save()                    
                    
                    # messages.success(request, "Запись успешно записана в БД.")        

                    
                # переадресуем на главную страницу
                return redirect('responsible_tmts_repair_list')

            else:                        
                form = Responsible_TMTS_repair_Form(request.POST)
                messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                messages.error(request, form.errors)
    else:
        form =Responsible_TMTS_repair_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'responsible_tmts_repair_list',
        }        
    return render(request, 'laptop/create.html', context)


# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# def responsible_tmts_repair_detail_view(request, id):
#     try:
#         # Получаем запись по-определенному id
#         data = Responsible_TMTS_repair_Model.objects.get(id=id)
#         title_text = "Ответственный за ремонт/обслуживание "
#     except Responsible_TMTS_repair_Model.DoesNotExist:
#         raise Http404('Такой записи не существует') 
#     return render(request, 'laptop/responsible_tmts_repair_detailview.html', {'data': data, 'title_text': title_text, 'user_login': request.user,})


# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# def responsible_tmts_repair_update_view(request, id):
#     try:
#         old_data = get_object_or_404(Responsible_TMTS_repair_Model, id=id)
#         title_text = "Ответственный за ремонт/обслуживание (обновление записи)"
#     except Exception:
#         raise Http404('Такой записи не существует')
    
#     # Если метод POST, то это обновленные данные
#     # Остальные методы - возврат данных для изменения
#     if request.method =='POST':
#         form = Responsible_TMTS_repair_Form(request.POST, instance=old_data)
#         if form.is_valid():
#             form.save()
#             return redirect(f'/laptop/responsible_tmts_repair_/{id}')
#     else:
#         form = Responsible_TMTS_repair_Form(instance = old_data)
#     context ={
# 'user_login': request.user,
#             'form':form,
#             'title_text':title_text,
#             'url_return_to_the_list':'responsible_tmts_repair_list',
#         }
#     return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.delete_responsible_tmts_repair_model', raise_exception=True)
def responsible_tmts_repair_delete_view(request, id):
    try:
        data = get_object_or_404(Responsible_TMTS_repair_Model, id=id)
        title_text = "Ответственный за ремонт/обслуживание (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('responsible_tmts_repair_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'responsible_tmts_repair_list','user_login': request.user,})



# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ (не добавлял область поиска)
@login_required
@permission_required(perm='laptop.view_responsible_tmts_repair_model', raise_exception=True)
def responsible_tmts_repair_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')
        dataset = Responsible_TMTS_repair_Model.objects.filter(
                                                    Q(fio__icontains=query)|
                                                    Q(account__icontains=query)|
                                                    Q(email__icontains=query)|
                                                    Q(distingished_name__icontains=query)|
                                                    Q(company__icontains=query)|
                                                    Q(company_position__icontains=query)|
                                                    Q(mobile__icontains=query)|
                                                    Q(telephone_number__icontains=query)
                                                   )

    title_text = "Ответственные за ремонт/обслуживание (поиск записей)"

    context = {
            'user_login': request.user,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/responsible_tmts_repair_listview.html', context)












# ***********************************************************************************************************************************************************
# Reestr_TMTS_repair_Model / Ремонт(обслуживание) ТМЦ

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_list_view(request):
    # Получаем все записи
    dataset = Reestr_TMTS_repair_Model.objects.all().select_related("reestr_TMTS","responsible_TMTS_repair","creator_account") 

    count_dataset = dataset.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages)  

    title_text = "Ремонт/обслуживание ТМЦ (список записей)"
    

    context = {
            # 'form': form,
            'user_login': request.user,
            'dataset': dataset,  
            'count_dataset': count_dataset,
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/reestr_tmts_repair_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# логируем операцию создания записи Reestr_TMTS_repair_Model и добавления ее в Arhiv_Reestr_TMTS_repair_Model
def reestr_tmts_repair_logging_CRUD_operations(data_reestr_TMTS, action, action_user):
                            
    # создаем объект Responsible_TMTS_Model 
    arhiv_tmts_repair = Arhiv_Reestr_TMTS_repair_Model()    

    arhiv_tmts_repair.id_reestr_tmts_repair = data_reestr_TMTS.id
    arhiv_tmts_repair.id_reestr_tmts = data_reestr_TMTS.reestr_TMTS.id    
    arhiv_tmts_repair.reestr_TMTS = str(data_reestr_TMTS.reestr_TMTS)    
    arhiv_tmts_repair.username_responsible_TMTS_repair = str(data_reestr_TMTS.username_responsible_TMTS_repair)      
    arhiv_tmts_repair.responsible_TMTS_repair = "" if str(data_reestr_TMTS.responsible_TMTS_repair)=="None" else str(data_reestr_TMTS.responsible_TMTS_repair)  
    arhiv_tmts_repair.created_reestr_tmts_repair = data_reestr_TMTS.created
    arhiv_tmts_repair.creator_account = str(data_reestr_TMTS.creator_account)
    arhiv_tmts_repair.updated_reestr_tmts_repair = data_reestr_TMTS.updated
    arhiv_tmts_repair.comment = str(data_reestr_TMTS.comment)
    arhiv_tmts_repair.archived = str(data_reestr_TMTS.archived)           
    arhiv_tmts_repair.action = action
    arhiv_tmts_repair.creator_action = str(action_user) #'Кем выполнено'

    arhiv_tmts_repair.save()



# Добавляем записи в реестр "Ремонт/обслуживание ТМЦ" 
# Учетные записи ответственных за ремонт выбираются из списка (внешний ключ)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def reestr_tmts_repair_add_entry(request, tmts_id):
    try:
        data_tmts = get_object_or_404(Reestr_TMTS_Model, id=tmts_id)

        try:
            data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)               

            # если статус не равен "в ремонте"
            if data_tmts.status != data_tmts_status_repair:
                # return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')
                return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')
            
            else:
                messages.error(request, 'Ошибка! Данная запись уже в статусе "в ремонте". Проверьте реестр "Ремонт/обслуживание ТМЦ".')               
                # переадресуем на страницу
                return redirect('reestr_tmts_list')
            
        except Exception:
            raise Http404('Статуса "в ремонте" не существует') 
        
    except Exception:
        raise Http404('Такой записи не существует')   
    


def search_responsible_TMTS_repair_user_in_ldap(user_name):

    try:
        lconn = ldap.initialize('ldap://site.ru')   # домен
        lconn.protocol_version = ldap.VERSION3  # версия протокола
        lconn.set_option(ldap.OPT_REFERRALS, 0) # не используем рефералы
        lconn.simple_bind_s('ldap@site.ru','password')  # учетные данные
        # print('Connect to AD succesfull')

        base = "dc=site,dc=ru"  # начальный контейнер, с которого начинаем поиск объектов
        
        scope = ldap.SCOPE_SUBTREE  # область поиска, SCOPE_SUBTREE - ищем в дочерних объектах
        
        filter = "(&(sAMAccountName=%s))" % user_name  # фильтр, ищем объекты
        
        # filter = "(&(objectcategory=person))"   # фильтр, ищем объекты "person" (пользователи)
        # filter = "(&(mail=*))"   # фильтр, ищем объекты
        # attrs = ['displayname','title']     # атрибуты искомых объектов        
        # attrs = ['mail','proxyAddresses']     # атрибуты искомых объектов
        attrs = ['displayname','title','mail','sAMAccountName','givenName', 'company', 'extensionAttribute2', 'mobile', 'telephoneNumber']     # атрибуты искомых объектов ('displayname','title','mail','sAMAccountName','givenName')

        result_set = []     # массив с полученным результатом

        ldap_result_id = lconn.search_ext(base, scope, filter, attrs)   # идентификатор поиска объектов в каталоге

        try:
            while 1:
                result_type, result_data = lconn.result(ldap_result_id, 0)
                if (result_data == []):
                    break
                else:
                    if result_type == ldap.RES_SEARCH_ENTRY:                        
                        # result_set.append(result_data)

                        # print("*"*55)
                        # print(result_data)
                        # print("*"*55)

                        fio = result_data[0][0].split(',')[0].split('=')[1] 
                        login = result_data[0][1].get('sAMAccountName')[0].decode("utf-8")
                        mail =  "" if result_data[0][1].get('mail', "") == "" else result_data[0][1].get('mail')[0].decode("utf-8")
                        distinguishedName = result_data[0][0]
                        company = "" if result_data[0][1].get('company', "") == "" else result_data[0][1].get('company')[0].decode("utf-8")
                        company_position = "" if result_data[0][1].get('extensionAttribute2', "") == "" else result_data[0][1].get('extensionAttribute2')[0].decode("utf-8")
                        mobile = "" if result_data[0][1].get('mobile', "") == "" else result_data[0][1].get('mobile')[0].decode("utf-8")
                        telephoneNumber = "" if result_data[0][1].get('telephoneNumber', "") == "" else result_data[0][1].get('telephoneNumber')[0].decode("utf-8")
                        
                        result_set.append({"fio":fio, "login":login, "mail":mail, "distinguishedName":distinguishedName,
                                           "company":company, "company_position":company_position,
                                           "mobile":mobile, "telephoneNumber":telephoneNumber,})           

                                

                        try:
                            # обновляем запись (возможна смена фамилии/должности)                        
                            responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=login.lower())                            

                            responsible_tmts.fio = fio
                            # responsible_tmts.account = result_user_data[0]['login']
                            responsible_tmts.email = mail
                            responsible_tmts.distingished_name = distinguishedName
                            responsible_tmts.company = company
                            responsible_tmts.company_position = company_position
                            responsible_tmts.mobile = mobile
                            responsible_tmts.telephone_number = telephoneNumber
                            responsible_tmts.save()
                        except Responsible_TMTS_repair_Model.DoesNotExist:
                            raise Http404('Такой записи не существует')

        except ldap.SIZELIMIT_EXCEEDED:
            print("ldap.SIZELIMIT_EXCEEDED")


        # for item in result_set:
        #     print(item)
        
        return result_set
    
    except ldap.SERVER_DOWN:
        print('Error connection to AD')


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_create_view(request, tmts_id):

    title_text = "Ремонт/обслуживание ТМЦ (добавление записи)"

    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Reestr_TMTS_repair_Form(request.POST)

        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу

            # print("*"*75)
            # print("1")
            # print("*"*75)

            # ---------------------------------------------------------------------------         
            try:               

                form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)
                
                
                
                # # print("---",form.instance.responsible_TMTS_repair, "---")
                # if form.instance.responsible_TMTS_repair == None:
                #     form =Reestr_TMTS_Form(request.POST)
                #     messages.error(request, 'Ошибка! Проверьте правильность учетной записи ответственного за ремонт/обслуживание.')
                #     messages.error(request, form.errors)
                # else:
                    # form.instance.username_responsible_TMTS_repair=form.instance.responsible_TMTS_repair.account

                # print("---",form.instance.responsible_TMTS_repair, "---")

                form.instance.username_responsible_TMTS_repair=form.instance.responsible_TMTS_repair.account 

                # получаем информацию из AD по имени пользователя и обновляем ее в реестре 'Ответственный за ремонт/обслуживание'
                result_user_data = search_responsible_TMTS_repair_user_in_ldap(form.instance.responsible_TMTS_repair.account)   
                # result_user_data = select_user_data_ldap(form.instance.responsible_TMTS_repair.account)   # получаем информацию из AD по имени пользователя

                # print("*"*75)
                # print("2-2")
                # print("*"*75)


                # проверяем, что поле учетной записи не пустое (пользователь найден в AD, действующий пользователь)
                if result_user_data != []:

                    # print("*"*75)
                    # print("3")
                    # print("*"*75)


                    # меняем статус записи Reestr_TMTS_Model на 'в ремонте'    
                    data_tmts = get_object_or_404(Reestr_TMTS_Model, id=tmts_id)
                    data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)
                    data_tmts.status = data_tmts_status_repair # меняем статус на 'в ремонте'
                    data_tmts.save()

                    # print("*"*75)
                    # print("4")
                    # print("*"*75)
                
                    # ---------------------------------------------------------------------------
                    # логируем операцию изменения записи Reestr_TMTS_Model в Arhiv_Reestr_TMTS_Model        
                    action = 'в ремонт' + " (" + form.instance.username_responsible_TMTS_repair + ")"
                    action_user = request.user        
                    reestr_tmts_logging_CRUD_operations(data_tmts, action, action_user)
                    # ---------------------------------------------------------------------------

                    form.instance.reestr_TMTS = data_tmts #'ТМЦ'


                                
                    # если 'Ответственный за ремонт' уже существует
                    # обновление записи уже выполнено в функции "search_responsible_TMTS_repair_user_in_ldap()"
                    
                    # if Responsible_TMTS_repair_Model.objects.filter(account__iexact=form.instance.responsible_TMTS_repair.account.lower()).exists():
                        
                    #     try:
                    #         # обновляем запись (возможна смена фамилии/должности)                        
                    #         responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=form.instance.username_responsible_TMTS_repair.lower())                            

                    #         responsible_tmts.fio = result_user_data[0]['fio']
                    #         # responsible_tmts.account = result_user_data[0]['login']
                    #         responsible_tmts.email = result_user_data[0]['mail']
                    #         responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                    #         responsible_tmts.company = result_user_data[0]['company']
                    #         responsible_tmts.company_position = result_user_data[0]['company_position']
                    #         responsible_tmts.mobile = result_user_data[0]['mobile']
                    #         responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                    #         responsible_tmts.save()
                    #     except Responsible_TMTS_repair_Model.DoesNotExist:
                    #         raise Http404('Такой записи не существует')   

                    # print("*"*75)
                    # print("5")
                    # print("*"*75)                    
                    
                                
                    result_object = form.save()

                    # print("*"*75)
                    # print(result_object)
                    # print("*"*75) 
                    
                    # ---------------------------------------------------------------------------
                    # логируем операцию создания записи Reestr_TMTS_repair_Model в Arhiv_Reestr_repair_TMTS_Model        
                    action = 'создание'
                    action_user = request.user        
                    reestr_tmts_repair_logging_CRUD_operations(result_object, action, action_user)
                    # ---------------------------------------------------------------------------
                    
                    # messages.success(request, "Запись успешно записана в БД.")        

                    
                    # переадресуем на главную страницу
                    return redirect('reestr_tmts_repair_list')

                else:                        
                    form =Reestr_TMTS_repair_Form(request.POST)
                    messages.error(request, 'Ошибка! Проверьте правильность учетной записи. Возможно учетная запись ответственного удалена.')
                    messages.error(request, form.errors)
            
            except Exception:
                form =Reestr_TMTS_repair_Form(request.POST)                
                messages.error(request, 'Ошибка! Такой записи не существует, либо статуса "в ремонте" не существует.')
                messages.error(request, form.errors)
                        
        else:
            form =Reestr_TMTS_repair_Form(request.POST)                    
            messages.error(request, form.errors)

    else:
        form =Reestr_TMTS_repair_Form()
    context = {
            'form': form,
            'user_login': request.user,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)


# "Возвращаем" (удаляем) запись из реестра "Ремонт/обслуживание ТМЦ" в статус "в работе" ("на складе") в реестр ТМЦ (ремонт выполнен)
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_completed_entry(request: HttpRequest, id):
    
    try:
        data_repair = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
        title_text = "Ремонт/обслуживание ТМЦ (работа выполнена)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':

        # print(data_repair.username_responsible_TMTS_repair)

        # Получаем из запроса только те данные которые использует форма
        form = Reestr_TMTS_repair_Form(request.POST, instance=data_repair)
        
        # Проверяем правильность введенных данных и сохраняем в базу        
        if form.is_valid():
        
            try:
                data_reestr_TMTS = get_object_or_404(Reestr_TMTS_Model, id=data_repair.reestr_TMTS.id)

                try:
                    data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)               

                    # если статус не равен "в ремонте"
                    if data_reestr_TMTS.status == data_tmts_status_repair:
                        # return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')
                        # return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')                         

                        if data_reestr_TMTS.username_responsible_TMTS != '' and data_reestr_TMTS.responsible_TMTS != None:
                            try:
                                data_tmts_status_job = get_object_or_404(Status_TMTS_Model, id=1) # в работе
                                data_reestr_TMTS.status = data_tmts_status_job
                            except Exception:
                                raise Http404('Статуса "в работе" не существует') 
                            
                        else:
                            try:
                                data_tmts_status_sklad = get_object_or_404(Status_TMTS_Model, id=3) # "на складе"
                                data_reestr_TMTS.status = data_tmts_status_sklad
                            except Exception:
                                raise Http404('Статуса "на складе" не существует') 
                            
                        data_reestr_TMTS.save()
                    
                    else:
                        messages.error(request, 'Ошибка! Данная запись не в статусе "в ремонте". Проверьте реестр "Учет ТМЦ".')               
                        # переадресуем на страницу
                        return redirect('reestr_tmts_repair_list')
                
                except Exception:
                    raise Http404('Статуса "в ремонте" не существует')
                
                
                # меняем ответственного, если в форме изменения
                data_repair.username_responsible_TMTS_repair = form.instance.responsible_TMTS_repair.account    

                # ---------------------------------------------------------------------------
                # логируем операцию в Arhiv_Reestr_TMTS_repair_Model              
                action = 'возврат из ремонта' + " (" + form.instance.responsible_TMTS_repair.account + ")" 
                action_user = request.user
                reestr_tmts_logging_CRUD_operations(data_reestr_TMTS, action, action_user)
                # ---------------------------------------------------------------------------
            
            except Exception:
                raise Http404('Такой записи Reestr_TMTS_Model не существует')        
    
            # ---------------------------------------------------------------------------
            # логируем операцию в Arhiv_Reestr_repair_TMTS_Model  
            action = 'работа выполнена' + " (" + form.instance.responsible_TMTS_repair.account + ")"      
            action_user = request.user        
            reestr_tmts_repair_logging_CRUD_operations(data_repair, action, action_user)
            # ---------------------------------------------------------------------------

            data_repair.delete()    # удаляем запись

            return redirect('reestr_tmts_list')
    else:
        form =Reestr_TMTS_repair_Form(instance=data_repair)
    
    context = {
            'form': form,
            'user_login': request.user,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_repair_list',
        }
    return render(request, 'laptop/completed_repair.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.change_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_update_view(request, id):
    try:
        old_data = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
        title_text = "Ремонт/обслуживание ТМЦ (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Reestr_TMTS_repair_Form(request.POST, instance=old_data)

        # Проверяем правильность введенных данных и сохраняем в базу        
        if form.is_valid():

            form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)

            if form.instance.responsible_TMTS_repair != None:

                result_user_data = select_user_data_ldap(form.instance.responsible_TMTS_repair.account)   # получаем информацию из AD по имени пользователя                
                # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
                if result_user_data != []:                                
                    try:
                        # обновляем запись (возможна смена фамилии/должности)                        
                        responsible_tmts_repair = get_object_or_404(Responsible_TMTS_repair_Model, 
                                                                    account__iexact=form.instance.responsible_TMTS_repair.account.lower())

                        responsible_tmts_repair.fio = result_user_data[0]['fio']
                        # responsible_tmts.account = result_user_data[0]['login']
                        responsible_tmts_repair.email = result_user_data[0]['mail']
                        responsible_tmts_repair.distingished_name = result_user_data[0]['distinguishedName']
                        responsible_tmts_repair.company = result_user_data[0]['company']
                        responsible_tmts_repair.company_position = result_user_data[0]['company_position']
                        responsible_tmts_repair.mobile = result_user_data[0]['mobile']
                        responsible_tmts_repair.telephone_number = result_user_data[0]['telephoneNumber']
                        responsible_tmts_repair.save()
                    except Responsible_TMTS_repair_Model.DoesNotExist:
                        raise Http404('Такой записи не существует')                    
                        
                    form.instance.responsible_TMTS_repair = responsible_tmts_repair   # сохраняем полученный объект Responsible_TMTS_repair_Model                                
                    result_data = form.save()

                    # ---------------------------------------------------------------------------
                    # логируем операцию в Arhiv_Reestr_repair_TMTS_Model  
                    action = 'изменение'     
                    action_user = request.user        
                    reestr_tmts_repair_logging_CRUD_operations(result_data, action, action_user)
                    # ---------------------------------------------------------------------------                    
                                
                    # messages.success(request, "Запись успешно записана в БД.")

                    # переадресуем на страницу
                    return redirect(f'/laptop/reestr_tmts_repair/{id}') 

                else:
                    # print("else1")
                        
                    form =Reestr_TMTS_repair_Form(request.POST, instance=old_data)
                    messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                    messages.error(request, form.errors)

            else:
                # print("else2")
                    
                form =Reestr_TMTS_repair_Form(request.POST, instance=old_data)
                messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                messages.error(request, form.errors)        
        else:
            # print("else3")
            
            form =Reestr_TMTS_repair_Form(request.POST, instance=old_data)    
            messages.error(request, form.errors)
    else:
        form = Reestr_TMTS_repair_Form(instance = old_data)
    context ={
                'user_login': request.user,
                'form':form,
                'title_text':title_text,
                'url_return_to_the_list':'reestr_tmts_repair_list',
        }
    return render(request, 'laptop/update.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Reestr_TMTS_repair_Model.objects.get(id=id)
        title_text = "Ремонт/обслуживание ТМЦ"
    except Reestr_TMTS_repair_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    

    context ={
        'user_login': request.user,
        'data':data,
        'title_text':title_text,
        'url_return_to_the_list':'reestr_tmts_repair_list',
        }
    return render(request, 'laptop/reestr_tmts_repair_detailview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# export all reestr (Reestr_TMTS_repair_Model)
@login_required
@permission_required(perm='laptop.view_reestr_tmts_repair_model', raise_exception=True)
def export_reestr_tmts_repair_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_tmts_repair.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('reestr_tmts_repair')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

 
    columns = ['ТМЦ','Учетная запись ответственного за ремонт/обслуживание','Ответственный за ремонт/обслуживание',
               'Дата регистрации', 'Кем изменено/создано','Дата изменения','Комментарий','Длительность ремонта (дней)',]#'Переведен в архив'
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []
    dataset = Reestr_TMTS_repair_Model.objects.all().select_related("reestr_TMTS","responsible_TMTS_repair","creator_account")
    for row in dataset:
        rows.append(
            [
            str(row.reestr_TMTS),
            str(row.username_responsible_TMTS_repair),    
            str(row.responsible_TMTS_repair),         
            row.created,
            str(row.creator_account),
            row.updated,
            row.comment,
            str(row.delta_data().days),
            #row.archived,            
            ]
        )
    
 
    # rows = Printed_pagesModel.objects.all().values_list('printers_in_service.service_object.service_object_name', 
    #                                                     'printers_in_service.printers.name', 
    #                                                     'printers_in_service.serial_number',
    #                                                     'printers_in_service.ip_address',
    #                                                     'created',
    #                                                     'printed_pages')
    
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_reestr_tmts_repair_model', raise_exception=True)
def reestr_tmts_repair_search_list_view(request):
    
    if request.method =='GET':
        query = request.GET.get('search_query')

        # lower_name = Reestr_TMTS_Model.objects.annotate(lower_name=Lower('owner_TMTS__name_legal_entity'))
        # lower_name.filter(lower_name__icontains=query)       
        # dataset = lower_name.filter(lower_name__icontains=query)
        
        dataset = Reestr_TMTS_repair_Model.objects.filter(
            Q(reestr_TMTS__owner_TMTS__name_legal_entity__icontains=query)|
            Q(reestr_TMTS__name_TMTS__manufacturer__icontains=query)|
            Q(reestr_TMTS__name_TMTS__name_model__icontains=query)|
            Q(reestr_TMTS__name_TMTS__type_TMTS__type_tmts__icontains=query)|
            Q(reestr_TMTS__serial_number__icontains=query)|
            Q(reestr_TMTS__responsible_TMTS__fio__icontains=query)|

            Q(responsible_TMTS_repair__fio__icontains=query)|
            Q(responsible_TMTS_repair__account__icontains=query)| 
            Q(responsible_TMTS_repair__company__icontains=query)|
            Q(responsible_TMTS_repair__company_position__icontains=query)|

            Q(creator_account__username__icontains=query)|
            
            Q(comment__icontains=query)
                                                   )
        
        count_dataset = dataset.count()
        
    title_text = "Ремонт/обслуживание ТМЦ (поиск записей)"

    context = {
            'user_login': request.user,
            'dataset': dataset,    
            'count_dataset': count_dataset,        
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/reestr_tmts_repair_listview.html', context)











# ***********************************************************************************************************************************************************
# Arhiv_Reestr_TMTS_repair_Model / Учет ТМЦ (архив)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_repair_model', raise_exception=True)
def reestr_arhiv_tmts_repair_list_view(request):    
    # Получаем записи    
    # dataset = Arhiv_Reestr_TMTS_repair_Model.objects.all().order_by('-created')[:100] 

    # Получаем записи
    dataset = Arhiv_Reestr_TMTS_repair_Model.objects.all().order_by('-created')
    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages) 

    title_text = 'Ремонт/обслуживание ТМЦ (история операций)'

    context = {
            'user_login': request.user,
            # 'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            "options": True
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_repair_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_repair_model', raise_exception=True)
def reestr_arhiv_tmts_repair_get_by_id(request, id):    

    title_text = "История операций ТМЦ: "

    try:
        # data_responsible_tmts = get_object_or_404(Arhiv_Reestr_TMTS_repair_Model, id_reestr_tmts_repair=id)
        # Получаем записи по-определенному id
        dataset = Arhiv_Reestr_TMTS_repair_Model.objects.filter(id_reestr_tmts_repair=id)

        title_text = "История операций ТМЦ: " + dataset[0].reestr_TMTS
        
        count_dataset = dataset.count()

        page = request.GET.get('page', 1)
        paginator = Paginator(dataset, 5)  #  paginate_by 5
        try:
            dataset = paginator.page(page)
        except PageNotAnInteger:
            dataset = paginator.page(1)
        except EmptyPage:
            dataset = paginator.page(paginator.num_pages) 

    except Arhiv_Reestr_TMTS_repair_Model.DoesNotExist:
        raise Http404('Таких записей не существует')    

    context = {
            'user_login': request.user,
            'dataset': dataset,   
            'count_dataset': count_dataset,          
            'title_text': title_text,
            'url_return_to_the_list': 'reestr_tmts_repair_list_view',
            "options": False
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_repair_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_repair_model', raise_exception=True)
def reestr_arhiv_tmts_repair_search_list_view(request):
    if request.method =='GET':
        query = request.GET.get('search_query')
        dataset = Arhiv_Reestr_TMTS_repair_Model.objects.filter(
                                                    Q(id_reestr_tmts_repair__icontains=query)|
                                                    Q(id_reestr_tmts__icontains=query)|
                                                    Q(reestr_TMTS__icontains=query)|
                                                    Q(username_responsible_TMTS_repair__icontains=query)|
                                                    Q(responsible_TMTS_repair__icontains=query)|
                                                    Q(created_reestr_tmts_repair__icontains=query)|
                                                    Q(creator_account__icontains=query)|
                                                    Q(updated_reestr_tmts_repair__icontains=query)|
                                                    Q(comment__icontains=query)|
                                                    Q(archived__icontains=query)|
                                                    Q(created__icontains=query)|
                                                    Q(action__icontains=query)|
                                                    Q(creator_action__icontains=query)
                                                   )

    title_text = 'Ремонт/обслуживание ТМЦ (поиск истории операций)'

    context = {
            'user_login': request.user,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/arhiv_reestr_tmts_repair_search_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# # export all reestr (Arhiv_Reestr_TMTS_Model)
@login_required
@permission_required(perm='laptop.view_arhiv_reestr_tmts_repair_model', raise_exception=True)
def export_reestr_arhiv_tmts_repair_xls(request: HttpRequest):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="reestr_arhiv_tmts_repair.xls"'
 
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('arhiv_repair')
 
    # Sheet header, first row
    row_num = 0
 
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
 
    columns = ['id записи','id ТМЦ','ТМЦ','Учетная запись ответственного за ремонт/обслуживание','Ответственный за ремонт/обслуживание','Дата регистрации',
                'Кем изменено/создано','Дата изменения','Комментарий','Дата действия','Действие','Кем выполнено']#,'Переведен в архив'
 
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
 
    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    
    rows = []
    dataset = Arhiv_Reestr_TMTS_repair_Model.objects.all()
    for row in dataset:
        rows.append(
            [
                row.id_reestr_tmts_repair,
                row.id_reestr_tmts,
                row.reestr_TMTS,
                row.username_responsible_TMTS_repair,
                row.responsible_TMTS_repair,
                row.created_reestr_tmts_repair,
                row.creator_account,
                row.updated_reestr_tmts_repair,
                row.comment,
                # row.archived,
                row.created,
                row.action,
                row.creator_action,        
            ]
        )

    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, datetime.datetime) else x for x in row] for row in rows ]
    
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
 
    wb.save(response)
    return response



# ***********************************************************************************************************************************************************
# Image_Reestr_TMTS_repair_Model / Ремонт(обслуживание) ТМЦ (изображения)

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_image_reestr_tmts_repair_model', raise_exception=True)
def reestr_image_tmts_repair_get_by_id(request, id):
    try:
        title_text = "Загруженные изображения ТМЦ"

        title_text_tmts = ""
        reestr_tmts_repair_data = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
        if reestr_tmts_repair_data:
            title_text_tmts = str(reestr_tmts_repair_data.reestr_TMTS)
            
        # Получаем записи по-определенному id
        # dataset = get_object_or_404(Image_Reestr_TMTS_repair_Model, reestr_repair_TMTS__id=id)
        # dataset = Image_Reestr_TMTS_repair_Model.objects.filter(reestr_repair_TMTS__id=id)
        dataset = Image_Reestr_TMTS_repair_Model.objects.filter(reestr_repair_TMTS=id)
        
        count_dataset = dataset.count()

        if len(dataset) != 0:
            # title_text_tmts = str(dataset[0].reestr_repair_TMTS) #"Загруженные изображения ТМЦ: " +
            reestr_tmts_repair_data = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
            title_text_tmts = str(reestr_tmts_repair_data) #"Загруженные изображения ТМЦ: " +
        
        

            page = request.GET.get('page', 1)
            paginator = Paginator(dataset, 5)  #  paginate_by 5
            try:
                dataset = paginator.page(page)
            except PageNotAnInteger:
                dataset = paginator.page(1)
            except EmptyPage:
                dataset = paginator.page(paginator.num_pages) 

    except Image_Reestr_TMTS_repair_Model.DoesNotExist:
        # messages.error(request, 'Ошибка! Данная запись уже в статусе "на складе".')               
        # переадресуем на страницу
        # return redirect('reestr_tmts_repair_list_view')
        raise Http404('Таких записей не существует')    

    context = {
            'user_login': request.user,
            'dataset': dataset,   
            'count_dataset': count_dataset,          
            'title_text': title_text,
            'title_text_tmts': title_text_tmts,
            'url_return_to_the_list': 'reestr_tmts_repair_list_view',
            "options": False,
            'id_tmts_repair': id,
            
        }    
    return render(request, 'laptop/image_reestr_tmts_repair_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.add_image_reestr_tmts_repair_model', raise_exception=True)    
def reestr_image_tmts_repair_create_view(request, id):    

    title_text = "Изображения ТМЦ (добавление записи)"

    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST': #and request.FILES:

        # # Получаем загруженный файл
        # file = request.FILES['file_image']
        # fs = FileSystemStorage()

        # #сохраняем на файловой системе
        # filename = fs.save(file.name, file)

        # # получение адреса по которому лежит файл
        # file_url = fs.url(filename)

        # Получаем из запроса только те данные которые использует форма
        form = Image_Reestr_TMTS_repair_Form(request.POST, request.FILES)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу

            # reestr_tmts_repair_data = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
            # print("*"*55)
            # print(reestr_tmts_repair_data)
            # print("*"*55)


            # form.instance.reestr_repair_TMTS = reestr_tmts_repair_data
            form.instance.reestr_repair_TMTS = id



            form.save()
            # переадресуем на главную страницу            
            return redirect(f'/laptop/reestr_image_tmts_repair_get_by_id/{id}')
    else:
        form = Image_Reestr_TMTS_repair_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_repair_list',
            
        }        
    return render(request, 'laptop/create_image.html', context)








# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@login_required
@permission_required(perm='laptop.view_image_reestr_tmts_repair_model', raise_exception=True)
def reestr_image_tmts_repair_list_view(request):
    # Получаем записи
    dataset = Image_Reestr_TMTS_repair_Model.objects.all()
    count_dataset = dataset.count()

    page = request.GET.get('page', 1)
    paginator = Paginator(dataset, 5)  #  paginate_by 5
    try:
        dataset = paginator.page(page)
    except PageNotAnInteger:
        dataset = paginator.page(1)
    except EmptyPage:
        dataset = paginator.page(paginator.num_pages) 

    title_text = 'Ремонт(обслуживание) ТМЦ (изображения)'

    context = {
            'user_login': request.user,
            # 'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            "options": True,
            "count_dataset": count_dataset,
            
        }    
    return render(request, 'laptop/image_reestr_tmts_repair_listview.html', context)









class Reestr_TMTS_Model_View(CreateView):
    model = Reestr_TMTS_Model
    form_class = Reestr_TMTS_Model_SearchForm
    success_url = "/"


def reestr_TMTS_Model_testSearch(request):
    title_text = 'test'
    
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Reestr_TMTS_Model_SearchForm2(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('reestr_tmts_list')
    else:
        form =Reestr_TMTS_Model_SearchForm2()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_list',
        }        
    return render(request, 'laptop/create_test.html', context)



































# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
class Reestr_TMTS_Model_List(ListView):
    model = Reestr_TMTS_Model
    table_class = Reestr_TMTS_Model_Table
    template_name = 'laptop/reestr_tmts.html'


def reestr_TMTS_list_new(request: HttpRequest):
    table = Reestr_TMTS_Model_Table(Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account"))
    RequestConfig(request).configure(table)
    return render(request, 'laptop/reestr_tmts.html', {'table': table})







def reestr_TMTS_list_universal(request: HttpRequest):
    model_headers = [f.name for f in Reestr_TMTS_Model._meta.get_fields()]
    query_results = [list(i.values()) for i in list(Reestr_TMTS_Model.objects.all().select_related("status","owner_TMTS","name_TMTS","responsible_TMTS","creator_account").values())]
   

    title_text = "Учет ТМЦ (список записей)"   

    context = {
            'user_login': request.user,
            'model_headers': model_headers,
            'query_results': query_results,
            'title_text':title_text,            
        }   




    return render(request, 'laptop/reestr_tmts_universal.html', context)






# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# class Reestr_TMTS_repair_Model_List(ListView):
#     model = Reestr_TMTS_repair_Model
#     template_name = 'laptop/reestr_tmts_repair_listview.html'
#     context_object_name = 'dataset'
#     # extra_context = {
            #'user_login': request.user,
#     #     'url_return_to_the_list':'reestr_tmts_repair_list', 
#     #     'title_text': "Ремонт/обслуживание ТМЦ (список записей)",
        
#     # }
    
#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)
#         context['title_text'] = 'Ремонт/обслуживание ТМЦ (список записей)'
#         context['url_return_to_the_list'] = 'reestr_tmts_repair_list'    
#         return context
    
#     # def get_queryset(self) -> QuerySet[Any]:
#     #     # return super().get_queryset()
#     #     return Reestr_TMTS_repair_Model.objects.filter(archived = False)


# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# class Reestr_TMTS_repair_Model_Create(CreateView):
#     model = Reestr_TMTS_repair_Model
#     form_class = Reestr_TMTS_repair_ModelForm
#     template_name = 'laptop/reestr_tmts_repair_model_form.html'
#     success_url = reverse_lazy('reestr_tmts_repair_list')

#     def form_valid(self, form, **kwargs):
#         self.object = form.save(commit=False)

#         # ---------------------------------------------------------------------------         
#         try:
#             # меняем статус записи Reestr_TMTS_Model на 'в ремонте'    
#             data_tmts = get_object_or_404(Reestr_TMTS_Model, id=self.kwargs.get('tmts_id'))
#             data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)
#             data_tmts.status = data_tmts_status_repair # меняем статус на 'в ремонте'
#             data_tmts.save()
            
#             # логируем операцию изменения записи Reestr_TMTS_Model в Arhiv_Reestr_TMTS_Model        
#             action = 'в ремонт'        
#             action_user = self.request.user        
#             reestr_tmts_logging_CRUD_operations(data_tmts, action, action_user)


#             form.instance.reestr_TMTS = data_tmts #'ТМЦ'

#             form.instance.creator_account = self.request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)

                    
#             print(form.instance.username_responsible_TMTS_repair)

#             result_user_data = select_user_data_ldap(form.instance.username_responsible_TMTS_repair)   # получаем информацию из AD по имени пользователя
                    
#             # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
#             if result_user_data != []:      
#                 print("*"*35)
#                 print("result_user_data != []:")
#                 print("*"*35)          
                            
#                 # если 'Ответственный за ремонт' уже существует
#                 if Responsible_TMTS_repair_Model.objects.filter(account__iexact=form.instance.username_responsible_TMTS_repair.lower()).exists():
#                     try:
#                         # обновляем запись (возможна смена фамилии/должности)                        
#                         responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=form.instance.username_responsible_TMTS_repair.lower())                            

#                         responsible_tmts.fio = result_user_data[0]['fio']
#                         # responsible_tmts.account = result_user_data[0]['login']
#                         responsible_tmts.email = result_user_data[0]['mail']
#                         responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
#                         responsible_tmts.company = result_user_data[0]['company']
#                         responsible_tmts.company_position = result_user_data[0]['company_position']
#                         responsible_tmts.mobile = result_user_data[0]['mobile']
#                         responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
#                         responsible_tmts.save()
#                     except Responsible_TMTS_repair_Model.DoesNotExist:
#                         raise Http404('Такой записи не существует')
                                
#                 else:   # 'Ответственный за ремонт' не существует в БД
#                     # создаем объект Responsible_TMTS_repair_Model 
#                     responsible_tmts = Responsible_TMTS_repair_Model()

#                     responsible_tmts.fio = result_user_data[0]['fio']
#                     responsible_tmts.account = result_user_data[0]['login']
#                     responsible_tmts.email = result_user_data[0]['mail']
#                     responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
#                     responsible_tmts.company = result_user_data[0]['company']
#                     responsible_tmts.company_position = result_user_data[0]['company_position']
#                     responsible_tmts.mobile = result_user_data[0]['mobile']
#                     responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
#                     responsible_tmts.save()
                    
#                     form.instance.responsible_TMTS_repair = responsible_tmts   # сохраняем полученный объект Responsible_TMTS_repair_Model
                            
#                 # result_object = form.save()    

# #                         # # ---------------------------------------------------------------------------
# #                         # # логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
# #                         # # created_dateTime=datetime.datetime.now()
# #                         # # updated_dateTime=datetime.datetime.now()
# #                         # action = 'создание'                    
# #                         # create_user = request.user
# #                         # # reestr_tmts_logging_CRUD_operations(result_object, created_dateTime, updated_dateTime, action, create_user)
# #                         # reestr_tmts_logging_CRUD_operations(result_object, action, create_user)
# #                         # # ---------------------------------------------------------------------------
# #                         # messages.success(request, "Запись успешно записана в БД.")                   


#         except Exception:
#             raise Http404('Такой записи не существует, либо статуса "в ремонте" не существует.') 
#         # ---------------------------------------------------------------------------
        
                
#         return super(Reestr_TMTS_repair_Model_Create, self).form_valid(form)

                    

#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super(Reestr_TMTS_repair_Model_Create, self).get_context_data(**kwargs)
#         context['tmts_id'] = self.kwargs.get('tmts_id')
#         context['title_text'] = 'Ремонт/обслуживание ТМЦ (создание записи)'
#         context['url_return_to_the_list'] = 'reestr_tmts_repair_list'    
#         return context





# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# class Reestr_TMTS_repair_Model_Detail(DetailView):
#     model = Reestr_TMTS_repair_Model
#     template_name = 'laptop/reestr_tmts_repair_detailview.html'

# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# class Reestr_TMTS_repair_Model_Update(UpdateView):
#     model = Reestr_TMTS_repair_Model
#     form_class = Reestr_TMTS_repair_Form
#     template_name = 'laptop/update.html'
#     success_url = reverse_lazy('reestr_tmts_repair_list')
    
#     def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
#         context = super().get_context_data(**kwargs)
#         context['title_text'] = 'Ремонт/обслуживание ТМЦ (изменение записей)'
#         context['url_return_to_the_list'] = 'reestr_tmts_repair_list'    
#         return context




# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# def reestr_tmts_repair_update_view(request, id):
#     try:
#         old_data = get_object_or_404(Reestr_TMTS_repair_Model, id=id)
#         title_text = "Ремонт/обслуживание ТМЦ (обновление записи)"
#     except Exception:
#         raise Http404('Такой записи не существует')
    
#     # Если метод POST, то это обновленные данные
#     # Остальные методы - возврат данных для изменения
#     if request.method =='POST':
#         form = Reestr_TMTS_repair_Form(request.POST, instance=old_data)
#         if form.is_valid():
#             form.save()
#             return redirect(f'/laptop/reestr_tmts_repair_/{id}')
#     else:
#         form = Reestr_TMTS_repair_Form(instance = old_data)
#     context ={
#             'form':form,
#             'title_text':title_text,
#             'url_return_to_the_list':'reestr_tmts_repair_list',
#         }
#     return render(request, 'laptop/update.html', context)

















"""
Добавляем записи в реестр "Ремонт/обслуживание ТМЦ" 
Учетные записи ответственных за ремонт вводятся вручную, при добавлении записи в реестр

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def reestr_tmts_repair_add_entry(request, tmts_id):
    try:
        data_tmts = get_object_or_404(Reestr_TMTS_Model, id=tmts_id)

        # print(tmts_id, "---", data_tmts)
        
        try:
            data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)               

            if data_tmts.status != data_tmts_status_repair:
                # return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')
                return redirect(f'/laptop/reestr_tmts_repair_create/{tmts_id}/')
            
            else:
                messages.error(request, 'Ошибка! Данная запись уже в статусе "в ремонте". Проверьте реестр "Ремонт/обслуживание ТМЦ".')               
                # переадресуем на страницу
                return redirect('reestr_tmts_list')
            
        except Exception:
            raise Http404('Статуса "в ремонте" не существует') 
        
    except Exception:
        raise Http404('Такой записи не существует')   
    


def reestr_tmts_repair_create_view(request, tmts_id):

    title_text = "Ремонт/обслуживание ТМЦ (добавление записи)"

    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Reestr_TMTS_repair_Form(request.POST)

        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу



            # ---------------------------------------------------------------------------         
            try:
                

                form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)

                # print("^"*35)    
                # print(form.instance.username_responsible_TMTS_repair)
                # print("^"*35)


                result_user_data = select_user_data_ldap(form.instance.username_responsible_TMTS_repair)   # получаем информацию из AD по имени пользователя
                    
                # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
                if result_user_data != []:      
                    # print("*"*35)
                    # print("result_user_data != []:")
                    # print("*"*35)

                    # меняем статус записи Reestr_TMTS_Model на 'в ремонте'    
                    data_tmts = get_object_or_404(Reestr_TMTS_Model, id=tmts_id)
                    data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)
                    data_tmts.status = data_tmts_status_repair # меняем статус на 'в ремонте'
                    data_tmts.save()
                
                    # логируем операцию изменения записи Reestr_TMTS_Model в Arhiv_Reestr_TMTS_Model        
                    action = 'в ремонт' + " (" + form.instance.username_responsible_TMTS_repair + ")"
                    action_user = request.user        
                    reestr_tmts_logging_CRUD_operations(data_tmts, action, action_user)

                    form.instance.reestr_TMTS = data_tmts #'ТМЦ'

                                
                    # если 'Ответственный за ремонт' уже существует
                    if Responsible_TMTS_repair_Model.objects.filter(account__iexact=form.instance.username_responsible_TMTS_repair.lower()).exists():
                        try:
                            # обновляем запись (возможна смена фамилии/должности)                        
                            responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=form.instance.username_responsible_TMTS_repair.lower())                            

                            responsible_tmts.fio = result_user_data[0]['fio']
                            # responsible_tmts.account = result_user_data[0]['login']
                            responsible_tmts.email = result_user_data[0]['mail']
                            responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                            responsible_tmts.company = result_user_data[0]['company']
                            responsible_tmts.company_position = result_user_data[0]['company_position']
                            responsible_tmts.mobile = result_user_data[0]['mobile']
                            responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                            responsible_tmts.save()
                        except Responsible_TMTS_repair_Model.DoesNotExist:
                            raise Http404('Такой записи не существует')
                                    
                    else:   # 'Ответственный за ремонт' не существует в БД
                        # создаем объект Responsible_TMTS_repair_Model 
                        responsible_tmts = Responsible_TMTS_repair_Model()

                        responsible_tmts.fio = result_user_data[0]['fio']
                        responsible_tmts.account = result_user_data[0]['login']
                        responsible_tmts.email = result_user_data[0]['mail']
                        responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
                        responsible_tmts.company = result_user_data[0]['company']
                        responsible_tmts.company_position = result_user_data[0]['company_position']
                        responsible_tmts.mobile = result_user_data[0]['mobile']
                        responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
                        responsible_tmts.save()
                        
                    
                    form.instance.responsible_TMTS_repair = responsible_tmts   # сохраняем полученный объект Responsible_TMTS_repair_Model
                                
                    result_object = form.save()
                    
                
                        # ---------------------------------------------------------------------------
                        # # логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
                        # # created_dateTime=datetime.datetime.now()
                        # # updated_dateTime=datetime.datetime.now()
                        # action = 'создание'                    
                        # create_user = request.user
                        # # reestr_tmts_logging_CRUD_operations(result_object, created_dateTime, updated_dateTime, action, create_user)
                        # reestr_tmts_logging_CRUD_operations(result_object, action, create_user)
                        # ---------------------------------------------------------------------------
                    
                    # messages.success(request, "Запись успешно записана в БД.")        

                    
                    # переадресуем на главную страницу
                    return redirect('reestr_tmts_repair_list')

                else:                        
                    form =Reestr_TMTS_repair_Form(request.POST)
                    messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
                    messages.error(request, form.errors)
            
            except Exception:
                raise Http404('Такой записи не существует, либо статуса "в ремонте" не существует.')
                        
        else:
            form =Reestr_TMTS_repair_Form(request.POST)                    
            messages.error(request, form.errors)

    else:
        form =Reestr_TMTS_repair_Form()
    context = {
            'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'reestr_tmts_list',
        }        
    return render(request, 'laptop/create.html', context)
"""

















"""

# # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
# def reestr_tmts_repair_create_view(request, id):

#     if request.method == 'GET':
#         print("*"*35)
#         print("get   reestr_tmts_repair_create_view(request, id)")
#         print("*"*35)

#     if request.method == 'POST':

#         try:
#             data_tmts = get_object_or_404(Reestr_TMTS_Model, id=id)    
#         except Exception:
#             raise Http404('Такой записи не существует')
        
#         try:
#             data_tmts_status_repair = get_object_or_404(Status_TMTS_Model, id=2)
#         except Exception:
#             raise Http404('Статуса "в ремонте" не существует')
        
#         print("*"*35)
#         print("data_tmts_status_repair", data_tmts_status_repair)
#         print("data_tmts.status", data_tmts.status)
#         print("*"*35)

#         if data_tmts.status != data_tmts_status_repair:

#             print("*"*35)
#             print("if data_tmts.status != data_tmts_status_repair:")
#             print("*"*35)


#             data_tmts.status = data_tmts_status_repair # меняем статус на 'в ремонте'
#             data_tmts.save()

#             # ---------------------------------------------------------------------------
#             # логируем операцию изменения записи Reestr_TMTS_Model в Arhiv_Reestr_TMTS_Model        
#             action = 'в ремонт'        
#             action_user = request.user        
#             reestr_tmts_logging_CRUD_operations(data_tmts, action, action_user)
#             # ---------------------------------------------------------------------------


#             title_text = "Ремонт/обслуживание ТМЦ (добавление записи)"
#             # user_login = request.user

#             # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
#             if request.method == 'POST':
#                 print("*"*35)
#                 print("if request.method == 'POST':")
#                 print("*"*35)


#                 # Получаем из запроса только те данные которые использует форма
#                 form = Reestr_TMTS_repair_Form(request.POST)

#                 # Проверяем правильность введенных данных и сохраняем в базу        
#                 if form.is_valid():

#                     print("*"*35)
#                     print("if form.is_valid():")
#                     print("*"*35)

#                     form.instance.reestr_TMTS = data_tmts #'ТМЦ'

#                     form.instance.creator_account = request.user # записываем в скрытое поле "creator_account" данные по авторизированному пользователю (Кем изменено/создано)
                    
#                     result_user_data = select_user_data_ldap(form.instance.username_responsible_TMTS_repair)   # получаем информацию из AD по имени пользователя
                    
#                     # проверяем, что поле учетной записи не пустое (пользователь найден в AD)
#                     if result_user_data != []:      
#                         print("*"*35)
#                         print("result_user_data != []:")
#                         print("*"*35)          
                            
#                         # если 'Ответственный за ремонт' уже существует
#                         if Responsible_TMTS_repair_Model.objects.filter(account__iexact=form.instance.username_responsible_TMTS_repair.lower()).exists():
#                             try:
#                                 # обновляем запись (возможна смена фамилии/должности)                        
#                                 responsible_tmts = get_object_or_404(Responsible_TMTS_repair_Model, account__iexact=form.instance.username_responsible_TMTS_repair.lower())                            

#                                 responsible_tmts.fio = result_user_data[0]['fio']
#                                 # responsible_tmts.account = result_user_data[0]['login']
#                                 responsible_tmts.email = result_user_data[0]['mail']
#                                 responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
#                                 responsible_tmts.company = result_user_data[0]['company']
#                                 responsible_tmts.company_position = result_user_data[0]['company_position']
#                                 responsible_tmts.mobile = result_user_data[0]['mobile']
#                                 responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
#                                 responsible_tmts.save()
#                             except Responsible_TMTS_repair_Model.DoesNotExist:
#                                 raise Http404('Такой записи не существует')
                                
#                         else:   # 'Ответственный за ремонт' не существует в БД
#                             # создаем объект Responsible_TMTS_repair_Model 
#                             responsible_tmts = Responsible_TMTS_repair_Model()

#                             responsible_tmts.fio = result_user_data[0]['fio']
#                             responsible_tmts.account = result_user_data[0]['login']
#                             responsible_tmts.email = result_user_data[0]['mail']
#                             responsible_tmts.distingished_name = result_user_data[0]['distinguishedName']
#                             responsible_tmts.company = result_user_data[0]['company']
#                             responsible_tmts.company_position = result_user_data[0]['company_position']
#                             responsible_tmts.mobile = result_user_data[0]['mobile']
#                             responsible_tmts.telephone_number = result_user_data[0]['telephoneNumber']
#                             responsible_tmts.save()
                    
#                         form.instance.responsible_TMTS_repair = responsible_tmts   # сохраняем полученный объект Responsible_TMTS_repair_Model
                            
#                         result_object = form.save()


#                         # --------
#                         # # ---------------------------------------------------------------------------
#                         # # логируем операцию создания записи Reestr_TMTS_Model и добавления ее в Arhiv_Reestr_TMTS_Model
#                         # # created_dateTime=datetime.datetime.now()
#                         # # updated_dateTime=datetime.datetime.now()
#                         # action = 'создание'                    
#                         # create_user = request.user
#                         # # reestr_tmts_logging_CRUD_operations(result_object, created_dateTime, updated_dateTime, action, create_user)
#                         # reestr_tmts_logging_CRUD_operations(result_object, action, create_user)
#                         # # ---------------------------------------------------------------------------

#                         # -------- 

#                         # messages.success(request, "Запись успешно записана в БД.")

#                         # переадресуем на главную страницу
#                         return redirect('reestr_tmts_repair_list')            
                        
#                     else:
#                         # form.add_error('__all__', 'Ошибка! Проверьте правильность логина и пароля.')
#                         form =Reestr_TMTS_repair_Form(request.POST)
#                         messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
#                         messages.error(request, form.errors)
#                         # print('Ошибка! Проверьте правильность учетной записи.')
                        
#                 else:
#                     form =Reestr_TMTS_repair_Form(request.POST)
#                     # messages.error(request, 'Ошибка! Проверьте правильность учетной записи.')
#                     messages.error(request, form.errors)

#             else:
#                 form =Reestr_TMTS_repair_Form()
            
#             context = {
#                     # 'user_login': user_login,
#                     'data_tmts': data_tmts,
#                     'form': form,
#                     'title_text':title_text,
#                     'url_return_to_the_list':'reestr_tmts_list',
#                 }        
#             return render(request, 'laptop/create.html', context)
        
#         else:
#             messages.error(request, 'Ошибка! Уже данная запись уже в статусе "в ремонте".')
                
#             # переадресуем на страницу
#             return redirect('reestr_tmts_list')











"""






"""
# ***********************************************************************************************************************************************************
# Base_Search_Container_Model / Начальная (базовая) область поиска в AD

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def base_search_container_create_view(request):
    title_text = "Начальная (базовая) область поиска в AD (добавление записи)"
    # Проверяем, что запрос на добавление записи (POST) или просто на получение формы
    if request.method == 'POST':
        # Получаем из запроса только те данные которые использует форма
        form = Base_Search_Container_Form(request.POST)
        # Проверяем правильность введенных данных
        if form.is_valid():
            # сохраняем в базу
            form.save()
            # переадресуем на главную страницу
            return redirect('base_search_container_list')
    else:
        form =Base_Search_Container_Form()
    context = {
    'user_login': request.user,
            'form': form,
            'title_text':title_text,
            'url_return_to_the_list':'base_search_container_list',
        }        
    return render(request, 'laptop/create.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def base_search_container_list_view(request):
    form = Base_Search_Container_Form()

    # Получаем все записи
    dataset = Base_Search_Container_Model.objects.all()    

    title_text = "Начальная (базовая) область поиска в AD (список записей)"

    context = {
    'user_login': request.user,
            'form': form,
            'dataset': dataset,            
            'title_text':title_text,
            
        }    
    return render(request, 'laptop/base_search_container_listview.html', context)


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def base_search_container_detail_view(request, id):
    try:
        # Получаем запись по-определенному id
        data = Base_Search_Container_Model.objects.get(id=id)
        title_text = "Начальная (базовая) область поиска в AD"
    except Base_Search_Container_Model.DoesNotExist:
        raise Http404('Такой записи не существует') 
    return render(request, 'laptop/base_search_container_detailview.html', {'data': data, 'title_text': title_text})


# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def base_search_container_update_view(request, id):
    try:
        old_data = get_object_or_404(Base_Search_Container_Model, id=id)
        title_text = "Начальная (базовая) область поиска в AD (обновление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
    
    # Если метод POST, то это обновленные данные
    # Остальные методы - возврат данных для изменения
    if request.method =='POST':
        form = Base_Search_Container_Form(request.POST, instance=old_data)
        if form.is_valid():
            form.save()
            return redirect(f'/laptop/base_search_container/{id}')
    else:
        form = Base_Search_Container_Form(instance = old_data)
    context ={
            'form':form,
            'title_text':title_text,
            'url_return_to_the_list':'base_search_container_list',
        }
    return render(request, 'laptop/update.html', context)
    

# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
def base_search_container_delete_view(request, id):
    try:
        data = get_object_or_404(Base_Search_Container_Model, id=id)
        title_text = "Начальная (базовая) область поиска в AD (удаление записи)"
    except Exception:
        raise Http404('Такой записи не существует')
 
    if request.method == 'POST':
        data.delete()
        return redirect('base_search_container_list')
    else:
        return render(request, 'laptop/delete.html', {'title_text':title_text,'url_return_to_the_list':'base_search_container_list',})
    
"""
