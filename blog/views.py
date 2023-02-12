from django.shortcuts import render
from .models import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from django.db.models import Avg, Count
from django.db.models.functions import TruncMonth


# 홈페이지 요청---------------------------------------------------------
def index(request):
    return render(request,'blog/index.html')


# 연동 페이지 요청-----------------------------------------------------
def connect(request):
    products = Products.objects.all()[:5]
    customers = Customers.objects.all()[:5]
    employees = Employees.objects.all()[:5]
    offices = Offices.objects.all()[:5]
    orderdetails =Orderdetails.objects.all()[:5]
    payments =Payments.objects.all()[:5]
    productlines = Productlines.objects.all()[:5]
    orders = Orders.objects.all()[:5]
    return render(request, 'blog/connect.html',{
        'products':products,
        'customers':customers,
        'employees':employees,
        'offices':offices,
        'orderdetails':orderdetails,
        'payments':payments,
        'productlines':productlines,
        'orders':orders
    })


#  분석 페이지 요청 ---------------------------------------------
def analyze(request):

    # 나라별 고객 수--------------------------------------
    customers_anl = Customers.objects.values('customernumber','customername','country','creditlimit')
    customers_anl_df = pd.DataFrame(customers_anl)
    customers_anl_df = customers_anl_df.groupby('country',as_index=False).agg(총원=('customernumber','count')).sort_values('총원',ascending=False).reset_index(drop=True)[:5]
    # 나라별 고객 수-------------------------------------------
    
    # 나라별 평균 카드한도 금액--------------------------------------
    customers__credit_anl_df = pd.DataFrame(customers_anl)
    customers_credit_anl_df = customers__credit_anl_df.groupby('country',as_index=False).agg(한도평균=('creditlimit','mean')).sort_values('한도평균',ascending=False).reset_index(drop=True)[:5]
    # 나라별 평균 카드한도 금액--------------------------------------

    # 년도별,월별 상품 주문 건수------------------------------------------
    orders = Orders.objects.values('ordernumber','orderdate')
    orders_df = pd.DataFrame(orders)
    orders_df['year'] = orders_df['orderdate'].map(lambda x : str(x.year) + '년')
    orders_df['month'] = orders_df['orderdate'].map(lambda x : str(x.month) + '월')
    orders_grby_year = orders_df.groupby('year',as_index=False).agg(건수=('ordernumber','count')).sort_values('year',ascending=True).reset_index(drop=True)
    orders_grby_month = orders_df.groupby('month',as_index=False).agg(건수=('ordernumber','count')).sort_values('건수',ascending=False).reset_index(drop=True)[:5]
    # 년도별,월별 상품 주문 건수------------------------------------------

    # 생산 라인별 평균 가격-----------------------------------------------
    products = Products.objects.values('productline','buyprice')
    products_df = pd.DataFrame(products)
    products_grby_price = products_df.groupby('productline',as_index=False).agg(평균가격=('buyprice','mean')).sort_values('평균가격',ascending=False).reset_index(drop=True)
    # 생산 라인별 평균 가격-----------------------------------------------

    # 지사별 직원 수----------------------------------------------
    employees = Employees.objects.values('employeenumber','officecode')
    employees_df = pd.DataFrame(employees)
    offices = Offices.objects.values('officecode','city')
    offices_df = pd.DataFrame(offices)
    code_empl_merge = pd.merge(employees_df,offices_df,on='officecode')[['city','employeenumber']]
    merge_grby = code_empl_merge.groupby('city',as_index=False).agg(직원수=('employeenumber','count'))
    # 지사별 직원 수----------------------------------------------

    customers_anl_contect = {'customers_anl':customers_anl_df.to_html(justify='center',border=0,classes='table table-striped'),
                             'customers_credit_contect':customers_credit_anl_df.to_html(justify='center',border=0,classes='table table-striped'),
                             'orders_grby_year':orders_grby_year.to_html(justify='center',border=0,classes='table table-striped'),
                             'orders_grby_month':orders_grby_month.to_html(justify='center',border=0,classes='table table-striped'),
                             'products_grby_price':products_grby_price.to_html(justify='center',border=0,classes='table table-striped'),
                             'merge_grby':merge_grby.to_html(justify='center',border=0,classes='table table-striped')
    }



    return render(request, 'blog/analyze.html',customers_anl_contect)


#  시각화 페이지 요청-----------------------------------------------
def visualization(request):

    # 년도별 고객수 시각화--------------------------------------------
    co1 = Orders.objects.filter(orderdate__contains='2003').count()
    co2 = Orders.objects.filter(orderdate__contains='2004').count()
    co3 = Orders.objects.filter(orderdate__contains='2005').count()
    co_label_list = [2003,2004,2005]
    co_list = [co1, co2, co3]

    # 2003년도 월별 고객 수 시각화-------------------------------------------------
    month_no_cus = Orders.objects.filter(orderdate__year=2003).annotate(month=TruncMonth('orderdate')).values('month')\
        .annotate(cnt=Count('ordernumber')).values('month','cnt').order_by('-cnt')[:5]
    month_no_cus_list = []
    month_no_cus_cnt_list = []
    for ind in range(month_no_cus.count()):
        month_no_cus_list.append(dict(month_no_cus[ind])['month'])
        month_no_cus_cnt_list.append(dict(month_no_cus[ind])['cnt'])


    # customers의 나라별 고객 신용 한도 top5------------------------------------
    # cry에 ORM으로 
    cry = Customers.objects.values('country').annotate(avg=Avg('creditlimit')).values('country','avg').order_by('-avg')[:5]
    cry_list = []
    cry_avg_list = []
    for ind in range(cry.count()):
        cry_list.append(dict(cry[ind])['country'])
        cry_avg_list.append(dict(cry[ind])['avg'])
        
    # customers의 나라별 고객 수 Top5-----------------------------------
    cus_no = Customers.objects.values('country').annotate(count=Count('customernumber')).values('country','count').order_by('-count')[:5]
    cus_no_list = []
    cus_no_count_list = []
    for ind in range(cus_no.count()):
        cus_no_list.append(dict(cus_no[ind])['country'])
        cus_no_count_list.append(dict(cus_no[ind])['count'])

    # 생산 라인별 평균 가격-----------------------------------------------
    prd_no = Products.objects.values('productline').annotate(mean=Avg('buyprice')).values('productline','mean')
    pro_no_list=[]
    pro_no_mean_list=[]
    for ind in range(prd_no.count()):
        pro_no_list.append(dict(prd_no[ind])['productline'])
        pro_no_mean_list.append(dict(prd_no[ind])['mean'])
    # 생산 라인별 평균 가격-----------------------------------------------
    
    # 도시별 직원 수----------------------------------------------------
    city_em = Employees.objects.values('officecode').annotate(count=Count('employeenumber')).values('officecode__city','count')
    city_list =[]
    city_empl_no = []
    for ind in range(city_em.count()):
        city_list.append(dict(city_em[ind])['officecode__city'])
        city_empl_no.append(dict(city_em[ind])['count'])
    # 도시별 직원 수----------------------------------------------------
    
    connect = {'co_label_list':co_label_list,'co_list':co_list,'cry_list':cry_list,
               'cry_list':cry_list,'cry_avg_list':cry_avg_list,'cus_no_list':cus_no_list,'cus_no_count_list':cus_no_count_list,
               'month_no_cus_list':month_no_cus_list, 'month_no_cus_cnt_list':month_no_cus_cnt_list,
               'pro_no_list':pro_no_list, 'pro_no_mean_list':pro_no_mean_list,
               'city_list':city_list, 'city_empl_no':city_empl_no}
    return render(request,'blog/visualization.html',connect)







