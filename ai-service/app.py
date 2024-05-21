from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

app = Flask(__name__)
metrics = PrometheusMetrics(app)
model = None

def load_model():
    global model
    try:
        model = joblib.load('model.pkl')
    except FileNotFoundError:
        data = pd.DataFrame({
            'feature1': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'feature2': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
        })
        model = IsolationForest(contamination=0.1)
        model.fit(data)
        joblib.dump(model, 'model.pkl')

@app.before_request
def before_request():
    global model
    if model is None:
        load_model()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = pd.DataFrame(data)
    prediction = model.predict(df)
    return jsonify(prediction=prediction.tolist())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
