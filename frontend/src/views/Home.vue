<script>
// import { RouterLink, RouterView} from 'vue-router';
// axiosでapiと接続
import axios from 'axios';

export default {
    data() {
        return {
            // アプロード用（ファイルを入れる）
            param: new FormData(),
            // アプロード用（Content-Typeをファイルと設定）
            config: {
                headers:{'Content-Type':'multipart/form-data'}
            },

            paramDownload: new FormData(),
            // config: {
            //     headers:{'Content-Type':'multipart/form-data'}
            // },
            // データベースの検索結果
            // list: null,
            // ダウンロードしたファイルのパス
            pathLocal: "",
            
            headers: [
                { text: "動作", value: "do" },
                { text: "ファイル名", value: "name"},
                { text: "ファイルサイズ", value: "size"},
                { text: "アプロード日付", value: "date", sortable: true},
                { text: "ファイル形式", value: "format"},
                { text: "ファイルパス", value: "path"},
            ],

            items: [],
            itemsTrashCan: [],
            clientName: "A01",
            
        }
    },
    methods: {
        // ファイルのアプロード
        updateSend(){
            this.param.append('clientName','A01');
            // console.log('clientName: '+this.param.get('clientName'));
            if(this.param.get('file') === null){
                alert("ファイルを選択してください")
                return;
            }
            if(this.param.get('file').size >= 100000000){ //100MB
                alert("100MB以内のファイルを選択してください")
                return;
            }
            // ファイルのアプロード
            axios.post('http://localhost:8000/api/upload',this.param,this.config)
            .then(response=>{
                if(response.data.code === "200"){
                    // メッセージを画面に表示
                    alert("アプロードしました");
                    
                    this.searchAll();
                }
                else{
                    alert("ファイル名が被った");

                }

            })
        },
        // 選択したファイルを更新（paramに入れる）
        update(e){
            let file = e.target.files[0];
            this.param = new FormData();
            this.param.append('file',file);
        },
        // ファイルをダウンロード
        download(saveName, name){
            
            this.paramDownload.append('userName',saveName.substring(14));
            this.paramDownload.append('name',name);
            // ファイルをダウンロード
            // axios.post('http://localhost:8000/api/download',this.paramDownload,this.config,
            axios.post('http://localhost:8000/api/download',this.paramDownload,
                {
                    responseType: 'blob', // apiからダウンロードしたファイルをBlobとして受け入れる
                }
                )
                    .then(response=>{
                        //　ファイルをURLとして生成
                        const url = window.URL.createObjectURL(new Blob([response.data],
                            { type: 'application/octet-stream' }));//　octet-streamはファイル形式を指定しない場合に使う
                        // ダウンロード用のリンクを生成
                        const link = document.createElement('a');
                        // リンク先は当ファイルと設定
                        link.href = url;
                        // // pathをStringとして保存
                        // this.pathLocal = String(path)
                        // // ファイル名を取得
                        // let fileNameFull = this.pathLocal.split("/")[2]
                        let fileNameFull = name
                        // 'download'は当リンクの内容をダウンロード
                        // fileNameFullはファイル名を設定
                        link.setAttribute('download', fileNameFull);
                        // 当リンクを画面に追加
                        document.body.appendChild(link);
                        // 当リンクをクリックし、ダウンロードを行う
                        link.click();
                    })

        },
        // ファイルサイズの単位を変換する
        fileSizeUnit(size){
            if(size <= 1000)
                return Math.round(size)+"B"
            else if(size <= 1000000)
                return Math.round(size/1000)+"KB"
            else if(size <= 1000000000)
                return Math.round(size/1000000)+"MB"
            else
                return Math.round(size/1000000000)+"TB"
        },
        deleteFile(path){
            // console.log("path? is "+path.type())
            // console.log(path)
            let pathStr = path.toString()
            // console.log(pathStr)
            
            // ファイルをダウンロード
            axios.post('http://localhost:8000/api/delete',
                {s: pathStr},// ファイルパスを送る
                {        
                    responseType: 'blob', // apiからダウンロードしたファイルをBlobとして受け入れる
                }
                )
                .then(response=>{
                    // console.log(response.data.code)
                  
                    this.searchAll();
                    this.searchAllTrashCan();
                })
        },
        deleteFilePermanently(path){
            let pathStr = path.toString()
            
            // ファイルをダウンロード
            axios.post('http://localhost:8000/api/deletePermanently',
                {s: pathStr},// ファイルパスを送る
                // {        
                //     responseType: 'blob', // apiからダウンロードしたファイルをBlobとして受け入れる
                // }
                )
                .then(response=>{
                    this.searchAll();
                    this.searchAllTrashCan();
                })
        },
        searchAll(){
            // 最初にデータベースにある資料を検索
            axios.post('http://localhost:8000/api/serchAll')
                .then(response=>{
                    // データベースの検索結果を更新
                    // this.list = response.data.testData;

                    this.items = []
                    let counter = 0;
                    response.data.testData.forEach(item => {
                        let itemSet = {"id": counter+1, "fileNo": item[0], "saveName": item[8], "name": item[1], "size": this.fileSizeUnit(item[2]), "date": item[3]+"/"+item[4]+"/"+item[5], "format": item[6], "path": item[7]}
                        this.items.push(itemSet);
                        counter++;
                    });
                })
        },
        searchAllTrashCan(){
            // 最初にデータベースにある資料を検索
            axios.post('http://localhost:8000/api/serchAllTrashCan')
            // axios.post('http://localhost:8000/api/serchAll')
                .then(response=>{
                    // データベースの検索結果を更新
                    // this.list = response.data.testData;

                    this.itemsTrashCan = []
                    let counter = 0;
                    response.data.testData.forEach(item => {
                        let itemSet = {"id": counter+1, "fileNo": item[0], "saveName": item[8], "name": item[1], "size": this.fileSizeUnit(item[2]), "date": item[3]+"/"+item[4]+"/"+item[5], "format": item[6], "path": item[7]}
                        this.itemsTrashCan.push(itemSet);
                        counter++;
                    });
                })
        }

    },
    mounted() {
        this.searchAll();
        this.searchAllTrashCan();
    },

}

</script>
<template>
    <div>
        <h1>アプロード機能</h1>
        <button type="submit" @click="updateSend">アプロード</button>
        <input name="file" type="file" @change="update"/>
        <hr/>
        <br/>
        <h1>ダウンロード機能</h1>
        <EasyDataTable :headers="headers" :items="items">
            <template #item-do="{ saveName,name,fileNo }">
                <button @click="download(saveName, name)">ダウンロード</button>
                <button @click="deleteFile(fileNo)">削除</button>
            </template>
        </EasyDataTable>
        <hr/>
        <br/>
        <h1>ゴミ箱</h1>
        <EasyDataTable :headers="headers" :items="itemsTrashCan">
            <template #item-do="{ fileNo }">
                <button @click="deleteFilePermanently(fileNo)">完全削除</button>
            </template>
        </EasyDataTable>

    </div>
</template>
  