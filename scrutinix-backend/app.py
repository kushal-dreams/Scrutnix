import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from extensions import db, migrate


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    if cors_origins != "*":
        cors_origins = [o.strip() for o in cors_origins.split(",")]

    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    db.init_app(app)
    migrate.init_app(app, db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    from routes.auth import auth_bp
    from routes.search import search_bp
    from routes.report import report_bp
    from routes.analyzer import analyzer_bp
    from routes.profile import profile_bp
    from routes.live_feed import live_feed_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(analyzer_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(live_feed_bp)

    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'Scrutinix backend is running'}

    with app.app_context():
        import models
        db.create_all()
        print('[OK] Database tables created/verified')

    return app


app = create_app()

if __name__ == '__main__':
    port = Config.PORT
    print(f'\n  Scrutinix Backend Running on http://localhost:{port}')
    print('  OTP codes print to this console\n')
    app.run(debug=Config.DEBUG, port=port, threaded=True)
