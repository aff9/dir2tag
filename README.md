# dir2tag

## 概要

windowsエクスプローラーの階層構造を基に、ファイルタグを自動生成するツール。

## 手順

1. 現行フォルダ構造を走査し、各ファイルのパス（フォルダ階層）を分解してタグ候補を抽出する。
   - 例: Projects/ClientA/Design/logo.png → タグ: Projects, ClientA, Design
2. フォルダ名をスラッグ化／正規化する。
3. 各ファイルのパス情報を基に、フォルダ名をタグ化して自動生成する。
4. 生成したタグ情報とメタデータを元に、TagSpaces へのインポート用 JSON ファイルを出力する。

## 開発計画（段階別）

| ステージ | 主目的 | 主なモジュール/メソッド | 期待する出力 | 備考 |
|-----------|---------|---------------------------|----------------|------|
| Stage1 | 動画ファイル列挙 | `dir2tag/core/paths.py`: `enumerate_video_files(root: Path) -> Iterator[Path]`<br>`main.py`: `main(argv) -> int` | 標準出力に相対パス一覧 | 最小依存 (標準ライブラリのみ) |
| Stage2 | パス→タグ変換 | `dir2tag/core/tag_rules.py`: `normalize_tag(text: str) -> Optional[str]`<br>`dir2tag/core/tag_rules.py`: `path_to_tags(relative_path: Path) -> list[str]` | JSONL 行 `{"relative_path": str, "tags": [...]}` | relative_pathはフルパス, サイドカー生成はまだ行わない |
| Stage3 | 日付タグと重複排除 | `dir2tag/core/date_rules.py`: `extract_date_tags(path: Path) -> list[str]`<br>`dir2tag/core/records.py`: `build_record(...)` | JSONL | `path.stat().st_ctime`（必要なら `st_mtime`）から年月日タグを生成 |
| Stage4 | CLI 拡張・エクスポート | `dir2tag/cli.py`: `build_parser()`, `run(args)`<br>`dir2tag/io/exporters.py`: `write_jsonl`, `write_csv`, `write_sidecar` | `--jsonl`, `--csv`, `--sidecar` オプション対応 | `argparse` とファイル出力処理 |
| Stage5 | テスト導入 | `tests/test_tag_rules.py` など | pytest によるユニットテスト | 必須ケース: タグ正規化 / 日付抽出 |
| Stage6 (任意) | 動画メタ取得 | `dir2tag/core/meta.py`: `probe_video(path: Path) -> VideoMeta` | JSONL, メタフィールド付与 (duration, width など) | ffprobe 依存, Stage2で作成したjsonに追加|
| Stage7 (任意) | 類似判定 | `dir2tag/core/similarity.py`: `compute_signature(path: Path) -> Signature` | ロバストフィンガープリント出力 | ffmpeg signature / TMK+PDQF |

### 進め方メモ

- 仕様変更が出たときは、該当ステージのメソッド契約（引数・戻り値）を最初に更新してから実装を修正する。

## 依存関係（セットアップ）

- 必須バイナリ: [ffmpeg](https://ffmpeg.org/) , [ffprobe](https://ffmpeg.org/ffprobe.html)
- Python 3.12 以上
- Python パッケージ : `ffprobe` 利用には追加不要。`Pillow`, `imagehash` は Stage7 の pHash 系機能で使用予定。

## CLI仕様

| オプション | 必須 | 説明 | 例 | 備考 |
|-------------|------|------|----|------|
| `<root>` | Yes | 走査対象のルートディレクトリ | `python main.py D:\Media` | Stage1 から実装 |
| `--jsonl PATH` | No | JSONL 形式で出力 | `--jsonl out/tags.jsonl` | Stage4 で対応 |
| `--csv PATH` | No | CSV 形式で出力 | `--csv out/tags.csv` | Stage4 |
| `--sidecar` | No | 各ファイルに `<name>.tags.json` を生成 | `--sidecar` | Stage4 |
| `--no-date` | No | 日付タグを抑制 | `--no-date` | Stage4 (Stage3の機能を制御) |
| `--limit N` | No | 処理対象件数の上限 (デバッグ向け) | `--limit 100` | Stage4 |
| `--meta` | Optional | ffprobe で動画メタ取得 | `--meta` | Stage6 |

### サイドカーフォーマット

TagSpaces が推奨するサイドカー形式（`.ts.json`）に合わせる。  
公式仕様: <https://docs.tagspaces.org/help/metadata/>

```json
{
  "tags": [
    {
      "title": "projects",
      "type": "label",
      "color": "#4caf50"
    },
    {
      "title": "clienta",
      "type": "label"
    },
    {
      "title": "design",
      "type": "label"
  "customMeta": {
    "source": "dir2tag",
    "relativePath": "Projects/ClientA/Design/logo.mp4"
    "width": 1920,
    "height": 1080,
    "codec": "h264"
  },
  "description": "",
  "annotations": []
}
```

- `tags`: TagSpaces が解釈するタグ一覧。`title` は必須、`type` は label/flag など。
- `customMeta`: dir2tag 独自メタ（相対パスや生成元）。
- `media`: ffprobe 等で得た動画メタ（Stage6 で付与）。
- `description` / `annotations`: 未使用時は空のまま保存。
Stage4 ではこの構造で `.ts.json` を出力する。

## 将来的に実施

- 類似動画ファイルの検出と統合を行ために、ハッシュ値等のメタデータを計算し、サイドカーに保持する。
- 旧フォルダ構造を削除し、フラット化する。

### 重複ポリシー

| 重複種類 | 検出方法 | 削除ポリシー |
|-----------|------------|----------------|
| 完全重複 | ファイルハッシュ (SHA-256 等) が一致 | 最もビットレートが高い版を残し、他は削除 |
| 再エンコード重複 | ロバスト動画フィンガープリント (ffmpeg signature / TMK+PDQF) の距離が閾値以下 | 解像度が高いものを残し、同解像度なら VMAF スコアが高いものを残す |
| 部分重複 | タイムライン類似度や手動レビュー (範囲一致率がしきい値超え) | ユーザーに判断を委ねる |
