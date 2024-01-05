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
            // データベースの検索結果
            // list: null,
            // ダウンロードしたファイルのパス
            pathLocal: "",
            
            headers: [
                { text: "動作", value: "download" },
                { text: "ファイル名", value: "name"},
                { text: "ファイルサイズ", value: "size"},
                { text: "アプロード日付", value: "date", sortable: true},
                { text: "ファイル形式", value: "format"},
                { text: "ファイルパス", value: "path"},
            ],

            items: [],
            
        }
    },
    methods: {
        // ファイルのアプロード
        updateSend(){
            // ファイルのアプロード
            axios.post('http://localhost:8000/api/upload',this.param,this.config)
            .then(response=>{
                // メッセージを画面に表示
                alert("アプロードしました");
                
                this.searchAll();

            })
        },
        // 選択したファイルを更新（paramに入れる）
        update(e){
            let file = e.target.files[0];
            this.param = new FormData();
            this.param.append('file',file);
        },
        // ファイルをダウンロード
        download(path){
            // ファイルをダウンロード
            axios.post('http://localhost:8000/api/download',
                {s: path},// ファイルパスを送る
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
                        // pathをStringとして保存
                        this.pathLocal = String(path)
                        // ファイル名を取得
                        let fileNameFull = this.pathLocal.split("/")[2]
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
            
            // ファイルをダウンロード
            axios.post('http://localhost:8000/api/delete',
                {s: path},// ファイルパスを送る
                {        
                    responseType: 'blob', // apiからダウンロードしたファイルをBlobとして受け入れる
                }
                )
                .then(response=>{
                    // console.log(response.code)
                  
                    this.searchAll();
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
                        let itemSet = {"id": counter+1, "download": item[6], "name": item[0], "size": this.fileSizeUnit(item[1]), "date": item[2]+"/"+item[3]+"/"+item[4], "format": item[5], "path": item[6]}
                        this.items.push(itemSet);
                        counter++;
                    });
                })
            }

    },
    mounted() {
        this.searchAll();
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
            <template #item-download="{ path }">
                <button @click="download(path)">ダウンロード</button>
                <button @click="deleteFile(path)">削除</button>
            </template>
        </EasyDataTable>
    </div>
</template>
  