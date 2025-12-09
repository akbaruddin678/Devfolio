from flask import render_template, request
from app.main import main_bp
from app.models import User, Project, BlogPost

@main_bp.route('/')
@main_bp.route('/index')
def index():
    featured_projects = Project.query.filter_by(is_featured=True, is_public=True)\
        .order_by(Project.created_at.desc()).limit(6).all()
    recent_posts = BlogPost.query.filter_by(is_published=True)\
        .order_by(BlogPost.created_at.desc()).limit(3).all()
    featured_users = User.query.filter(User.projects.any())\
        .order_by(User.created_at.desc()).limit(4).all()
    
    return render_template('index.html',
                         featured_projects=featured_projects,
                         recent_posts=recent_posts,
                         featured_users=featured_users)

@main_bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    projects = Project.query.filter_by(is_public=True)\
        .order_by(Project.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    # Remove joinedload - dynamic relationships don't support it
    users = User.query.filter(User.projects.any())\
        .order_by(User.created_at.desc()).limit(20).all()
    
    return render_template('explore.html', 
                         projects=projects,
                         users=users)

@main_bp.route('/features')
def features():
    return render_template('features.html')

@main_bp.route('/about')
def about():
    return render_template('about.html')