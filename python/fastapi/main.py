import uvicorn

from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, Request

from datetime import datetime, timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pymysql

class Item(BaseModel):
    title : str
    url : str
    type : str

class ItemList(BaseModel):
    items : List[Item]

def insert_Data(data_url_list):
    password = "PASSWORD"
    yackhu_db = pymysql.connect(
        user='root', 
        passwd=password, 
        host='127.0.0.1', 
        db='hoonzidata', 
        charset='utf8'
    )
    cursor = yackhu_db.cursor(pymysql.cursors.DictCursor)
    
    select_sql = """
    SELECT url FROM `urldata` WHERE url IN (%s)
    """

    insert_sql = """
    INSERT INTO `urldata` (title, url, type)
    VALUE (%s,%s,%s)
    """

    url_list = tuple([data_url[1] for data_url in data_url_list])

    format_strings = ",".join(['%s'] * len(data_url_list)) 
    cursor.execute(select_sql % format_strings, url_list)

    result = cursor.fetchall()
    result_url_list = [ info['url'] for info in result]

    for data_url in data_url_list:
        title = data_url[0]
        url = data_url[1]
        type_ = data_url[2]

        if url not in result_url_list:
            cursor.execute(insert_sql, (title, url, type_))

    yackhu_db.commit()
    cursor.close()

def select_url_page(limit=10, offset=0):
    password = "PASSWORD"
    yackhu_db = pymysql.connect(
        user='root', 
        passwd=password, 
        host='127.0.0.1', 
        db='hoonzidata', 
        charset='utf8'
    )

    cursor = yackhu_db.cursor(pymysql.cursors.DictCursor)
    
    select_sql = """
    SELECT title, url, type FROM `urldata` ORDER BY reg_date DESC LIMIT %s OFFSET %s
    """

    cursor.execute(select_sql, (limit, offset*limit))
    result = cursor.fetchall()
    cursor.close()
    return result

def delete_url():
    password = "PASSWORD"
    yackhu_db = pymysql.connect(
        user='root', 
        passwd=password, 
        host='127.0.0.1', 
        db='hoonzidata', 
        charset='utf8'
    )
    cursor = yackhu_db.cursor(pymysql.cursors.DictCursor)

    password = "PASSWORD"
    yackhu_db = pymysql.connect(
        user='root', 
        passwd=password, 
        host='127.0.0.1', 
        db='hoonzidata', 
        charset='utf8'
    )

    cursor = yackhu_db.cursor(pymysql.cursors.DictCursor)
    delete_sql = """
    DELETE FROM `urldata` WHERE reg_date < CURDATE() - interval 7 day
    """

    cursor.execute(delete_sql)
    result = cursor.fetchall()

    yackhu_db.commit()
    cursor.close()

app = FastAPI() 
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/") 
def read_root(): 
    return {"Hello": "World"}

@app.post("/items/")
async def insert_item(items: List[Item]):

    data_url_list = []
    for item in items:
        data_url_list.append([item.title, item.url,item.type])
    insert_Data(data_url_list)
    
    return items

@app.post("/itemsDelete")
async def return_urls():
    delete_url()
# @app.get("/items/{id}", response_class=HTMLResponse)
# async def read_item(request: Request, id: str):
#     return templates.TemplateResponse("item.html", {"request": request, "id": id})

@app.get("/items/{offset}", response_class=HTMLResponse)
async def return_urls(request: Request, offset : int):
    if offset < 1:
        offset = 1
    num_list = []
    if offset < 3:
        num_list = [1,2,3,4,5]
    else:
        for n in range(offset-2, offset+3):
            num_list.append(n)

    url_infos = select_url_page(limit=10, offset=offset)
    ItemList = url_infos

    return templates.TemplateResponse("urls.html",  
    {"request": request,
    "url_infos": ItemList, 
    "num_list" : num_list, 
    "offset" : offset})

    

if __name__ == "__main__":
    uvicorn.run(app,
    host="0.0.0.0",
    port=8000)