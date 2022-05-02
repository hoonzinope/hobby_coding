import requests
from bs4 import BeautifulSoup
import re

class crawler:

    keywords = []

    def __init__(self) -> None:
        self.keywords = ['ㅇㅎ','후방','약후','ㅎㅂ']

    # ygosu ㅇㅎ return
    def ygosu_url_return(self):
        type_ = 'ygosu'
        
        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = "https://ygosu.com/all_search/?type=&add_search_log=Y&keyword={}".format(keyword)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            ul = soup.find('ul', {'id': "board_search_result"})
            for sub_ul in ul.find_all('ul'):
                if sub_ul.find("li",{'class':'thumbnail_li'}):
                    a = sub_ul.find('a',{'class':"subject"})

                    title = a.text
                    url = a.get('href')
                    if url not in url_set:
                        title_url_list.append([title, url, type_])
                        url_set.add(url)
        self.db_insert_query(title_url_list)        
        return title_url_list

    # fmkorea ㅇㅎ return
    def fmkorean_url_return(self):
        type_ = "fmkorea"

        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = "https://www.fmkorea.com/index.php?mid=home&act=IS&where=document&search_target=title&is_keyword={}&page=1".format(keyword)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            ul = soup.find('ul',{'class':'searchResult'})

            for li in ul.find_all("li"):
                a = li.find('a')
                title = a.text
                title = re.sub('\[[^\]]*\]','', title)
                title = title.strip()
                
                url = "https://www.fmkorea.com"+a.get('href')
                if url not in url_set:
                    title_url_list.append([title, url, type_])
                    url_set.add(url)
        self.db_insert_query(title_url_list)
        return title_url_list

    #dogdrip ㅇㅎ return
    def dogdrip_url_return(self):
        type_ = 'dogdrip'

        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = "https://www.dogdrip.net/?_filter=search&act=&vid=&mid=userdog&category=&search_target=title&search_keyword={}".format(keyword)
            headers = {
                'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')

            for tr in soup.find_all("tr",{'class':''}):
                if tr.find('td',{'class':'title'}):
                    ahref = tr.find('a',{'class':'ed link-reset'})
                    title = ahref.find('span',{'class':'ed title-link'}).text
                    url = "https://www.dogdrip.net"+ahref.get("href")

                    if url not in url_set:
                        title_url_list.append([title, url, type_])
                        url_set.add(url)
        return title_url_list

    # etorent ㅇㅎ return
    def etorent_url_return(self):
        type_ = "etoland"

        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = 'http://www.etoland.co.kr/bbs/board.php?bo_table=hit&sca={}'.format(keyword)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for a in soup.find_all('a',{'class':'subject_a '}):
                url = "http://www.etoland.co.kr"+a.get('href').replace("..","")
                title = a.text
                if url not in url_set:
                    title_url_list.append([title, url, type_])
                    url_set.add(url)
        self.db_insert_query(title_url_list)            
        return title_url_list

    # dc ㅇㅎ return
    def dc_mom_url_return(self):
        type_ = "dc_mom"
        url = "https://gall.dcinside.com/mgallery/board/lists/?id=beautifulbody&sort_type=N&search_head=0&page=1"
        headers = {
            'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        url_set = set()
        title_url_list = []
        for tr in soup.find_all('tr',{'class':'ub-content us-post'}):
            if tr.find('em',{'class':'icon_img icon_notice'}):
                continue
            else:
                a = tr.find('a')
                title = a.text
                url = "https://gall.dcinside.com"+a.get('href')

                if url not in url_set:
                    title_url_list.append([title, url, type_])
                    url_set.add(url)
        self.db_insert_query(title_url_list)
        return title_url_list

    # td ㅇㅎ return
    def today_humor_url_return(self):
        type_ = "today_humor"

        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = "http://www.todayhumor.co.kr/board/list.php?kind=search&table=humordata&search_table_name=humordata&keyfield=subject&keyword={}".format(keyword)
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for tr in soup.find_all('tr',{'class':'view list_tr_humordata'}):
                td = tr.find('td',{'class':'subject'})
                a = td.find('a')

                title = a.text
                url = "http://www.todayhumor.co.kr"+a.get('href')

                if url not in url_set:
                    title_url_list.append([title, url, type_])
                    url_set.add(url)
        self.db_insert_query(title_url_list)
        return title_url_list

    def bobadream_url_return(self):
        type_ = "bobadream"
        url_set = set()
        title_url_list = []
        for keyword in self.keywords:
            url = "https://www.bobaedream.co.kr/list.php?code=strange&s_cate=&maker_no=&model_no=&or_gu=10&or_se=desc&s_selday=&pagescale=30&info3=&noticeShow=&bestCode=&bestDays=&bestbbs=&vdate=&ndate=&nmdate=&s_select=Subject&s_key={}".format(keyword)
            headers = {
                    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
                }
            response = requests.get(url, headers= headers)
            response.raise_for_status()
            response.encoding = "utf-8"
            soup = BeautifulSoup(response.text, 'html.parser')
            for tr in soup.find_all('tr'):
                if tr.get("itemtype"):
                    a = tr.find('a')
                    title = a.text
                    url = "https://www.bobaedream.co.kr"+a.get('href')

                    if url not in url_set:
                        title_url_list.append([title, url, type_])
                        url_set.add(url)
        self.db_insert_query(title_url_list)
        return title_url_list

    def db_insert_query(self,data_url_list):
        post_data = []
        for data_info in data_url_list:
            temp_dict = {}
            temp_dict['title'] = data_info[0]
            temp_dict['url'] = data_info[1]
            temp_dict['type'] = data_info[2]    
            post_data.append(temp_dict)

        api_url = "http://localhost:8000/items/"
        response = requests.post(api_url, json=post_data)

    def db_delete_query(self):
        api_url = "http://localhost:8000/itemsDelete/"
        response = requests.post(api_url)    