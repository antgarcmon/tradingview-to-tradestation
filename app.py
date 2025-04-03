from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Clave secreta para evitar ejecuciones no deseadas
SECRET_KEY = 'CXQKEzgv Qlb0vxDS tHHIOQRb QKOtA84e 0rPKQnxw eqzSfUje'

# Configuración
DEFAULT_SYMBOL = 'SPXL'
DEFAULT_AMOUNT_USD = 4000
MIN_TIME_BETWEEN_ORDERS = 60
DELAY_VALIDATION_SECONDS = 60

last_order_time = 0
pending_orders = {}

def ejecutar_orden_con_retraso(order_id, action, symbol, amount_usd):
    global last_order_time
    time.sleep(DELAY_VALIDATION_SECONDS)

    if order_id in pending_orders:
        payload = {
            "symbol": symbol,
            "action": action,
            "amount": amount_usd
        }
        print(f"\n✅ Ejecutando orden tras retardo: {payload}")
        last_order_time = time.time()
        del pending_orders[order_id]

@app.route('/webhook', methods=['POST'])
def webhook():
    global last_order_time
    data = request.json

    if not data or data.get('secret') != SECRET_KEY:
        return jsonify({"error": "Autenticación fallida"}), 403

    action = data.get('action')
    symbol = data.get('symbol', DEFAULT_SYMBOL)
    amount_usd = data.get('amount', DEFAULT_AMOUNT_USD)

    current_time = time.time()
    if current_time - last_order_time < MIN_TIME_BETWEEN_ORDERS:
        return jsonify({"status": "Demasiado pronto"}), 429

    order_id = f"{symbol}_{action}_{int(current_time)}"
    pending_orders[order_id] = {"symbol": symbol, "action": action, "amount": amount_usd}

    threading.Thread(target=ejecutar_orden_con_retraso, args=(order_id, action, symbol, amount_usd)).start()

    return jsonify({"status": f"🕒 Orden programada con retardo de {DELAY_VALIDATION_SECONDS}s"}), 200

if __name__ == '__main__':
    app.run(port=5000)
