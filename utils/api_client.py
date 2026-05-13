import threading
import requests
from utils.logger import setup_logger

logger = setup_logger("api_client")

class WeatherAPI:
    def __init__(self):
        # Sử dụng Open-Meteo API (không cần key), tọa độ Hà Nội
        self.url = "https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true"

    def fetch_weather_async(self, callback):
        """
        Gọi API thời tiết chạy trên một thread riêng.
        Khi gọi xong sẽ kích hoạt callback với dữ liệu trả về (chạy trên luồng chính).
        """
        def task():
            try:
                logger.info("Bắt đầu tải dữ liệu thời tiết...")
                response = requests.get(self.url, timeout=5)
                response.raise_for_status()
                data = response.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", "--")
                callback(True, f"Hà Nội: {temp}°C", None)
                logger.info("Tải dữ liệu thời tiết thành công.")
            except Exception as e:
                logger.error(f"Lỗi khi tải thời tiết: {e}")
                callback(False, None, str(e))

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()
