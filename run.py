import os
from app import create_app
from app.extensions import db

app = create_app(os.getenv('FLASK_ENV') or 'default')

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Create admin user if doesn't exist
        from app.models import User
        admin_email = app.config.get('ADMIN_EMAILS', ['admin@devfolio.com'])[0]
        if not User.query.filter_by(email=admin_email).first():
            admin = User(
                username='admin',
                email=admin_email,
                password='admin123',  # Change this in production!
                full_name='System Administrator',
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully!')
    
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)