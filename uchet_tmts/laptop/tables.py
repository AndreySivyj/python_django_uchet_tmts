# laptop/tables.py
import django_tables2 as tables
from .models import Reestr_TMTS_Model

class Reestr_TMTS_Model_Table(tables.Table):
    class Meta:
        model = Reestr_TMTS_Model
        # template_name = "django_tables2/bootstrap_htmx.html"


        # show_header = False
        # template_name = "laptop/reestr_tmts.html"


        # fields = ('id', 'status', 'owner_TMTS', 'name_TMTS', 'serial_number', 'username_responsible_TMTS', 'responsible_TMTS', 'location',
        #             'created', 'creator_account', 'updated', 'comment', 'archived',)
        
        
        # attrs = {'class': 'paleblue'}