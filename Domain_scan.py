from fake_useragent import UserAgent
import re
import lxml
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas import DataFrame as df
import random
proxies = {'http': '127.0.0.1:9050',
            'https': '127.0.0.1:9050',}
ua = UserAgent()
skus = ['78e66a63-337a-4a9a-8959-41c6654dfb56',
        'e82ae690-a2d5-4d76-8d30-7c6e01e6022e',
        '94763226-9b3c-4e75-a931-5c89701abe66',
        '314c4481-f395-4525-be8b-2ec4bb1e9d91']

def data_need(sku,domain):
    url = 'https://signup.microsoft.com/signup?skug=Education&sku=%(sku)s'%{"sku":sku}
    headers = {
        'accept': '*/*',
        'upgrade-insecure-requests': '1',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://signup.microsoft.com',
        'referer': 'https://signup.microsoft.com/signup?skug=Education&sku=%(sku)s'%{"sku":sku},
        'user-agent': ua.random,}
    datas = {
        'StepsData.Email': '%(name)s@%(domain)s'%{"name": int(random.random()*100000000), "domain":domain},
        'SkuId': sku,
        'skug': 'Education'}
    return url,headers,datas

def request_post(url, headers, proxies, datas):
    try:
        req = requests.request("POST", url, headers=headers, proxies=proxies, params=datas)
    except requests.exceptions.RequestException:
        req = request_post(url, headers, proxies, datas)

    return (req)

def get_domain_can_register(domain, T_list):
    url = "https://who.is/whois/" + domain
    x = requests.get(url)
    if "No match for" in x.text or "NOT FOUND" in x.text:
        print('%(domain)s havenot registered'%{"domain":domain})
    else:
        T_list.append(9)
        T_list.append(9)
        T_list.append(9)
        return T_list


def openfile(filename):
    file = open(filename,'r')
    a = file.read()[1:-1].replace("'", "").replace(" ", "")
    list1 = a.split(',')
    file.close()
    return list1

filename = 'co.txt'
domains = openfile(filename)

domain_df = df(columns = ['domain', 'A1PT', 'A1PS', 'A1T', 'A1S'])
numbers = len(domains)
number = 0
for domain in domains:
    number += 1
    print('{} of {}'.format(number,numbers))
    T_list = []
    T_list.append(domain)
    for sku in skus:
        url,headers,datas = data_need(sku,domain)
        while 1:
            req = request_post(url, headers, proxies, datas)
            soup = BeautifulSoup(req.text, 'html.parser')
            h2 = str(re.compile(r'<[^>]+>', re.S).sub('', str(soup.select('h2'))))
            ver = str(re.compile(r'<[^>]+>', re.S).sub('', str(soup.select('#VerificationCodeTitleText'))))
            phone = str(re.compile(r'<[^>]+>', re.S).sub('', str(soup.select('#SMSTryAgainLink_before'))))

            if phone.find("Didn't get it or need a new code") != -1:
                continue
            elif h2.find("Your school is eligible for Office 365 Education") != -1:
                T_list.append(1)
                break
            elif h2.find("institution doesn't meet our academic eligibility requirements to receive Office 365 for free") != -1:
                T_list.append(5)
                break
            elif h2.find("isn't on our list of eligible intitutions") != -1:
                T_list.append(0)
                break
            elif ver.find("Enter the code to complete signup") != -1:
                T_list.append(2)
                break

            else:
                T_list.append(3)
                print(soup)
                print(h2)
                print(ver)
                print(phone)
    print(T_list)
    domain_df.to_csv("co.csv")
    domain_df.loc[len(domain_df)] = T_list
domain_df.to_csv("co.csv")
