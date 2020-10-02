import requests
import bs4 as bs
import datetime
import time

BannerUsername='johngamal'
BannerPassword='HypoheticalPasswordHere'

C_number=   7
C_dept=     ['CSCE',    'MACT',     'CSCE',     'CSCE',     'CSCE',     'ARIC',     'CSCE']
C_id=       ['3301',    '2123',     '3302',     '3701',     '4930',     '3097',     '4930']
C_crn=      ['10090',   '10182',    '10697',    '11092',    '11608',    '10991',    '10985']
C_rep=      ['-1',      '-1',       '-1',       '-1',       '-1',       '-1',       '-1']
C_rem=      [-1000]*C_number


scrapper = {}
s = requests.Session()

R_crn=      ['10090',   '10182',    '10697',    '11092',    '11608',    '10991',    '10985']
R_day=      28

# def reserveCourse(CRN):
#     print(CRN)
#     for i in range(len(scrapper['CRN_IN'])):
#         if scrapper['CRN_IN'][i] == '':
#             scrapper['CRN_IN'][i]=CRN
#             break
#
#     print (scrapper)
#     reserve = s.post('https://ssb-prod.ec.aucegypt.edu/PROD/bwckcoms.P_Regs',data=scrapper)
#     # print(reserve.text)
#     buildScrapper()
#     # print(reserve.text)


def addCourse(CRN):
    print(CRN)
    for i in range(len(scrapper['CRN_IN'])):
        if scrapper['CRN_IN'][i] == '':
            scrapper['CRN_IN'][i]=CRN
            break

    print(scrapper)

def dropCourse(CRN):
    for i in range(len(scrapper['CRN_IN'])):
        if scrapper['CRN_IN'][i] == CRN:
            scrapper['RSTS_IN'][i]='DW'
            break

    print(scrapper)

def submitRequest():
    if scrapper != {}:
        reserve = s.post('https://ssb-prod.ec.aucegypt.edu/PROD/bwckcoms.P_Regs',data=scrapper)
        print(reserve.text)
        buildScrapper()

def buildScrapper():
    scrapper.clear()
    registerReq = {'term_in':'202110'}
    registrationHTML = s.post('https://ssb-prod.ec.aucegypt.edu/PROD/bwskfreg.P_AltPin',data=registerReq)
    soup = bs.BeautifulSoup(registrationHTML.text,'lxml')



    for form in soup.find_all('form'):
        for row in form.find_all('input') :
            name = row.get('name')
            if name and name != 'KEYWRD_IN':

                if name not in scrapper:
                    scrapper[name]=[]
                value = row.get('value')

                if value :
                    if value != 'Class Search':
                        scrapper[name].append(str(value).replace(' ','+'))
                else:
                    scrapper[name].append('')

                if name and value and name=='RSTS_IN' and value=='DUMMY':
                    for row in form.find_all('select') :
                        name = row.get('name')
                        if name:
                            if name not in scrapper:
                                scrapper[name]=[]

                            value = row.get('value')
                            if value :
                                scrapper[name].append(str(value).replace(' ','+'))
                            else:
                                scrapper[name].append('')
    print(scrapper)



def init():
    res = s.get('https://ssb-prod.ec.aucegypt.edu/PROD/twbkwbis.P_ValLogin')
    payload={'sid':[BannerUsername],'PIN':[BannerPassword]}
    r = s.post('https://ssb-prod.ec.aucegypt.edu/PROD/twbkwbis.P_ValLogin',params=payload)
    buildScrapper()

def scanUntilReserved():
    while(1):
        flag=0
        for i in range(C_number):
            courseData={'term_in':'202110', 'sel_subj':['dummy', C_dept[i]], 'SEL_CRSE':C_id[i],
                    'SEL_TITLE':'', 'BEGIN_HH':'0', 'BEGIN_MI':'0',
                    'BEGIN_AP':'a', 'SEL_DAY':'dummy', 'SEL_PTRM':'dummy', 'END_HH':'0',
                    'END_MI':'0', 'END_AP':'a', 'SEL_CAMP':'dummy', 'SEL_SCHD':'dummy',
                    'SEL_SESS':'dummy', 'SEL_INSTR':['dummy', '%'], 'SEL_ATTR':['dummy', '%'],
                    'SEL_LEVL':['dummy', '%'], 'SEL_INSM':'dummy', 'sel_dunt_code':'',
                    'sel_dunt_unit':'', 'call_value_in':'', 'rsts':'dummy', 'crn':'dummy', 'path':'1',
                    'SUB_BTN':'View+Sections'}

            courseHTML = s.post('https://ssb-prod.ec.aucegypt.edu/PROD/bwskfcls.P_GetCrse',data=courseData)
            soup = bs.BeautifulSoup(courseHTML.text,'lxml')

            cnt=-1
            for URL in soup.find_all('td'):
                if URL.string == C_crn[i]:
                    cnt=14
                if cnt==0:
                    C_rem[i]=int(URL.string)
                    if C_rem[i]>=1:
                        addCourse(C_crn[i])
                        if C_rep[i] != -1:
                            dropCourse(C_rep[i])
                        flag = 1
                cnt=cnt-1
        if flag:
            submitRequest()
            print('request sent')
        print(C_rem)
        time.sleep(3)                                                   ###can be removed for more sensitivity

def register():
    current_time = datetime.datetime.now()
    lastMin = current_time.minute
    while(1):
        current_time = datetime.datetime.now()
        if current_time.day != R_day-1:
            buildScrapper()
            for CRN in R_crn:
                addCourse(CRN)
            submitRequest()
        elif current_time.minute < lastMin or current_time.minute >= lastMin+3:
            refreshHTML = s.get('https://ssb-prod.ec.aucegypt.edu/PROD/bwskfcls.p_sel_crse_search')
            print('refreshed')
            print(refreshHTML.text)
            lastMin = current_time.minute

init()
# scanUntilReserved()
# register()

################################
"""
TODO:
1- organise                                         Done
2- Drops                                            Done
3- replace                                          Done
4- time handeling                                   Done
5- handle refreshing session                        Done
6- handle delays between requests and questions     Done
7- Documentation?                                   naaaaaaah
"""
################################

