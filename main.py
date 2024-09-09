from flask import Flask, request
from flask_cors import CORS
from database import create_app
from routes.colaborador import colaborador_bp
from routes.meta import meta_bp
from routes.premiacaoMeta import premiacaoMeta_bp
from routes.premiacaoReconquista import premiacaoReconquista_bp
from routes.orders import orders_bp
from routes.sales import sales_bp
from routes.ticket import ticket_bp
from routes.reconquest import reconquest_bp
from routes.closing import closing_bp




app, db = create_app()

CORS(app, resources={r"/api/*": {"origins": "*"}})

# # Logging middleware
# @app.before_request
# def log_request_info():
#     print(f"Request Method: {request.method}")
#     print(f"Request URL: {request.url}")

# @app.after_request
# def log_response_info(response):
#     print(f"Response Status: {response.status}")
#     print(f"Response Headers: {response.headers}")
#     return response

app.register_blueprint(colaborador_bp, url_prefix='/api')
app.register_blueprint(meta_bp, url_prefix='/api')
app.register_blueprint(premiacaoMeta_bp, url_prefix='/api')
app.register_blueprint(premiacaoReconquista_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api')
app.register_blueprint(sales_bp, url_prefix='/api')
app.register_blueprint(ticket_bp, url_prefix='/api')
app.register_blueprint(reconquest_bp, url_prefix='/api')
app.register_blueprint(closing_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5001)











