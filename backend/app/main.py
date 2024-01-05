from pathlib import Path
from fastapi import  FastAPI, UploadFile, Form
from starlette.responses import FileResponse
from pydantic import BaseModel

import time
import sqlite3

from datetime import datetime

app = FastAPI()

# エラー422の対策
class Item(BaseModel):
    s:str

# データベースにある資料を検索
@app.post("/api/serchAll")
def searchAll():
    print("search!")
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    result = cur.execute("SELECT * FROM file")
    for  item  in  result.fetchall():
        # print(item[6])
        file_path = Path(item[6])
        if(file_path.exists() is not True):
            print("file_path?")
            print("path: "+item[6])
            cur.execute(f"DELETE FROM file WHERE SAVE_NAME = '{item[7]}'")
            con.commit()

    result = cur.execute("SELECT * FROM file WHERE DEL_FLG = 0")
    resultReturn = []
    for  item  in  result.fetchall():
        resultReturn.append(item)
    con.close()

    # 検索結果を返す
    return {'code': '200', 'testData': resultReturn}

# ファイルをアプロード
@app.post("/api/upload")
def upload(file: UploadFile,clientName: str = Form(...)):

    print("clientName: "+clientName)
    
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # cur.execute("DROP TABLE client")
    cur.execute("CREATE TABLE IF NOT EXISTS client(CLIENT_NAME varchar(3) primary key,FILE_NAME_COUNTER varchar(14))")
    
    clientNameNumOrigin = cur.execute(f"""select count(*) from client
                   where client.CLIENT_NAME ='{clientName}';
                """)
    for item in clientNameNumOrigin:
        clientNameNum = item[0]
    current_dateTime = datetime.now()
    current_dateTime_fix = str('{:0>4d}'.format(current_dateTime.year)+'{:0>2d}'.format(current_dateTime.month)+'{:0>2d}'.format(current_dateTime.day))
    if(clientNameNum == 0):
        cur.execute(f"""
            INSERT INTO client VALUES
                ('{clientName}', '{current_dateTime_fix}000000');
        """)
        con.commit()
    result = cur.execute(f"SELECT * FROM client WHERE CLIENT_NAME = '{clientName}'")
    for  item  in  result.fetchall():
        clientNum = item[1]
    
    # 1. 判斷clientNum是否為今天
    if(clientNum[:-6] != current_dateTime_fix):
        #    1. 為今天的情況(數字加1)
        clientNumTemp = int(clientNum[8:])
        clientNumTemp += 1
        clientNumTempStr = str('{:0>6d}'.format(clientNumTemp))
        clientNumNew = clientNum[:-6]+clientNumTempStr
    else:
        #    2. 不為今天的情況(日期更新&計數改成"000001")
        clientNumNew = current_dateTime_fix+"000001"

    # 受け入れたファイルをbytesとして保存、ファイル名も保存
    fileBytes = file.file.read()
    fileName = file.filename
    # 指定されたパスで当ファイルをアーカイブ
    fout = open("./database/"+clientNumNew+clientName+"."+fileName.split(".")[-1], 'wb')
    fout.write(fileBytes)
    fout.close()

    # データベースに必要な資料を用意
    path = Path('./database', clientNumNew+"."+fileName.split(".")[-1])
    fileSize = path.stat().st_size
    # fileUpdateTime = time.localtime(path.stat().st_mtime)
    fileUpdateTimeOrigin = time.strftime("%Y-%m-%d",time.localtime(path.stat().st_mtime))
    fileUpdateTime = fileUpdateTimeOrigin.split("-")
    fileUpdateYear = fileUpdateTime[0]
    fileUpdateMonth = fileUpdateTime[1]
    fileUpdateDay = fileUpdateTime[2]
    fileType = fileName.split(".")[-1]

    cur.execute("DROP TABLE file")
    
    # テーブルを作る（もしなければ）
    cur.execute("CREATE TABLE IF NOT EXISTS file(FILE_NAME varchar(270) primary key,FILE_SIZE integer,UPDATE_YEAR varchar(4),UPDATE_MONTH varchar(2),UPDATE_DAY varchar(2),FILE_FORMAT varchar(10),FILE_PATH varchar(270),SAVE_NAME varchar(17),DEL_FLG INTEGER DEFAULT 0)")
    # cur.execute("CREATE TABLE IF NOT EXISTS file(FILE_NAME varchar(270) primary key,FILE_SIZE integer,UPDATE_YEAR varchar(4),UPDATE_MONTH varchar(2),UPDATE_DAY varchar(2),FILE_FORMAT varchar(10),FILE_PATH varchar(270),DEL_FLG INTEGER DEFAULT 0)")
    
    try: 
        # 資料をテーブルに追加
        cur.execute(f"""
            INSERT INTO file VALUES
                ('{fileName}', {fileSize}, '{fileUpdateYear}', '{fileUpdateMonth}', '{fileUpdateDay}', '{fileType}', './database/{clientNumNew}{clientName}.{fileType}', '{clientNumNew}{clientName}', 0);
        """)
        # cur.execute(f"""
        #     INSERT INTO file VALUES
        #         ('{fileName}', {fileSize}, '{fileUpdateYear}', '{fileUpdateMonth}', '{fileUpdateDay}', '{fileType}', './database/{fileName}', '{clientNumNew}{clientName}', 0);
        # """)
        con.commit()
        print("01")
    except:
        # print("02")
    #     # テーブル中の資料を更新（もし当ファイル名が既に存在している）
    #     cur.execute(f"""
    #          UPDATE file
    #             SET FILE_NAME = '{fileName}',
    #                 FILE_SIZE = {fileSize},
    #                 UPDATE_YEAR = '{fileUpdateYear}',
    #                 UPDATE_MONTH = '{fileUpdateMonth}',
    #                 UPDATE_DAY = '{fileUpdateDay}',
    #                 FILE_FORMAT = '{fileType}',
    #                 FILE_PATH = './database/{fileName}',
    #                 DEL_FLG = 0
    #                 WHERE FILE_NAME = '{fileName}'
    #     """)
    #     con.commit()
        print("02")

    # 成功メッセージを返す
    return {'code': '200'}

# ファイルをダウンロード
@app.post("/api/download")
def download(s:Item):
    
    # ファイルパスとファイル名を取得
    filePath = Path(str(s).split("'")[-2])
    fileName = str(s).split("'")[-2].split(".")[0]

    # 当ファイルパスでファイルを読み取り、ファイル名とともに返す
    return FileResponse(filePath, filename=fileName, media_type='application/octet-stream')

# ファイルをダウンロード
@app.post("/api/delete")
def delete(s:Item):
    fileName = str(s).split("'")[-2].split("/")[-1]

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()
    cur.execute(f"""
             UPDATE file
                SET DEL_FLG = 1
                    WHERE FILE_NAME = '{fileName}'
        """)
    con.commit()

    # 成功メッセージを返す
    return {'code': '200'}

# ホームページ
@app.get("/")
async def get_index():
    return FileResponse('public/index.html')

# urlが見つからない場合
@app.get("/{whatever:path}")
async def get_static_files_or_404(whatever):
    # パスを取得
    file_path = Path("public").joinpath(whatever)
    # パスがファイルの場合、ファイルを返す
    if (file_path).is_file():
        return FileResponse(file_path)
    # パスがファイルではなかった場合、ホームページに戻る
    return FileResponse('public/index.html')