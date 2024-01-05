from pathlib import Path
from fastapi import  FastAPI
from fastapi import UploadFile
from starlette.responses import FileResponse
from pydantic import BaseModel

import time
import sqlite3


app = FastAPI()

# データベースにある資料を検索
@app.post("/api/serchAll")
def searchAll():

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()

    # 全ての資料を検索（ret1で検索結果を記録）
    result = cur.execute("SELECT * FROM file")
    for  item  in  result.fetchall():
        file_path = Path(item[6])
        if(file_path.exists() is not True):
            cur.execute(f"DELETE FROM file WHERE FILE_NAME = '{item[0]}'")
            con.commit()

    result = cur.execute("SELECT * FROM file")
    resultReturn = []
    for  item  in  result.fetchall():
        resultReturn.append(item)
    con.close()

    # 検索結果を返す
    return {'code': '200', 'testData': resultReturn}

# ファイルをアプロード
@app.post("/api/upload")
def upload(file: UploadFile):
    
    # 受け入れたファイルをbytesとして保存、ファイル名も保存
    fileBytes = file.file.read()
    fileName = file.filename
    # 指定されたパスで当ファイルをアーカイブ
    fout = open("./database/"+fileName, 'wb')
    fout.write(fileBytes)
    fout.close()

    # データベースに必要な資料を用意
    path = Path('./database', fileName)
    fileSize = path.stat().st_size
    # fileUpdateTime = time.localtime(path.stat().st_mtime)
    fileUpdateTimeOrigin = time.strftime("%Y-%m-%d",time.localtime(path.stat().st_mtime))
    fileUpdateTime = fileUpdateTimeOrigin.split("-")
    fileUpdateYear = fileUpdateTime[0]
    fileUpdateMonth = fileUpdateTime[1]
    fileUpdateDay = fileUpdateTime[2]
    fileType = fileName.split(".")[-1]

    # データベースと接続
    con = sqlite3.connect("file_manage.db")
    cur = con.cursor()
    # cur.execute("DROP TABLE file")
    
    # テーブルを作る（もしなければ）
    cur.execute("CREATE TABLE IF NOT EXISTS file(FILE_NAME varchar(270) primary key,FILE_SIZE integer,UPDATE_YEAR varchar(4),UPDATE_MONTH varchar(2),UPDATE_DAY varchar(2),FILE_FORMAT varchar(10),FILE_PATH varchar(270))")
    
    try: 
        # 資料をテーブルに追加
        cur.execute(f"""
            INSERT INTO file VALUES
                ('{fileName}', {fileSize}, '{fileUpdateYear}', '{fileUpdateMonth}', '{fileUpdateDay}', '{fileType}', './database/{fileName}')
        """)
        con.commit()
    except:
        # テーブル中の資料を更新（もし当ファイル名が既に存在している）
        cur.execute(f"""
             UPDATE file
                SET FILE_NAME = '{fileName}',
                    FILE_SIZE = {fileSize},
                    UPDATE_YEAR = '{fileUpdateYear}',
                    UPDATE_MONTH = '{fileUpdateMonth}',
                    UPDATE_DAY = '{fileUpdateDay}',
                    FILE_FORMAT = '{fileType}',
                    FILE_PATH = './database/{fileName}'
                    WHERE FILE_NAME = '{fileName}'
        """)
        con.commit()

    # 成功メッセージを返す
    return {'code': '200'}

# エラー422の対策
class Item(BaseModel):
    s:str

# ファイルをダウンロード
@app.post("/api/download")
def download(s:Item):
    
    # ファイルパスとファイル名を取得
    filePath = Path(str(s).split("'")[-2])
    fileName = str(s).split("'")[-2].split(".")[0]

    # 当ファイルパスでファイルを読み取り、ファイル名とともに返す
    return FileResponse(filePath, filename=fileName, media_type='application/octet-stream')

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