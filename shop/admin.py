from django.contrib import admin
from . models import products,Contact,Orders,OrderUpdate

# Register your models here.
admin.site.register(products)
admin.site.register(Contact)
admin.site.register(Orders)
admin.site.register(OrderUpdate)