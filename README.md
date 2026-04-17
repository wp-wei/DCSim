# Minimal OpenModelica + Buildings data center template (headless)

このリポジトリは、**OpenModelica + Buildings を Python (OMPython) から headless 実行**するための空冷データセンター最小テンプレートです。

最優先は「ロードできる・simulate できる・温度応答が取れる」ことです。物理忠実度は intentionally simplified です。

## Prerequisites

### A) Docker を使う場合（推奨）

- Docker Engine
- （任意）docker compose

### B) ローカルに直接入れる場合

- OpenModelica CLI (`omc`) が PATH 上で利用可能
- Python 3.10+
- `OMPython` インストール済み
- Buildings ライブラリ (`Buildings/package.mo`) の配置

---

## Directory structure

```text
mydc/
  README.md
  requirements.txt
  run.py
  verify.py
  Dockerfile
  docker-compose.yml
  .github/workflows/ci.yml
  MyDC/
    package.mo
    package.order
    Examples/
      package.mo
      package.order
      SingleRoomDX.mo
```

---

## Buildings path handling

`run.py` は以下の順で Buildings を探索します。

1. `BUILDINGS_PATH`（推奨）
2. `BUILDINGS_LIB`（後方互換）
3. `OPENMODELICALIBRARY` に含まれるパス
4. 既定パス: `./Buildings`, `../Buildings`, `~/Buildings`, `/opt/Buildings`, `/usr/share/modelica/Buildings`

明示指定の例:

```bash
export BUILDINGS_PATH=/path/to/Buildings
```

---

## Reproducible run (Docker)

### 1) イメージ作成

```bash
docker build --pull -t mydc-openmodelica .
```

### 2) 必須確認コマンド

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e BUILDINGS_PATH=/opt/Buildings mydc-openmodelica bash -lc "omc --version"
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e BUILDINGS_PATH=/opt/Buildings mydc-openmodelica bash -lc "python3 -c 'import OMPython; print(\"ok\")'"
```

### 3) シミュレーション

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e BUILDINGS_PATH=/opt/Buildings -v "$PWD:/workspace" -w /workspace mydc-openmodelica bash -lc "python3 run.py"
```

### 4) 検証

```bash
docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp -e BUILDINGS_PATH=/opt/Buildings -v "$PWD:/workspace" -w /workspace mydc-openmodelica bash -lc "python3 verify.py"
```

結果ファイルはホスト側 `results/SingleRoomDX_res(.mat)` に生成されます。

### docker compose を使う場合

```bash
docker compose run --rm mydc
```

---

## Local run (without Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Buildings を手動配置したら
export BUILDINGS_PATH=/path/to/Buildings

omc --version
python3 -c "import OMPython; print('ok')"
python3 run.py
python3 verify.py
```

---

## What is modeled (intentionally simplified)

`MyDC.Examples.SingleRoomDX`:

- 1室の lumped 熱容量
- 集約 IT 発熱（Pulse）
- 単純な比例冷却（負の熱流・容量制限付き）
- 代表温度 `TRoom` の時間応答

省略しているもの:

- 詳細ラック airflow
- CRAH/チラー詳細配管
- CFD
- 電力ネットワーク連携

---

## Common failure modes

1. `omc: command not found`
   - OpenModelica が入っていない or PATH 未設定
2. `ModuleNotFoundError: OMPython`
   - `pip install -r requirements.txt` を再実行
3. `Could not find Buildings/package.mo`
   - `BUILDINGS_PATH` を正しいディレクトリへ設定
4. `loadFile(...)` failed
   - `package.mo` / `package.order` と path を確認
5. verify fail（結果ファイルなし）
   - 先に `python3 run.py` のエラーを解消

---

## CI

GitHub Actions (`.github/workflows/ci.yml`) で Docker build 後に以下を実行します。

- `omc --version`
- `python3 -c "import OMPython; print('ok')"`
- `python3 run.py`
- `python3 verify.py`

---

## Next sensible extensions

- 2-zone 化（ホット/コールドアイル）
- 冷却モデルの段階的高度化
- IT 負荷プロファイル外部入力
