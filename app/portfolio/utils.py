import os
import uuid
from PIL import Image
from flask import current_app
import mimetypes

def allowed_file(filename):
    allowed = current_app.config['ALLOWED_EXTENSIONS']
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed

def save_file(file, subfolder):
    if not file or not allowed_file(file.filename):
        return None
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    
    # Create upload path
    upload_folder = current_app.config['UPLOAD_FOLDER']
    upload_path = os.path.join(upload_folder, subfolder, filename)
    
    # Save file
    file.save(upload_path)
    
    # If it's an image, create thumbnail
    if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
        create_thumbnail(upload_path)
    
    return filename

def create_thumbnail(image_path, size=(300, 300)):
    try:
        img = Image.open(image_path)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        
        # Save thumbnail
        dir_name, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        thumbnail_path = os.path.join(dir_name, f"{name}_thumb{ext}")
        img.save(thumbnail_path)
        
        return thumbnail_path
    except Exception as e:
        current_app.logger.error(f"Error creating thumbnail: {e}")
        return None

def delete_file(filename, subfolder):
    if filename and filename != 'default-profile.jpg':
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, subfolder, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Also delete thumbnail if exists
            dir_name, file_name = os.path.split(file_path)
            name, ext = os.path.splitext(file_name)
            thumb_path = os.path.join(dir_name, f"{name}_thumb{ext}")
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
        except Exception as e:
            current_app.logger.error(f"Error deleting file: {e}")

def log_view(entity_type, entity_id, request):
    from app.models import ViewLog, db
    from flask_login import current_user
    
    try:
        view_log = ViewLog(
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string[:500] if request.user_agent else None,
            referrer=request.referrer[:255] if request.referrer else None,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(view_log)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error logging view: {e}")
        db.session.rollback()

def get_view_stats(user_id, entity_type=None, days=30):
    from app.models import ViewLog, db
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    query = ViewLog.query.filter(ViewLog.user_id == user_id)
    
    if entity_type:
        query = query.filter(ViewLog.entity_type == entity_type)
    
    since_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(ViewLog.timestamp >= since_date)
    
    # Get daily counts
    daily_counts = db.session.query(
        func.date(ViewLog.timestamp).label('date'),
        func.count(ViewLog.id).label('count')
    ).filter(
        ViewLog.user_id == user_id,
        ViewLog.timestamp >= since_date
    ).group_by(
        func.date(ViewLog.timestamp)
    ).order_by('date').all()
    
    return {
        'total_views': query.count(),
        'daily_counts': [{'date': str(d[0]), 'count': d[1]} for d in daily_counts]
    }