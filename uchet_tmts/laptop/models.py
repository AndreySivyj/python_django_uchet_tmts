# -*- coding: UTF-8 -*-

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.timesince import timesince
import datetime
 

class Type_TMTS_Model(models.Model):
    type_tmts = models.CharField(max_length=50, verbose_name='Тип оборудования', unique=True, db_index=True)    

    class Meta:
        verbose_name_plural = '(1) Тип оборудования'
        verbose_name = 'Тип оборудования'
        ordering = ['type_tmts',]
    
    def __str__(self):
        return str(self.type_tmts)
    

class Name_TMTS_Model(models.Model):
    type_TMTS = models.ForeignKey('Type_TMTS_Model', on_delete=models.PROTECT, verbose_name='Тип оборудования')
    manufacturer = models.CharField(max_length=50, verbose_name='Производитель')
    name_model = models.CharField(max_length=50, verbose_name='Модель')

    class Meta:
        verbose_name_plural = '(1) Модели ТМЦ'
        verbose_name = 'Модель ТМЦ'
        ordering = ['type_TMTS', 'manufacturer', 'name_model']

    # def __iter__(self):
    #     # for field in self._meta.fields:
    #     #     yield (field.verbose_name, field.value_to_string(self))
        
    #     # field_names = [f.name for f in self._meta.fields]
    #     # for field_name in field_names:
    #     #     value = getattr(self, field_name, None)
    #     #     yield (field_name, value)

    
    def __str__(self):        
        return str(self.type_TMTS.type_tmts) + ' | ' + str(self.manufacturer) + ' | ' + str(self.name_model)
    
    # def get_absolute_url(self):
    #     return reverse('print-server', kwargs={'id': self.pk})


class Owner_TMTS_Model(models.Model):
    name_legal_entity = models.CharField(max_length=150, verbose_name='Юридическое лицо')

    class Meta:
        verbose_name_plural = '(1) Владелецы ТМЦ'
        verbose_name = 'Владелец ТМЦ'
        ordering = ['name_legal_entity',]
    
    def __str__(self):
        return str(self.name_legal_entity)
    

class Responsible_TMTS_Model(models.Model):
    fio = models.CharField(max_length=75, verbose_name='ФИО')
    account = models.CharField(max_length=50, verbose_name='Учетная запись')
    email = models.EmailField(verbose_name='Email')
    distingished_name = models.CharField(max_length=175, verbose_name='Имя объекта')
    company = models.CharField(max_length=75, blank=True, verbose_name='Юридическое лицо')
    company_position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    mobile = models.CharField(max_length=35, blank=True, verbose_name='Телефон (мобильный)')
    telephone_number = models.CharField(max_length=35, blank=True, verbose_name='Телефон')



    class Meta:
        verbose_name_plural = '(2) Ответственные за ТМЦ'
        verbose_name = 'Ответственный за ТМЦ'
        ordering = ['fio', 'account']
    
    def __str__(self):
        return str(self.fio) + ' | ' + str(self.account) + ' | ' + str(self.company) + ' | ' + str(self.company_position)\
                        + ' | ' + str(self.mobile) + ' | ' + str(self.telephone_number)



# class Base_Search_Container_Model(models.Model):
#     name_container = models.CharField(max_length=175, verbose_name='Начальный контейнер AD')
    
#     class Meta:
#         verbose_name_plural = '(2) Начальная (базовая) область поиска в AD'
#         verbose_name = 'Начальная (базовая) область поиска в AD'
#         ordering = ['name_container',]
    
#     def __str__(self):
#         return self.name_container


# ***********************************************************************************************************************************************************
class Status_TMTS_Model(models.Model):
    status = models.CharField(max_length=25, verbose_name='Статус', unique=True, db_index=True)   
    
    class Meta:
        # db_table='Status_printers' # указание имени таблицы в базе данных "вручную"
        verbose_name_plural = '(1) Статусы'
        verbose_name = 'Статус'
        ordering = ['id','status',]

    def __str__(self):
        return str(self.status)


class Reestr_TMTS_Model(models.Model):
    status = models.ForeignKey('Status_TMTS_Model', default=1, on_delete=models.PROTECT, verbose_name='Статус', related_name='status_tmts_fk')
    owner_TMTS = models.ForeignKey('Owner_TMTS_Model', on_delete=models.PROTECT, verbose_name='Владелец ТМЦ')
    name_TMTS = models.ForeignKey('Name_TMTS_Model', on_delete=models.PROTECT, verbose_name='Тип оборудования | Производитель | Модель')
    serial_number = models.CharField(max_length=50, blank=True, verbose_name='S/N', db_index=True)
    username_responsible_TMTS = models.CharField(max_length=50, blank=True, verbose_name='Учетная запись ответственного за ТМЦ')
    responsible_TMTS = models.ForeignKey('Responsible_TMTS_Model', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Ответственный за ТМЦ')
    location = models.CharField(max_length=100, blank=True, verbose_name='Локация/Кабинет')
    created = models.DateTimeField(auto_now_add=True, db_index=True)    
    creator_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Кем изменено/создано')
    updated = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, verbose_name='Комментарий') 
    start_of_operation_TMTS = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала эксплуатации ТМЦ')   
    archived = models.BooleanField(default=False, verbose_name='Утилизация')

    class Meta:
        verbose_name_plural = '(3) Учет ТМЦ'
        verbose_name = 'Учет ТМЦ'
        ordering = ['status', 'owner_TMTS', 'name_TMTS', 'username_responsible_TMTS',]        
        indexes = [
            models.Index(fields=['serial_number',]),
        ]

    # находим разницу между 'Дата начала эксплуатации ТМЦ' и текущей датой
    def delta_data(self):
        if self.start_of_operation_TMTS and self.created and self.updated:
            # return self.updated - self.created
            return datetime.datetime.now() - self.start_of_operation_TMTS        

    def __str__(self):


        if self.responsible_TMTS != None:
            return str(self.owner_TMTS.name_legal_entity) + ' | ' + str(self.name_TMTS.manufacturer) + ' | ' + str(self.name_TMTS.name_model)\
                + ' | ' + str(self.name_TMTS.type_TMTS.type_tmts) + ' | ' + str(self.serial_number) + ' | ' + str(self.responsible_TMTS.fio)
        else:
            return str(self.owner_TMTS.name_legal_entity) + ' | ' + str(self.name_TMTS.manufacturer) + ' | ' + str(self.name_TMTS.name_model)\
                + ' | ' + str(self.name_TMTS.type_TMTS.type_tmts) + ' | ' + str(self.serial_number) + ' | '
    
    # def get_absolute_url(self):
    #     return reverse('printers:printer_detail',
    #                    args=[self.name])


# лог изменения/добавления/удаления записей Reestr_TMTS_Model
class Arhiv_Reestr_TMTS_Model(models.Model):
    id_reestr_tmts = models.IntegerField(verbose_name='id ТМЦ')
    status = models.CharField(max_length=25, blank=True, verbose_name='Статус')
    owner_TMTS = models.CharField(max_length=150, blank=True, verbose_name='Владелец ТМЦ')    
    name_TMTS = models.CharField(max_length=150, blank=True, verbose_name='Тип оборудования | Производитель | Модель')
    serial_number = models.CharField(max_length=50, blank=True, verbose_name='S/N', db_index=True)
    username_responsible_TMTS = models.CharField(max_length=50, blank=True, verbose_name='Учетная запись ответственного за ТМЦ')
    responsible_TMTS = models.TextField(blank=True, verbose_name='Ответственный за ТМЦ')
    location = models.CharField(max_length=100, blank=True, verbose_name='Локация/Кабинет')
    created_reestr_tmts_model = models.DateTimeField(verbose_name='Дата создания записи')    
    creator_account = models.CharField(max_length=75, blank=True, verbose_name='Кем изменено/создано')    
    updated_reestr_tmts_model = models.DateTimeField(verbose_name='Дата изменения записи')
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    start_of_operation_TMTS = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала эксплуатации ТМЦ')
    archived = models.BooleanField(default=False, verbose_name='Утилизация')
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата действия', blank=True, )
    action = models.CharField(max_length=105, blank=True, verbose_name='Действие')
    creator_action = models.CharField(max_length=75, blank=True, verbose_name='Кем выполнено')

    class Meta:
        verbose_name_plural = '(4) Учет ТМЦ (архив)'
        verbose_name = 'Учет ТМЦ (архив)'
        ordering = ['created',]        
        # indexes = [
        #     models.Index(fields=['created',]),
        # ]

    def __str__(self):
        return  str(self.name_TMTS) + ' | ' + str(self.serial_number) + ' | ' + str(self.username_responsible_TMTS)\
                + ' | ' + str(self.created) + ' | ' + str(self.action) + ' | ' + str(self.creator_action)


# class Reestr_TMTS_Comments_Model(models.Model):
#     reestr_TMTS = models.ForeignKey('Reestr_TMTS_Model', blank=True, null=True, on_delete=models.PROTECT, verbose_name='Учет ТМЦ')
#     short_description = models.CharField(max_length=100, verbose_name='Краткое описание', default='')    
#     comment = models.TextField(verbose_name='Комментарий', default='')
#     created = models.DateTimeField(auto_now_add=True)
#     creator_account = models.CharField(max_length=50, blank=True, null=True, verbose_name='Кем изменен/создан')
#     updated = models.DateTimeField(auto_now=True, db_index=True)    

#     class Meta:
#         verbose_name_plural = '(3) Учет ТМЦ_Комментарии'
#         verbose_name = 'Учет ТМЦ_Комментарий'
#         ordering = ['created']
#         get_latest_by = 'updated' # поле типа DateField ИЛИ DateTimeField, которое будет взято в расчет при получении 
#                            # наиболее поздне/ранней записи  (методы latest() / earliest() вызванные без параметров)
#         indexes = [models.Index(fields=['created']),]
    
#     def __str__(self):
#         return self.short_description + ' | ' + str(self.updated)


# ***********************************************************************************************************************************************************
class Responsible_TMTS_repair_Model(models.Model):
    fio = models.CharField(max_length=75, verbose_name='ФИО')
    account = models.CharField(max_length=50, verbose_name='Учетная запись')
    email = models.EmailField(verbose_name='Email')
    distingished_name = models.CharField(max_length=175, verbose_name='Имя объекта')
    company = models.CharField(max_length=75, blank=True, verbose_name='Юридическое лицо')
    company_position = models.CharField(max_length=100, blank=True, verbose_name='Должность')
    mobile = models.CharField(max_length=35, blank=True, verbose_name='Телефон (мобильный)')
    telephone_number = models.CharField(max_length=35, blank=True, verbose_name='Телефон')


    class Meta:
        verbose_name_plural = '(5) Ответственные за ремонт/обслуживание'
        verbose_name = 'Ответственный за ремонт/обслуживание'
        ordering = ['fio', 'account']
    
    def __str__(self):
        return str(self.fio) + ' | ' + str(self.account) + ' | ' + str(self.company) + ' | ' + str(self.company_position)\
                        + ' | ' + str(self.mobile) + ' | ' + str(self.telephone_number)


class Reestr_TMTS_repair_Model(models.Model):
    reestr_TMTS = models.ForeignKey('Reestr_TMTS_Model', on_delete=models.PROTECT, verbose_name='ТМЦ')    
    username_responsible_TMTS_repair = models.CharField(max_length=50, blank=True, verbose_name='Учетная запись ответственного за ремонт/обслуживание')
    responsible_TMTS_repair = models.ForeignKey('Responsible_TMTS_repair_Model', on_delete=models.PROTECT, verbose_name='Ответственный за ремонт/обслуживание')    
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата регистрации')   
    creator_account = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, verbose_name='Кем изменено/создано')
    updated = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    comment = models.TextField(verbose_name='Комментарий', default='')
    archived = models.BooleanField(default=False, verbose_name='Переведен в архив')

    class Meta:
        verbose_name_plural = '(5) Ремонт(обслуживание) ТМЦ'
        verbose_name = 'Ремонт(обслуживание) ТМЦ'
        ordering = ['created', 'responsible_TMTS_repair',]        
        # indexes = [
        #     models.Index(fields=['serial_number',]),
        # ]

    def __str__(self):
        return str(self.reestr_TMTS.owner_TMTS.name_legal_entity) + ' | ' + str(self.reestr_TMTS.name_TMTS.manufacturer)\
                + ' | ' + str(self.reestr_TMTS.name_TMTS.name_model) + ' | ' + str(self.reestr_TMTS.name_TMTS.type_TMTS.type_tmts)\
                + ' | ' + str(self.reestr_TMTS.serial_number) + ' | ' + str(self.username_responsible_TMTS_repair) #+ ' | ' + self.created 
    
    # находим разницу между постановкой на ремонт и текущей датой
    def delta_data(self):
        if self.updated and self.created:
            # return self.updated - self.created
            return datetime.datetime.now() - self.created

    
    
    # def get_absolute_url(self):
    #     return reverse('printers:printer_detail',
    #                    args=[self.name])



# лог изменения/добавления/удаления записей Reestr_TMTS_repair_Model
class Arhiv_Reestr_TMTS_repair_Model(models.Model):
    id_reestr_tmts_repair = models.IntegerField(blank=True, verbose_name='id записи')
    id_reestr_tmts = models.IntegerField(blank=True, verbose_name='id ТМЦ')
    reestr_TMTS = models.TextField(blank=True, verbose_name='ТМЦ')    
    username_responsible_TMTS_repair = models.CharField(max_length=50, blank=True, verbose_name='Учетная запись ответственного за ремонт/обслуживание')
    responsible_TMTS_repair = models.TextField(blank=True, verbose_name='Ответственный за ремонт/обслуживание')    
    created_reestr_tmts_repair = models.DateTimeField(db_index=True, verbose_name='Дата регистрации') #created_reestr_tmts_repair = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата регистрации')
    creator_account = models.CharField(max_length=75, blank=True, verbose_name='Кем изменено/создано')     
    updated_reestr_tmts_repair = models.DateTimeField(verbose_name='Дата изменения')
    comment = models.TextField(verbose_name='Комментарий', default='')
    archived = models.BooleanField(default=False, verbose_name='Переведен в архив')
    created = models.DateTimeField(auto_now=True, db_index=True, verbose_name='Дата действия')
    action = models.CharField(max_length=105, blank=True, verbose_name='Действие')
    creator_action = models.CharField(max_length=75, blank=True, verbose_name='Кем выполнено')

    class Meta:
        verbose_name_plural = '(5) Ремонт(обслуживание) ТМЦ (архив)'
        verbose_name = 'Ремонт(обслуживание) ТМЦ (архив)'
        ordering = ['created',]        
        # indexes = [
        #     models.Index(fields=['-created',]),
        # ]

    def __str__(self):
        return str(self.reestr_TMTS) + ' | ' + str(self.username_responsible_TMTS_repair)\
                + ' | ' + str(self.created) + ' | ' + str(self.action) + ' | ' + str(self.creator_action)


# Добавление изображений к записям Reestr_TMTS_repair_Model
class Image_Reestr_TMTS_repair_Model(models.Model):
    # image_comment = models.CharField(max_length=150, blank=True, verbose_name='Описание')
    image_comment = models.TextField(verbose_name='Описание', default='')
    picture = models.ImageField(upload_to='images/%Y-%m-%d/',  verbose_name='Изображение')
    created = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата действия')
    # reestr_repair_TMTS = models.ForeignKey('Reestr_TMTS_repair_Model', on_delete=models.DO_NOTHING, verbose_name='Ремонт ТМЦ (id в реестре)')
    reestr_repair_TMTS = models.IntegerField(verbose_name='Ремонт ТМЦ (id в реестре)')

    class Meta:
        verbose_name_plural = '(6) Ремонт(обслуживание) ТМЦ (изображения)'
        verbose_name = 'Ремонт(обслуживание) ТМЦ (изображение)'
        ordering = ['created',]        
        # indexes = [
        #     models.Index(fields=['-created',]),
        # ]

    def __str__(self):
        return str(self.image_comment) + ' | ' + str(self.created)
        


# ***********************************************************************************************************************************************************

"""
# правильный запрос к БД (не делаются повторные запросы, при наличии связей, запрос один на все объекты)
    # cartridges = Cartridges.objects.select_related("cartridges_printers").prefetch_related("printers").all()
    # select_related("cartridges_printers") - для ForeignKey
    # prefetch_related("cartridges_printers") - для ManyToManyField


В качестве параметров select_related принимает имена ForeignKey/OneToOne полей или related_name поля OneToOne в связанной таблице. 
Также можно передавать имена полей в связанных через отношение внешнего ключа таблицах, например:

Employee.objects.all().select_related("city", "city__country")
# или вот так
Employee.objects.all().select_related("city").select_related("city__country")
# или вот так
Employee.objects.all().select_related("city__country")


В отличие от select_related, prefetch_related загружает связанные объекты отдельным запросом для каждого поля переданного
в качестве параметра и производит связывание объектов внутри python.
Однако prefetch_related можно также использовать там, где мы используем select_related, чтобы загрузить связанные записи используя дополнительный запрос, вместо JOIN.
"""






