# openweather-mcp

Open Weather Map API を利用した MCP サーバーです。都市名を指定して現在の天気情報を取得できます。

## 前提条件

- Python 3.11 以上
- [uv](https://docs.astral.sh/uv/)（パッケージ管理ツール）

## uv のインストール

macOS / Linux:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Homebrew:

```bash
brew install uv
```

インストール後、ターミナルを再起動してから `uv --version` で確認してください。

## 依存関係のインストール

```bash
uv sync
```

## OpenWeatherMap API キーの取得

1. [OpenWeatherMap](https://openweathermap.org/) にアクセスし、アカウントを作成する
2. ログイン後、[API keys](https://home.openweathermap.org/api_keys) ページを開く
3. API キーをコピーする（新規作成も可能）
4. プロジェクトルートに `.env` ファイルを作成し、API キーを設定する

```bash
cp .env.example .env
```

`.env` を編集して `your-api-key-here` を取得した API キーに置き換えてください。

```
OPENWEATHER_API_KEY=your-api-key-here
OPENWEATHER_BASE_URL=https://api.openweathermap.org/data/2.5
```

## Claude Desktop での使い方

Claude Desktop の設定ファイル（`claude_desktop_config.json`）に以下を追加してください。

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "openweathermap": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/openweather-mcp",
        "run",
        "openweather.py"
      ]
    }
  }
}
```

`/path/to/openweather-mcp` は実際のプロジェクトのパスに置き換えてください。

設定後、Claude Desktop を再起動すると `get_weather` ツールが使えるようになります。チャットで「東京の天気を教えて」のように聞くと、現在の天気情報を返します。
