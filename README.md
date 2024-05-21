# AI Monitoreo y Detección de Anomalías

## Descripción General

Este proyecto demuestra cómo configurar un sistema de monitoreo y detección de anomalías utilizando NGINX, Prometheus, Grafana y un servicio de IA para predicciones. El sistema se despliega en Kubernetes y utiliza una combinación de herramientas para visualizar y predecir anomalías en el tráfico web.

## Componentes

1. **NGINX**: Servidor web para generar datos de tráfico.
2. **Prometheus**: Recopila métricas de NGINX.
3. **Grafana**: Visualiza métricas y predicciones.
4. **Servicio de IA**: Utiliza aprendizaje automático para predecir anomalías en los datos.

## Arquitectura

![Diagrama de Arquitectura](./ruta/a/diagrama-de-arquitectura.png)

## Prerrequisitos

- Clúster de Kubernetes
- kubectl configurado
- Docker
- Minikube
- VS Code

## Configuración

### 1. Desplegar NGINX

Crear un despliegue para NGINX:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
### Desplegar el exportador de NGINX para recopilar métricas:

yaml
Copy code
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-exporter
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-exporter
  template:
    metadata:
      labels:
        app: nginx-exporter
    spec:
      containers:
      - name: nginx-exporter
        image: nginx/nginx-prometheus-exporter:latest
        args:
          - -nginx.scrape_uri=http://nginx:80/stub_status
        ports:
        - containerPort: 9113
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-exporter
spec:
  selector:
    app: nginx-exporter
  ports:
  - protocol: TCP
    port: 9113
    targetPort: 9113
### 2. Desplegar Prometheus
### Crear un ConfigMap para la configuración de Prometheus:

yaml
Copy code
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
      - job_name: 'nginx'
        static_configs:
          - targets: ['nginx-exporter:9113']
Desplegar Prometheus utilizando el ConfigMap:

yaml
Copy code
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
spec:
  type: NodePort
  selector:
    app: prometheus
  ports:
  - protocol: TCP
    port: 9090
    targetPort: 9090
    nodePort: 30900
### 3. Desplegar Grafana
#### Crear un despliegue para Grafana:

yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        volumeMounts:
        - name: grafana-storage
          mountPath: /var/lib/grafana
      volumes:
      - name: grafana-storage
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: grafana
spec:
  type: LoadBalancer
  selector:
    app: grafana
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
    nodePort: 32000
### 4. Desplegar el Servicio de IA
#### Crear un Dockerfile para el servicio de IA:

dockerfile
FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "app.py"]
### Crear un despliegue para el servicio de IA:

yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-service
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ai-service
  template:
    metadata:
      labels:
        app: ai-service
    spec:
      containers:
      - name: ai-service
        image: your-dockerhub-username/ai-service:latest
        ports:
        - containerPort: 5000
---
apiVersion: v1
kind: Service
metadata:
  name: ai-service
spec:
  selector:
    app: ai-service
  ports:
  - protocol: TCP
    port: 5000
    targetPort: 5000
### 5. Configurar Grafana
####Agregar el servicio de IA como una fuente de datos en Grafana y crear un panel para visualizar las predicciones.

### Ir a Grafana -> Configuration -> Data Sources.
### Agregar una nueva fuente de datos con los siguientes detalles:
Tipo: JSON API
URL: http://ai-service:5000
Acceso: Server (default)
Crear un nuevo panel y configurar la consulta para usar la fuente de datos JSON API con la solicitud POST adecuada a /predict.
6. Configurar Alertas
Configurar alertas en Grafana para notificar cuando se detecten anomalías:

Crear una regla de alerta en el panel con los datos de predicción.
Establecer la condición de alerta para que se active cuando la predicción contenga -1.
Configurar los canales de notificación (correo electrónico, Slack, etc.) para las alertas.
Conclusión
Esta configuración demuestra cómo monitorear el tráfico web utilizando Prometheus y Grafana, y mejorar la observabilidad con detección de anomalías basada en IA. El servicio de IA predice anomalías basándose en los datos de entrada y los resultados se visualizan en Grafana, ayudando a identificar y responder rápidamente a patrones inusuales en el tráfico web.

Para más detalles, consulta el repositorio y sigue los pasos para replicar la configuración en tu entorno.
