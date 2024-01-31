from pathlib import Path
from typing import List
from fastapi import  FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse
from pydantic import BaseModel
from io import BytesIO
from zipfile import ZipFile
from datetime import datetime
from starlette.middleware.cors import CORSMiddleware # 追加

import time
import sqlite3


app = FastAPI()

# CORSを回避するために追加（今回の肝）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

# エラー422の対策
class Item(BaseModel):
    pathStr:str


# データベースにある資料を検索
@app.get("/users")
async def getUsers(_sort: str, _order: str, name_like: str):
    print("getUsers!")
    print("_sort: "+_sort)
    print("_order: "+_order)
    print("name_like: "+name_like)

    if(name_like == "2"):
            return [{"id": "2", "name": "Jack2", "age": 20}]
        
    if(_sort == "id"):
        if(_order == "asc"):
            # 検索結果を返す
            return [{"id": "1", "name": "Jack", "age": 20},{"id": "2", "name": "Jack2", "age": 20}]
        else:
            return [{"id": "2", "name": "Jack2", "age": 20},{"id": "1", "name": "Jack", "age": 20}]
    else:
            return [{"id": "1", "name": "Jack", "age": 20},{"id": "2", "name": "Jack2", "age": 20}]
        
# データベースにある資料を検索
@app.post("/searchAll")
def searchAll():
    # データベースと接続
    sqlConnect = sqlite3.connect("file_manage.db")
    sqlCursor = sqlConnect.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    fileSearchResult = sqlCursor.execute("SELECT * FROM file")
    for  item  in  fileSearchResult.fetchall():
        file_path = Path(item[7])
        # ファイルがファイルパスにない場合、データベースにある資料を削除
        if(file_path.exists() is not True):
            sqlCursor.execute(f"DELETE FROM file WHERE FILE_NO = {item[0]}")
            sqlConnect.commit()

    # 削除してないデータを検索
    fileSearchExistResult = sqlCursor.execute("SELECT * FROM file WHERE DEL_FLG = 0")
    resultReturn = []
    # 検索結果を取り出す
    for  item  in  fileSearchExistResult.fetchall():
        resultReturn.append(item)
    sqlConnect.close()

    # 検索結果を返す
    return {'code': '200', 'resultReturn': resultReturn}

@app.post("/searchAllTrashCan")
def searchAllTrashCan():
    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    fileSearchResult = sqlCursor.execute("SELECT * FROM file")
    for  item  in  fileSearchResult.fetchall():
        file_path = Path(item[7])
        # ファイルがファイルパスにない場合、データベースにある資料を削除
        if(file_path.exists() is not True):
            sqlCursor.execute(f"DELETE FROM file WHERE FILE_NO = {item[0]}")
            sqlConnect.commit()

    fileSearchNoExistResult = sqlCursor.execute("SELECT * FROM file WHERE DEL_FLG = 1")
    resultReturn = []
    # 検索結果を取り出す
    for  item  in  fileSearchNoExistResult.fetchall():
        resultReturn.append(item)
    sqlConnect.close()

    # 検索結果を返す
    return {'code': '200', 'resultReturn': resultReturn}

@app.post("/searchFilePath")
def searchFilePath():
    print("searchFilePath!")
    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    sqlCursor.execute("CREATE TABLE IF NOT EXISTS filePath(FILE_PATH_NO int primary key,FILE_PATH varchar(270))")

    # 全ての資料を検索（ret1で検索結果を記録）
    filePathSearchResult = sqlCursor.execute("SELECT count(*) FROM filePath where FILE_PATH_NO = 1")
    for  item  in  filePathSearchResult.fetchall():
        if(item[0] == 0):
            sqlCursor.execute("INSERT INTO filePath VALUES (1, '');")
            sqlConnect.commit()

    filePathSearchResultNew = sqlCursor.execute("SELECT * FROM filePath where FILE_PATH_NO = 1")
    for  item  in  filePathSearchResultNew.fetchall():
        resultReturn = item[1]

    # 検索結果を返す
    return {'code': '200', 'path': resultReturn}

@app.post("/updateFilePath")
def updateFilePath(path: str = Form(...)):
    print("updateFilePath!")
    print("path: "+path)
    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    folder_path = Path(path)
    if not folder_path.exists():
        print('folder no exist!')
        return {'code': '400'}

    sqlCursor.execute(f"""
        UPDATE filePath
        SET FILE_PATH = '{path}'
            WHERE FILE_PATH_NO = 1
    """)
    sqlConnect.commit()

    # 検索結果を返す
    return {'code': '200'}

# ファイルをアプロード
@app.post("/upload")
# def upload(files: List[UploadFile],clientName: str = Form(...)):
def upload(files: List[UploadFile] = File(...),clientName: str = Form(...)):
# def upload(files: UploadFile,clientName: str = Form(...)):

    print("upload!")

    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    for file in files:
        # print("file!")
        # print("file.filename: "+file.filename)

        # ファイル名が既にデータベース存在している資料を検索（その数だけ）
        DuplicateFile = sqlCursor.execute(f"""select count(*) from file f
                    where f.FILE_NAME ='{file.filename}' and
                            f.SAVE_NAME LIKE '%{clientName}';
                    """)
        for item in DuplicateFile:
            DuplicateFileNum = item[0]
        if(DuplicateFileNum == 1):
            return {'code': '400'}

        # クライアントのファイル名のカウンター用のテーブルを作成
        sqlCursor.execute("CREATE TABLE IF NOT EXISTS client(CLIENT_NAME varchar(3) primary key,FILE_NAME_COUNTER varchar(14))")
        # 当ユーザーのファイル名のカウンターを検索（その数だけ）
        clientNameNumOrigin = sqlCursor.execute(f"""select count(*) from client
                    where client.CLIENT_NAME ='{clientName}';
                    """)
        for item in clientNameNumOrigin:
            clientNameNum = item[0]
        # 今の時間を取得
        current_dateTime = datetime.now()
        current_dateTime_fix = str('{:0>4d}'.format(current_dateTime.year)+'{:0>2d}'.format(current_dateTime.month)+'{:0>2d}'.format(current_dateTime.day))
        # 当ユーザーのファイル名のカウンターが存在しない場合、作る
        if(clientNameNum == 0):
            sqlCursor.execute(f"""
                INSERT INTO client VALUES
                    ('{clientName}', '{current_dateTime_fix}000000');
            """)
            sqlConnect.commit()
        # 当ユーザーのファイル名のカウンターを検索
        clientSearchResult = sqlCursor.execute(f"SELECT * FROM client WHERE CLIENT_NAME = '{clientName}'")
        for  item  in  clientSearchResult.fetchall():
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
        sqlCursor.execute(f"""
                UPDATE client
                SET FILE_NAME_COUNTER = '{clientNumNew}'
                    WHERE CLIENT_NAME = '{clientName}'
        """)
        sqlConnect.commit()

        # 受け入れたファイルをbytesとして保存、ファイル名も保存
        fileBytes = file.file.read()
        fileName = file.filename
        # 指定されたパスで当ファイルをアーカイブ
        filePathSearchResult = sqlCursor.execute("SELECT * FROM filePath where FILE_PATH_NO = 1")
        for  item  in  filePathSearchResult.fetchall():
            pathSearch = item[1]
        fout = open(pathSearch+"/"+clientNumNew+clientName+"."+fileName.split(".")[-1], 'wb')
        fout.write(fileBytes)
        fout.close()

        # データベースに必要な資料を用意
        path = Path(pathSearch+"/"+clientNumNew+clientName+"."+fileName.split(".")[-1])
        fileSize = path.stat().st_size
        fileUpdateTimeOrigin = time.strftime("%Y-%m-%d",time.localtime(path.stat().st_mtime))
        fileUpdateTime = fileUpdateTimeOrigin.split("-")
        fileUpdateYear = fileUpdateTime[0]
        fileUpdateMonth = fileUpdateTime[1]
        fileUpdateDay = fileUpdateTime[2]
        fileType = fileName.split(".")[-1]

        # テーブルを作る（もしなければ）
        sqlCursor.execute("CREATE TABLE IF NOT EXISTS file(FILE_NO integer primary key AUTOINCREMENT,FILE_NAME varchar(270),FILE_SIZE integer,UPDATE_YEAR varchar(4),UPDATE_MONTH varchar(2),UPDATE_DAY varchar(2),FILE_FORMAT varchar(10),FILE_PATH varchar(270),SAVE_NAME varchar(17),DEL_FLG INTEGER DEFAULT 0)")
        
        # 資料をテーブルに追加
        sqlCursor.execute(f"""
            INSERT INTO file VALUES
                (NULL,'{fileName}', {fileSize}, '{fileUpdateYear}', '{fileUpdateMonth}', '{fileUpdateDay}', '{fileType}', '{pathSearch}\{clientNumNew}{clientName}.{fileType}', '{clientNumNew}{clientName}', 0);
        """)
        sqlConnect.commit()

    # 成功メッセージを返す
    return {'code': '200'}

# ファイルをダウンロード
@app.post("/download")
def download(userName: str = Form(...), name: str = Form(...)):

    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    # ファイル名とユーザーナンバーで検索
    fileSearchResult = sqlCursor.execute(f"SELECT * FROM file WHERE FILE_NAME = '{name}' and SAVE_NAME LIKE '%{userName}'")
    for  item  in  fileSearchResult.fetchall():
        resultGet = item[7]
    
    filePath = Path(resultGet)
    fileName = name

    # # 当ファイルパスでファイルを読み取り、ファイル名とともに返す
    return FileResponse(filePath, filename=fileName, media_type='application/octet-stream')

# ファイルをダウンロード
@app.post("/multipleDownload")
def multipleDownload(userNameList: List[str] = Form(...), nameList: List[str] = Form(...)):

    # ファイルパスとファイル名を保存用
    files = []
    # 各ファイルのファイルパスとファイル名を保存
    for item in nameList:
        userName = userNameList[0]
        name = item

        # データベースと接続
        sqlConnect= sqlite3.connect("file_manage.db")
        sqlCursor= sqlConnect.cursor()

        # ファイル名とユーザーナンバーで検索
        fileSearchResult = sqlCursor.execute(f"SELECT * FROM file WHERE FILE_NAME = '{name}' and SAVE_NAME LIKE '%{userName}'")
        for  item  in  fileSearchResult.fetchall():
            resultGet = item[7]
        # ファイルパスとファイル名を保存
        filePath = Path(resultGet)
        fileName = name
        files.append((filePath, fileName))

    # 各ファイルをまとめて、Bytesとしてzipに入れる
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zip_archive:
        for file_path, file_name in files:
            zip_archive.write(file_path, arcname=file_name)

    # BytesIOを初期化
    zip_buffer.seek(0)

    # StreamingResponseで生成したzipを返す
    return StreamingResponse(zip_buffer, media_type="application/zip", headers={"Content-Disposition": "attachment; filename=download.zip"})

# ファイルをダウンロード
@app.post("/delete")
def delete(pathStr:Item):
    print("delete!")
    print(pathStr)
    
    fileNo = str(pathStr).split("'")[-2]
    print("fileNo: "+fileNo)

    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()
    print("01")
    # 削除（DEL_FLGを1とする）
    sqlCursor.execute(f"""
             UPDATE file
                SET DEL_FLG = 1
                    WHERE FILE_NO = {fileNo}
        """)
    sqlConnect.commit()
    print("02")

    # 成功メッセージを返す
    return {'code': '200'}

# ファイルをダウンロード
@app.post("/cancelDelete")
def cancelDelete(pathStr:Item):
    
    fileNo = str(pathStr).split("'")[-2]

    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()
    # 削除（DEL_FLGを1とする）
    sqlCursor.execute(f"""
             UPDATE file
                SET DEL_FLG = 0
                    WHERE FILE_NO = {fileNo}
        """)
    sqlConnect.commit()

    # 成功メッセージを返す
    return {'code': '200'}

@app.post("/deletePermanently")
def deletePermanently(pathStr:Item):

    fileNo = str(pathStr).split("'")[-2]

    # データベースと接続
    sqlConnect= sqlite3.connect("file_manage.db")
    sqlCursor= sqlConnect.cursor()

    # 当ファイルのデータベースにある資料を取得、ファイルパスで削除
    fileSearchResult = sqlCursor.execute(f"SELECT * FROM file WHERE FILE_NO = '{fileNo}'")
    for  item  in  fileSearchResult.fetchall():
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