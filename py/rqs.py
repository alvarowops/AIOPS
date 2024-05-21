import requests
import time

PROMETHEUS_URL = 'http://prometheus-server:9090'
AI_SERVICE_URL = 'http://ai-service:5000/predict'

def get_nginx_metrics():
    response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': 'nginx_http_requests_total'})
    return response.json()['data']['result']

def send_metrics_to_ai(metrics):
    metrics_data = [{'feature1': float(metric['value'][1]), 'feature2': 10.0} for metric in metrics]  # Usar un segundo valor adecuado
    response = requests.post(AI_SERVICE_URL, json=metrics_data)
    return response.json()['prediction']

while True:
    metrics = get_nginx_metrics()
    predictions = send_metrics_to_ai(metrics)
    print(f"Predicciones: {predictions}")
    time.sleep(60)  # Ejecutar cada minuto
