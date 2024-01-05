<script>
// import { RouterLink, RouterView} from 'vue-router';
// axiosでapiと接続
import axios from 'axios';

import { ref } from 'vue';

const ClickRowArgument = {
  isSelected: false,
  indexInCurrentPage: 0,
};

const headers = [
  { text: "PLAYER", value: "player" },
  { text: "TEAM", value: "team"},
  { text: "NUMBER", value: "number"},
  { text: "POSITION", value: "position"},
  { text: "HEIGHT", value: "indicator.height"},
  { text: "WEIGHT", value: "indicator.weight", sortable: true},
  { text: "LAST ATTENDED", value: "lastAttended"},
  { text: "COUNTRY", value: "country"},
  { text: "Operation", value: "operation"},
];

const items = [
    { "id": 1, "player": "Stephen Curry", "page": "https://www.nba.com/player/201939/stephen-curry", "avator": "https://bafkreih3oswhrhrvxwhebuqqnlqtklnth5pbc2q3iv6446icpltt6tymvy.ipfs.dweb.link/?filename=Stephen.png", "teamName": "GSW", "teamUrl": "https://www.nba.com/team/1610612744/warriors", "number": 30, "position": 'G', indicator: {"height": '6-2', "weight": 185}, "lastAttended": "Davidson", "country": "USA"},
    { "id": 2, "player": "Lebron James",  "page": "https://www.nba.com/player/2544/lebron-james", "avator": "https://bafkreigphmpdonfxpcb7lwrzv754t2xp2cw3segdpsj44rpurzwnuowhsq.ipfs.dweb.link/?filename=lebron.png", "teamName": "LAL", "teamUrl": "https://www.nba.com/team/1610612747/lakers", "number": 6, "position": 'F', indicator: {"height": '6-9', "weight": 250}, "lastAttended": "St. Vincent-St. Mary HS (OH)", "country": "USA"},
    { "id": 3, "player": "Kevin Durant", "page": "https://www.nba.com/player/201142/kevin-durant", "avator": "https://bafkreihvjvturzol7kfdafrnpxvilj2rti5bwyee7wbvtxogrx34uzjfz4.ipfs.dweb.link/?filename=Kevin.png", "teamName": "BKN", "teamUrl": "https://www.nba.com/team/1610612751/nets", "number": 7, "position": 'F', indicator: {"height": '6-10', "weight": 240}, "lastAttended": "Texas-Austin", "country": "USA"},
    { "id": 4, "player": "Giannis Antetokounmpo", "page": "https://www.nba.com/player/203507/giannis-antetokounmpo", "avator": "https://bafkreie26rcr5ppdpqrclr3kpk7p7hqyypjo3o2g43yk35ly4e5dmwxigm.ipfs.dweb.link/?filename=Giannis.png", "teamName": "MIL", "teamUrl": "https://www.nba.com/team/1610612749/bucks", "number": 34, "position": 'F', indicator: {"height": '6-11', "weight": 242}, "lastAttended": "Filathlitikos", "country": "Greece"},
  ];

export default { 
    // components:{
    //     RouterLink,
    // },
    // components: { TableLite },
    setup() {
        return {
            headers: ref(headers),
            items: ref(items),
        };
    },
    data() {
        return {
            // アプロード用（ファイルを入れる）
            param: new FormData(),
            // アプロード用（Content-Typeをファイルと設定）
            config: {
                headers:{'Content-Type':'multipart/form-data'}
            },
            // データベースの検索結果
            list: null,
            // ダウンロードしたファイルのパス
            pathLocal: "",
            
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
                // データベースにあるファイルの資料を検索
                axios.post('http://localhost:8000/api/serchAll')
                    .then(response=>{
                        // データベースの検索結果を更新
                        this.list = response.data.testData;
                    

                    })

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
        
        // showRow(e){
        //     document.getElementById('row-clicked').innerHTML = JSON.stringify();
        // },
        teamCheck(teamName){
            console.log("teamName: "+teamName)
        }

    },
    mounted() {
        // 最初にデータベースにある資料を検索
        axios.post('http://localhost:8000/api/serchAll')
            .then(response=>{
                // データベースの検索結果を更新
                this.list = response.data.testData;

            })
    },

}

</script>
<template>
    <EasyDataTable :headers="headers" :items="items">
        <!-- <template #item-team="{ teamName, teamUrl }">
            <a :href="teamUrl">{{ teamName }}</a>
        </template> -->
        <template #item-team="{ teamName, teamUrl }">
            <button @click="teamCheck(teamName)">{{ teamName }}</button>
        </template>
        <!-- <template #item-indicator.weight="item">
            {{ item.indicator.weight }} (lbs)
        </template> -->
    </EasyDataTable>

    <!-- row clicked:<br />
    <div id="row-clicked"></div> -->
    <div>
        <h1>アプロード機能</h1>
        <button type="submit" @click="updateSend">アプロード</button>
        <input name="file" type="file" @change="update"/>
        <hr/>
        <br/>
        <h1>ダウンロード機能</h1>
        <table>
            <thead>
                <tr>
                <th colspan="6">データベース</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>ダウンロードリンク</td>
                    <td>ファイル名</td>
                    <td>ファイルサイズ</td>
                    <td>アプロード日付</td>
                    <td>ファイル形式</td>
                    <td>ファイルパス</td>
                </tr>
                <tr v-for="item in list">
                    <td><button @click="download(item[6])">リンク</button></td>
                    <td>{{ item[0] }}</td>
                    <td><p v-text=this.fileSizeUnit(item[1])></p></td>
                    <td>{{ item[2] }}/{{ item[3] }}/{{ item[4] }}</td>
                    <td>{{ item[5] }}</td>
                    <td>{{ item[6] }}</td>
                </tr>
            </tbody>
            </table>
    </div>
</template>
  