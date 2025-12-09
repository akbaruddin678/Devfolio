from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.models import User, Project, BlogPost, ViewLog
from app.extensions import db

@admin_bp.before_request
@login_required
def restrict_admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/')
def dashboard():
    # Get statistics
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_posts = BlogPost.query.count()
    total_views = ViewLog.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Get recent projects
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    
    # Get system stats
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    
    new_users_week = User.query.filter(
        db.func.date(User.created_at) >= week_ago
    ).count()
    
    new_projects_week = Project.query.filter(
        db.func.date(Project.created_at) >= week_ago
    ).count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_projects=total_projects,
                         total_posts=total_posts,
                         total_views=total_views,
                         recent_users=recent_users,
                         recent_projects=recent_projects,
                         new_users_week=new_users_week,
                         new_projects_week=new_projects_week)

@admin_bp.route('/users')
def users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:user_id>/toggle')
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "activated" if user.is_active else "deactivated"
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/projects')
def projects():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    projects = Project.query.order_by(Project.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/projects.html', projects=projects)

@admin_bp.route('/projects/<int:project_id>/toggle')
def toggle_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.is_public = not project.is_public
    db.session.commit()
    
    status = "published" if project.is_public else "unpublished"
    flash(f'Project "{project.title}" has been {status}.', 'success')
    return redirect(url_for('admin.projects'))

@admin_bp.route('/analytics')
def analytics():
    from datetime import datetime, timedelta
    
    # Get date range
    days = int(request.args.get('days', 30))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get daily user registrations
    daily_registrations = db.session.query(
        db.func.date(User.created_at).label('date'),
        db.func.count(User.id).label('count')
    ).filter(
        User.created_at >= start_date
    ).group_by(
        db.func.date(User.created_at)
    ).order_by('date').all()
    
    # Get daily project creations
    daily_projects = db.session.query(
        db.func.date(Project.created_at).label('date'),
        db.func.count(Project.id).label('count')
    ).filter(
        Project.created_at >= start_date
    ).group_by(
        db.func.date(Project.created_at)
    ).order_by('date').all()
    
    # Get top viewed projects
    top_projects = Project.query.order_by(Project.views.desc()).limit(10).all()
    
    # Get top active users
    from sqlalchemy import func
    top_users = db.session.query(
        User,
        func.count(Project.id).label('project_count')
    ).join(Project).group_by(User.id)\
     .order_by(func.count(Project.id).desc())\
     .limit(10).all()
    
    return render_template('admin/analytics.html',
                         days=days,
                         daily_registrations=daily_registrations,
                         daily_projects=daily_projects,
                         top_projects=top_projects,
                         top_users=top_users)