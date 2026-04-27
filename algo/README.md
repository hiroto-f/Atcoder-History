# AtCoder + atcoder-cli (acc) 利用手順メモ

このリポジトリでは **`atcoder-cli (acc)` + `online-judge-tools (oj)`** を使って、ローカルテストおよび提出を行います。
**`oj` は仮想環境の Python に依存するため、必ず仮想環境に入ってから作業してください。**

---

## ✅ 事前準備（最初の1回だけ）

### 1. 仮想環境を作成（未作成の場合）

```bash
python -m venv venv
```

### 2. 仮想環境に入る（★毎回必要）

```bash
# mac / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
```

> 💡 **重要：この手順を忘れると `oj` が正常に動きません。**

### 3. 必要なツールをインストール（最初の1回）

仮想環境に入った状態で：

```bash
pip install online-judge-tools
npm install -g atcoder-cli
```

（すでに入っている場合は不要）

---

## 📁 コンテストのセットアップ

### 新しいコンテストを作成

```bash
acc new abcXXX
```

例：

```bash
acc new abc349
```

これにより、以下のような構成になります：

```
abc349/
  ├── a/
  │   └── main.rs
  ├── b/
  │   └── main.rs
  ├── c/
  │   └── main.rs
  ├── ...
  └── contest.acc.json
```

---

## 🧪 ローカルテストの方法

### 単一ケースのテスト

問題フォルダに移動：

```bash
cd abc349/a
```

テスト実行：

```bash
oj t -c "cargo run --release" -d ./tests
```

もしもojが仮想環境の外のものを参照してしまう場合には、以下を実行。

```bash
export PATH="$VIRTUAL_ENV/bin:$PATH"
```

これにより、AtCoder のサンプル入力で自動テストが走ります。

---

### 特定のテストだけ実行したい場合

```bash
acc test --filter 1
```

---

### カスタム入力でテスト

```bash
echo -e "1 2 3" | cargo run
```

（Rust の場合）

---

## ✍️ コードを書く場所

各問題の `main.rs` を編集します。

例：

```bash
code abc349/a/main.rs
```

---

## 🚀 提出の手順

### 1. 仮想環境に入っていることを確認（★重要）

```bash
which python
```

`.../venv/bin/python` になっていれば OK。

---

### 2. 提出

問題フォルダで：

```bash
acc submit
```

またはコンテストルートから：

```bash
acc submit a
```

---

## ⚠️ よくあるトラブルと対処

### `ModuleNotFoundError: No module named 'distutils'` が出る

仮想環境に入ってから：

```bash
pip install setuptools
```

---

### `oj: command not found`

仮想環境に入ってから：

```bash
pip install online-judge-tools
```

---

## 📝 作業の流れ（まとめ）

毎回の基本フロー：

1. **仮想環境に入る**

   ```bash
   source venv/bin/activate
   ```

2. **コンテストを作成（初回のみ）**

   ```bash
   acc new abcXXX
   ```

3. **問題フォルダへ移動**

   ```bash
   cd abcXXX/a
   ```

4. **コードを書く**
5. **ローカルテスト**

   ```bash
   acc test
   ```

6. **提出**

   ```bash
   acc submit
   ```

---

必要であれば、

- Rust 用テンプレ
- Python 用テンプレ
- Docker 運用版

などに書き換えます。
その場合は教えてください 👍
