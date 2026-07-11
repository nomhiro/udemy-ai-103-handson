# L1-2 サービス／検索・知識・メモリの選定（設計ワークショップ）

> 対応レクチャー：`L1-2-4_実践_service-selection-design.md` ／ 対応スキル：S1.a-2,3,4

このレッスンは**コードを書かない設計回**です。Python の実行はありません。要件シナリオから「使う Foundry サービスの構成」を選び、**理由を言語化する**練習をします。実装（RAG・エージェント・Content Understanding）はセクション2/3/5 で行います。

## やること
1. `scenario-worksheet.md` を開く。
2. 3つのシナリオ（A: 社内QA ／ B: 文書要約 ／ C: マルチモーダル）について、7項目の選定表を埋める。
3. 各シナリオの**構成図**を描く（手描き・draw.io・PowerPoint など何でも可）。
4. Foundry ポータル（https://ai.azure.com ）の **Build → Knowledge / Tools / Agents** で、選んだ部品の在り処を確認する（作成は不要）。

## 必要なもの
- Microsoft Foundry プロジェクト（閲覧できればよい。リソース作成・課金は不要）
- `az login` は任意（ポータルを見るだけなら不要）

## 評価の観点
「正解は1つ」ではありません。**要件（権限・ソース数・クエリの複雑さ・GA縛り・モダリティ）に対して、選定理由を説明できるか**が大事です。

## 参考（座学 L1-2-1〜-3 の決定フロー）
1. グラウンディングの要否 → 2. 検索方式（keyword/vector/semantic/**hybrid**）→ 3. インデックス（integrated vectorization＋出典）→ 4. グラウンディング手段（AI Search 自作／File Search／**AI Search ツール**／**Foundry IQ**）→ 5. メモリ（会話／Memory store）→ 6. ツール（built-in／custom）→ 7. 認証（**Entra キーレス**）
