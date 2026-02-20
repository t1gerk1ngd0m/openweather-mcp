import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数から設定を取得
API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = os.getenv("OPENWEATHER_BASE_URL", "https://api.openweathermap.org/data/2.5")

# APIキーが設定されているかチェック
if not API_KEY:
    raise ValueError(
        "OPENWEATHER_API_KEY is not set. "
        "Please create a .env file with your API key."
    )

# MCPサーバーの初期化
mcp = FastMCP("openweathermap-service")

print(f"Weather MCP Server initialized")
print(f"Using API base URL: {BASE_URL}")


async def fetch_weather_data(city: str) -> Optional[dict[str, Any]]:
    """
    Open Weather Map APIから天気データを取得する

    Args:
        city: 都市名（英語）

    Returns:
        天気データのdict、エラーの場合はNone
    """
    url = f"{BASE_URL}/weather"
    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",  # 摂氏で温度を取得
        "lang": "ja",  # 日本語で天気の説明を取得
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                print(f"City not found: {city}")
            elif e.response.status_code == 401:
                print("Invalid API key")
            else:
                print(f"HTTP error: {e}")
            return None
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None


def format_weather_response(data: dict[str, Any]) -> str:
    """
    天気データを読みやすい形式にフォーマットする

    Args:
        data: Open Weather Map APIのレスポンス

    Returns:
        フォーマットされた天気情報
    """
    # データから必要な情報を抽出
    city_name = data.get("name", "不明")
    country = data.get("sys", {}).get("country", "")

    # 天気情報
    weather = data.get("weather", [{}])[0]
    description = weather.get("description", "不明")

    # 温度情報（すでに摂氏）
    main = data.get("main", {})
    temp = main.get("temp", 0)
    feels_like = main.get("feels_like", 0)
    temp_min = main.get("temp_min", 0)
    temp_max = main.get("temp_max", 0)
    humidity = main.get("humidity", 0)
    pressure = main.get("pressure", 0)

    # 風情報
    wind = data.get("wind", {})
    wind_speed = wind.get("speed", 0)
    wind_deg = wind.get("deg", 0)

    # 風向きを方角に変換
    wind_direction = convert_degrees_to_direction(wind_deg)

    # フォーマットされた応答を作成
    response = f"""
{city_name}, {country} の現在の天気

天候: {description}
現在の気温: {temp:.1f}°C
体感温度: {feels_like:.1f}°C
最低/最高気温: {temp_min:.1f}°C / {temp_max:.1f}°C
湿度: {humidity}%
気圧: {pressure} hPa
風: {wind_direction} {wind_speed} m/s
"""

    return response.strip()


def convert_degrees_to_direction(degrees: float) -> str:
    """風向き（度）を方角に変換する"""
    directions = [
        "北",
        "北北東",
        "北東",
        "東北東",
        "東",
        "東南東",
        "南東",
        "南南東",
        "南",
        "南南西",
        "南西",
        "西南西",
        "西",
        "西北西",
        "北西",
        "北北西",
    ]
    index = round(degrees / 22.5) % 16
    return directions[index]


@mcp.tool()
async def get_weather(city: str) -> str:
    """
    指定された都市の現在の天気を取得します

    Args:
        city: 都市名（例: Tokyo, London, New York）

    Returns:
        天気情報のフォーマットされた文字列
    """
    # 入力の検証
    if not city or not city.strip():
        return "エラー: 都市名を入力してください。"

    # 天気データを取得
    weather_data = await fetch_weather_data(city.strip())

    if weather_data is None:
        return f"すみません。'{city}' の天気情報を取得できませんでした。都市名を確認してもう一度お試しください。"

    # フォーマットして返す
    return format_weather_response(weather_data)


if __name__ == "__main__":
    # サーバーを起動
    mcp.run(transport="stdio")
