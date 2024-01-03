<script>
// import { RouterLink, RouterView} from 'vue-router';
// axiosでapiと接続
import axios from 'axios';

import { defineComponent, reactive } from "vue";
import TableLite from "../components/TableLite.vue";

// Fake Data for 'asc' sortable
const sampleData1 = (offst, limit) => {
  offst = offst + 1;
  let data = [];
  for (let i = offst; i <= limit; i++) {
    data.push({
      id: i,
      name: "TEST" + i,
      email: "test" + i + "@example.com",
    });
  }
  return data;
};

// Fake Data for 'desc' sortable
const sampleData2 = (offst, limit) => {
  let data = [];
  for (let i = limit; i > offst; i--) {
    data.push({
      id: i,
      name: "TEST" + i,
      email: "test" + i + "@example.com",
    });
  }
  return data;
};

export default { 
    // components:{
    //     RouterLink,
    // },
    components: { TableLite },
    
    setup() {
        // Table config
        const table = reactive({
        isLoading: false,
        isReSearch: false,
        rowClasses: (row) => {
            if (row.id == 1) {
            return ["aaa", "is-id-one"];
            }
            return ["bbb", "other"];
        },
        columns: [
            {
            label: "ID",
            field: "id",
            width: "3%",
            sortable: true,
            isKey: true,
            },
            {
            label: "Name",
            field: "name",
            width: "10%",
            sortable: true,
            display: function (row) {
                return (
                '<a href="#" data-id="' +
                row.id +
                '" class="is-rows-el name-btn">' +
                row.name +
                "</a>"
                );
            },
            },
            {
            label: "Email",
            field: "email",
            width: "15%",
            sortable: true,
            },
            {
            label: "",
            field: "quick",
            width: "10%",
            display: function (row) {
                return (
                '<button type="button" data-id="' +
                row.id +
                '" class="is-rows-el quick-btn">Button</button>'
                );
            },
            },
        ],
        rows: [],
        totalRecordCount: 0,
        sortable: {
            order: "id",
            sort: "asc",
        },
        messages: {
            pagingInfo: "Showing {0}-{1} of {2}",
            pageSizeChangeLabel: "Row count:",
            gotoPageLabel: "Go to page:",
            noDataAvailable: "No data",
        },
        });

        /**
         * Search Event
         */
        const doSearch = (offset, limit, order, sort) => {
        table.isLoading = true;
        setTimeout(() => {
            table.isReSearch = offset == undefined ? true : false;
            if (offset >= 10 || limit >= 20) {
            limit = 20;
            }
            if (sort == "asc") {
            table.rows = sampleData1(offset, limit);
            } else {
            table.rows = sampleData2(offset, limit);
            }
            table.totalRecordCount = 20;
            table.sortable.order = order;
            table.sortable.sort = sort;
        }, 600);
        };

        /**
         * Loading finish event
         */
        const tableLoadingFinish = (elements) => {
        table.isLoading = false;
        Array.prototype.forEach.call(elements, function (element) {
            if (element.classList.contains("name-btn")) {
            element.addEventListener("click", function () {
                console.log(this.dataset.id + " name-btn click!!");
            });
            }
            if (element.classList.contains("quick-btn")) {
            element.addEventListener("click", function () {
                console.log(this.dataset.id + " quick-btn click!!");
            });
            }
        });
        };

        /**
         * Row checked event
         */
        const updateCheckedRows = (rowsKey) => {
        console.log(rowsKey);
        };

        // First get data
        doSearch(0, 10, "id", "asc");

        return {
        table,
        doSearch,
        tableLoadingFinish,
        updateCheckedRows,
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
            
            headers: [
                { text: "Name", value: "name" },
                { text: "Height (cm)", value: "height", sortable: true },
                { text: "Weight (kg)", value: "weight", sortable: true },
                { text: "Age", value: "age", sortable: true }
            ],
            items: [
                { "name": "Curry", "height": 178, "weight": 77, "age": 20 },
                { "name": "James", "height": 180, "weight": 75, "age": 21 },
                { "name": "Jordan", "height": 181, "weight": 73, "age": 22 }
            ]
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
      <table-lite
        :has-checkbox="true"
        :is-loading="table.isLoading"
        :is-re-search="table.isReSearch"
        :columns="table.columns"
        :rows="table.rows"
        :rowClasses="table.rowClasses"
        :total="table.totalRecordCount"
        :sortable="table.sortable"
        :messages="table.messages"
        @do-search="doSearch"
        @is-finished="tableLoadingFinish"
        @return-checked-rows="updateCheckedRows"
    ></table-lite>
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
    <EasyDataTable
      :headers="headers"
      :items="items"
    />
</template>
  