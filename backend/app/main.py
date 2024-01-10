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
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    result = cur.execute("SELECT * FROM file")
    for  item  in  result.fetchall():
        file_path = Path(item[7])
        # ファイルがファイルパスにない場合、データベースにある資料を削除
        if(file_path.exists() is not True):
            cur.execute(f"DELETE FROM file WHERE FILE_NO = {item[0]}")
            con.commit()

    # 削除してないデータを検索
    result = cur.execute("SELECT * FROM file WHERE DEL_FLG = 0")
    resultReturn = []
    # 検索結果を取り出す
    for  item  in  result.fetchall():
        resultReturn.append(item)
    con.close()

    # 検索結果を返す
    return {'code': '200', 'testData': resultReturn}

@app.post("/api/serchAllTrashCan")
def serchAllTrashCan():
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    result = cur.execute("SELECT * FROM file")
    for  item  in  result.fetchall():
        file_path = Path(item[7])
        # ファイルがファイルパスにない場合、データベースにある資料を削除
        if(file_path.exists() is not True):
            cur.execute(f"DELETE FROM file WHERE FILE_NO = {item[0]}")
            con.commit()

    result = cur.execute("SELECT * FROM file WHERE DEL_FLG = 1")
    resultReturn = []
    # 検索結果を取り出す
    for  item  in  result.fetchall():
        resultReturn.append(item)
    con.close()

    # 検索結果を返す
    return {'code': '200', 'testData': resultReturn}

@app.post("/api/searchFilePath")
def searchFilePath():
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS filePath(FILE_PATH_NO int primary key,FILE_PATH varchar(270))")

    # 全ての資料を検索（ret1で検索結果を記録）
    result = cur.execute("SELECT count(*) FROM filePath where FILE_PATH_NO = 1")
    for  item  in  result.fetchall():
        if(item[0] == 0):
            cur.execute("INSERT INTO filePath VALUES (1, '');")
            con.commit()

    result = cur.execute("SELECT * FROM filePath where FILE_PATH_NO = 1")
    for  item  in  result.fetchall():
        resultReturn = item[1]

    # 検索結果を返す
    return {'code': '200', 'path': resultReturn}

@app.post("/api/updateFilePath")
def updateFilePath(path: str = Form(...)):
    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    cur.execute(f"""
        UPDATE filePath
        SET FILE_PATH = '{path}'
            WHERE FILE_PATH_NO = 1
    """)
    con.commit()

    # 検索結果を返す
    return {'code': '200'}

# ファイルをアプロード
@app.post("/api/upload")
def upload(file: UploadFile,clientName: str = Form(...)):

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # ファイル名が既にデータベース存在している資料を検索（その数だけ）
    DuplicateFile = cur.execute(f"""select count(*) from file f
                   where f.FILE_NAME ='{file.filename}' and
                         f.SAVE_NAME LIKE '%{clientName}';
                """)
    for item in DuplicateFile:
        DuplicateFileNum = item[0]
    if(DuplicateFileNum == 1):
        return {'code': '400'}

    # クライアントのファイル名のカウンター用のテーブルを作成
    cur.execute("CREATE TABLE IF NOT EXISTS client(CLIENT_NAME varchar(3) primary key,FILE_NAME_COUNTER varchar(14))")
    # 当ユーザーのファイル名のカウンターを検索（その数だけ）
    clientNameNumOrigin = cur.execute(f"""select count(*) from client
                   where client.CLIENT_NAME ='{clientName}';
                """)
    for item in clientNameNumOrigin:
        clientNameNum = item[0]
    # 今の時間を取得
    current_dateTime = datetime.now()
    current_dateTime_fix = str('{:0>4d}'.format(current_dateTime.year)+'{:0>2d}'.format(current_dateTime.month)+'{:0>2d}'.format(current_dateTime.day))
    # 当ユーザーのファイル名のカウンターが存在しない場合、作る
    if(clientNameNum == 0):
        cur.execute(f"""
            INSERT INTO client VALUES
                ('{clientName}', '{current_dateTime_fix}000000');
        """)
        con.commit()
    # 当ユーザーのファイル名のカウンターを検索
    result = cur.execute(f"SELECT * FROM client WHERE CLIENT_NAME = '{clientName}'")
    for  item  in  result.fetchall():
        clientNum = item[1]
    
    # clientNumが今日の場合、カウンターをプラス1とする
    if(clientNum[:-6] == current_dateTime_fix):
        clientNumTemp = int(clientNum[8:])
        clientNumTemp += 1
        clientNumTempStr = str('{:0>6d}'.format(clientNumTemp))
        clientNumNew = clientNum[:-6]+clientNumTempStr
    else:
        # clientNumが今日ではない場合、カウンターを1に戻す
        clientNumNew = current_dateTime_fix+"000001"
    # 更新したclientNumをデータベースに保存
    cur.execute(f"""
            UPDATE client
            SET FILE_NAME_COUNTER = '{clientNumNew}'
                WHERE CLIENT_NAME = '{clientName}'
    """)
    con.commit()

    # 受け入れたファイルをbytesとして保存、ファイル名も保存
    fileBytes = file.file.read()
    fileName = file.filename
    # 指定されたパスで当ファイルをアーカイブ
    fout = open("./database/"+clientNumNew+clientName+"."+fileName.split(".")[-1], 'wb')
    fout.write(fileBytes)
    fout.close()

    # データベースに必要な資料を用意
    path = Path('./database', clientNumNew+clientName+"."+fileName.split(".")[-1])
    fileSize = path.stat().st_size
    fileUpdateTimeOrigin = time.strftime("%Y-%m-%d",time.localtime(path.stat().st_mtime))
    fileUpdateTime = fileUpdateTimeOrigin.split("-")
    fileUpdateYear = fileUpdateTime[0]
    fileUpdateMonth = fileUpdateTime[1]
    fileUpdateDay = fileUpdateTime[2]
    fileType = fileName.split(".")[-1]

    # テーブルを作る（もしなければ）
    cur.execute("CREATE TABLE IF NOT EXISTS file(FILE_NO integer primary key AUTOINCREMENT,FILE_NAME varchar(270),FILE_SIZE integer,UPDATE_YEAR varchar(4),UPDATE_MONTH varchar(2),UPDATE_DAY varchar(2),FILE_FORMAT varchar(10),FILE_PATH varchar(270),SAVE_NAME varchar(17),DEL_FLG INTEGER DEFAULT 0)")
    
    # 資料をテーブルに追加
    cur.execute(f"""
        INSERT INTO file VALUES
            (NULL,'{fileName}', {fileSize}, '{fileUpdateYear}', '{fileUpdateMonth}', '{fileUpdateDay}', '{fileType}', './database/{clientNumNew}{clientName}.{fileType}', '{clientNumNew}{clientName}', 0);
    """)
    con.commit()

    # 成功メッセージを返す
    return {'code': '200'}

# ファイルをダウンロード
@app.post("/api/download")
def download(userName: str = Form(...), name: str = Form(...)):

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # ファイル名とユーザーナンバーで検索
    result = cur.execute(f"SELECT * FROM file WHERE FILE_NAME = '{name}' and SAVE_NAME LIKE '%{userName}'")
    for  item  in  result.fetchall():
        resultGet = item[7]
    
    filePath = Path(resultGet)
    fileName = name

    # # 当ファイルパスでファイルを読み取り、ファイル名とともに返す
    return FileResponse(filePath, filename=fileName, media_type='application/octet-stream')

# ファイルをダウンロード
@app.post("/api/delete")
def delete(s:Item):
    
    fileNo = str(s).split("'")[-2]

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()
    # 削除（DEL_FLGを1とする）
    cur.execute(f"""
             UPDATE file
                SET DEL_FLG = 1
                    WHERE FILE_NO = {fileNo}
        """)
    con.commit()

    # 成功メッセージを返す
    return {'code': '200'}

@app.post("/api/deletePermanently")
def deletePermanently(s:Item):

    fileNo = str(s).split("'")[-2]

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # 当ファイルのデータベースにある資料を取得、ファイルパスで削除
    result = cur.execute(f"SELECT * FROM file WHERE FILE_NO = '{fileNo}'")
    for  item  in  result.fetchall():
        file = Path(item[7])
        file.unlink()
    
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