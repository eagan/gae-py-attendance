# gae-py-attendance
[Google App Engine](https://cloud.google.com/appengine/) 上で動作する Web 出欠登録システムです。
同窓会の出欠を確認するために作りました。
使用言語は Python 3 で、データは Datastore に格納します。
とりあえず動かすことを優先して作ってしまいましたが、できるだけ汎用的な設計に変更していく予定です。

「郵便番号から住所を自動入力」には
[zipcloud 郵便番号検索API](http://zipcloud.ibsnet.co.jp/doc/api)
を使っています。
また、JavaScript フレームワーク
[jQuery](https://jquery.com/) および
[jQuery UI](https://jqueryui.com/) を使っています。
各プロジェクト関係者に感謝します。

## Google App Engine を使った理由
開発の発端となった会合には「無料で使えるサーバ」という要件がありました。
1 年間の試用期間は無料といったサービスはほかにもありますが、
Google App Engine（というより Google Cloud Platform）には「Always Free」と呼ばれる、
期間を限定しない無料枠があります。詳細は
[Google Cloud の無料枠](https://cloud.google.com/free/docs/gcp-free-tier)
を参照してください。

ただし Google App Engine はいろいろと特殊なので、
設計時点からプラットフォームを意識しておかないと、簡単には動かないと思います。
