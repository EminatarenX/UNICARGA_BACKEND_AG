from flask import Flask, jsonify
from flask_cors import CORS
from api.routes import register_api

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Registrar rutas de la API
register_api(app)

# Ruta principal para verificar que la API está funcionando
@app.route('/')
def index():
    return jsonify({
        'status': 'success',
        'message': 'API UNICARGA funcionando correctamente',
        'version': '1.0.0'
    })

# Manejador de errores para rutas no encontradas
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'status': 'error',
        'message': 'Recurso no encontrado'
    }), 404

# Manejador de errores para excepciones internas
@app.errorhandler(500)
def server_error(e):
    return jsonify({
        'status': 'error',
        'message': 'Error interno del servidor',
        'error': str(e)
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)