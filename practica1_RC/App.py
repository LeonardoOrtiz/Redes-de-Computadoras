from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

nombre = "leonardo"
ultimo_valor = 0
nombre_final = ""
estado_proceso = "activo"
SIGUIENTE_URL = "" # URL de Add
NOTIFICACION_URL = "" # URL de Notify

# Ruta para iniciar el proceso como primer nodo
@app.route('/start', methods=['GET'])
def start():
    global nombre, SIGUIENTE_URL

    valor = 0

    try:
        r = requests.post(SIGUIENTE_URL, json={"valor": valor,"name": nombre})
        if r.status_code >= 400:
            return jsonify({"error": "no ha sido posible iniciar el proceso", "problema": r.text}), r.status_code
    except Exception as e:
        return jsonify({"error": "condición inesperada que impide cumplir la solicitud", "problema": str(e)}), 500

    return jsonify({"valor": valor, "name": nombre})


# Ruta que recibe un número en el body (JSON)
@app.route('/add', methods=['GET','POST'])
def sumar_json():
    global nombre, ultimo_valor, SIGUIENTE_URL, NOTIFICACION_URL
    if request.method == 'POST':
        data = request.get_json()
    
        if not data or "valor" not in data or "name" not in data:
            return jsonify({"error": "Debes enviar un JSON con la clave 'valor' y 'name'"}), 400
    
        valor = data["valor"]

        resultado = valor + 1
        ultimo_valor = resultado

        if resultado >= 50:
            try:
                requests.post(NOTIFICACION_URL, json={"nodo_finalizado": nombre})
            except Exception as e:
                return jsonify({"error": "ocurrió un error al notificar", "problema": str(e)}), 500
            return jsonify({"valor": resultado, "name": nombre}), 200
        
        else:
            try:
                requests.post(SIGUIENTE_URL, json={"valor": resultado, "name": nombre})
            except Exception as e:
                return jsonify({"error": "ocurrió un error al reenviar", "problema": str(e)}), 500
            return jsonify({"valor": resultado, "name": nombre}), 200
    
    else: # Para el método GET
        # El nodo obtiene su último valor
        return jsonify({"valor": ultimo_valor, "name": nombre})


#Ruta para notificar que la ejecución del algoritmo finalizó
@app.route('/notify', methods=['GET','POST'])
def notify():
    global nombre, nombre_final, estado_proceso, NOTIFICACION_URL

    if request.method == 'POST':
        data = request.get_json()
        if not data or "nodo_finalizado" not in data:
            return jsonify({"error": "Debes enviar un JSON con la clave 'nodo_finalizado'"}), 400
        
        nombre_final = data["nodo_finalizado"]
        estado_proceso = "finalizado"

        if nombre_final == nombre:
            return jsonify({"estado_proceso": "finalizado", "nodo_finalizado": nombre_final, "notificacion_completa": True})
        else:
            try:
                requests.post(NOTIFICACION_URL, json={"nodo_finalizado": nombre_final})
            except Exception as e:
                return jsonify({"error": "condición inesperada que impide reenviar notificación", "problema": str(e)}), 500
            
            return jsonify({"estado_proceso": "finalizado", "nodo_finalizado": nombre_final, "notificacion_completa": False})

    
    else: 
        return jsonify({"estado_proceso": estado_proceso, "nodo_finalizado": nombre_final})

        


if __name__ == '__main__':
    app.run(debug=True)
    