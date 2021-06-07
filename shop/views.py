from django.shortcuts import render
from django.http import *
from .models import products, Contact, Orders ,OrderUpdate
from math import ceil
from django.core.mail import EmailMessage, send_mail
import logging
import json
from django.views.decorators.csrf import csrf_exempt 
from paytm import Checksum
from django.contrib import messages
MERCHANT_KEY = '@re!qkC#6Zv9TaB#'

# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.
# parmsdefault={}

def shop_home(request):
    # product = products.objects.all()
    # print(product)
    # n=len(product)
    # nSlides = n//4 + ceil((n/4)-(n//4))
    # allprods=[[product,range(1,nSlides),nSlides],[product,range(1,nSlides),nSlides]]
    # # parms= {'noofslides':nSlides,'product':product,'range':range(1,nSlides)}

    allprods = []
    catprods = products.objects.values('category', 'id')
    # print(catprods)
    cats = {item["category"] for item in catprods}
    for cat in cats:
        prod = products.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nSlides), nSlides])
    parms = {'allprods': allprods}
    return render(request, 'shop/shome.html',parms)


def shop_about(request):
    return render(request, 'shop/about.html')


def shop_contact(request):
    if request.method == "POST":
        print(request)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        subject = 'apcart contact'
        message = 'From: '+name+'\nemail : ' + \
            email + '\nphone : '+phone+'\n\n\n' + desc
        send_mail(subject, message, email, [
                  'arpanmistry8000@yahoo.com'], fail_silently=False)
        msg1='Dear'+name+',\nThank you so much to contact us!\nOur customer support executer will soon Respond to you.'          
        send_mail('apCart Support',msg1, email, [
                  email], fail_silently=False)
        return render(request,'shop/respond.html',{'name':str(name),'phone':str(phone),'email':str(email)})
    else:
        return render(request, 'shop/contact.html')


def shop_tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps([updates, order[0].items_json],default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{}')
        except Exception as e:
            return HttpResponse('{}')

    return render(request, 'shop/tracker.html')


def shop_search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = products.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = products.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod) != 0:
            allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods': allprods, "msg": ""}
    if len(allprods) == 0 or len(query)<4:
        params = {'msg': "Please make sure to enter relevant search query"}
    return render(request, 'shop/search.html', params)


def searchMatch(query, item):
    '''return true only if query matches the item'''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False


def productView(request, myid):
    product = products.objects.filter(id=myid)
    # print(product)
    parms = {'product': product[0]}
    return render(request, 'shop/prod.html', parms)


def shop_checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + \
            " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        order = Orders(items_json=items_json, name=name,amount=amount, email=email,
                       address=address, city=city, state=state, zip_code=zip_code, phone=phone)
        order.save()
        #--------------------------------------------------------------
        update = OrderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        #------------------------------------------------------------------
        
        id = order.order_id

    #     return render(request, 'shop/checkout.html', {'thank': thank, 'id': id})
    # return render(request, 'shop/checkout.html')
        param_dict = {

                'MID': 'bphAMo39412919623429',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shome/handlepayment/',

        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request, 'shop/paytm.html', {'param_dict': param_dict})

    return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            # print('order successful')
            order = Orders.objects.filter(order_id=response_dict['ORDERID'])
            # print(order[0].email)
            json_obj = json.loads(order[0].items_json)
            orderdetails = ''
            for x in json_obj:
                list = json_obj[x]
                orderdetails = orderdetails+'ProductName : ' + \
                    list[1]+'  Quantity:'+str(list[0])+'\n'
            zip_code = str(order[0].zip_code)
            phone = str(order[0].phone)
            id = str(order[0].order_id)
            amount1=str(order[0].amount)
            name=str(order[0].name)
            email=str(order[0].email)
            address=str(order[0].address)
            city=str(order[0].city)
            state=str(order[0].state)
            subject = 'Order Details apCart'
            message = 'Dear '+name+',\nThank You For shopping at apCart\nWe have successfully received your payment!'+'\nTotal Amount : '+amount1 +'/- Rs'+'\nTransaction id : \n'+str(response_dict['TXNID'])+'\nYour Order is ready for shipping\n\nDetails:\n'+orderdetails+'\n\nshipping details:\n'+name+',\n'+address+',\n'+city+',\n'+state+',\n'+zip_code+',\nContact number:'+phone+'\nOrderId:'+id+'\nYou can easily Track your order on our site with orderid : '+id+'\nKeep shoping with apcart,\nfor any query you can contact us Any time\nThank you!'
            send_mail(subject, message, email, [email], fail_silently=False)
            msg1='Dear Admin Congretulations!\nWe have received Order Request with below detals:\nOrderID : '+id+'\n\n'+orderdetails+'\n\n Amount Receivrd : '+amount1+'\nTransaction id : \n'+str(response_dict['TXNID'])+'\n\nshipping details:\n'+name+',\n'+address+',\n'+city+',\n'+state+',\n'+zip_code+',\nContact number:'+phone
            send_mail('apCart New Order Request', msg1, email, ['arpanmistry8000@yahoo.com'], fail_silently=False)
            update=Orders.objects.get(order_id=id)
            update.payment='successful'
            update.save()
            thank = True
            return render(request, 'shop/paymenttrue.html', {'thank': thank, 'id': id,'email':email})
        else:
            return render(request,'shop/paymentfalse.html')
    return render(request,'shop/paymentfalse.html')