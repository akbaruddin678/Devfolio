from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import current_user, login_required
from app.portfolio import portfolio_bp
from app.portfolio.forms import ProfileForm, ProjectForm, BlogPostForm, AchievementForm, SkillForm
from app.models import User, Project, BlogPost, Achievement, Skill, ViewLog
from app.extensions import db
from app.portfolio.utils import save_file, delete_file, log_view, get_view_stats
import os
from datetime import datetime
from slugify import slugify

@portfolio_bp.route('/dashboard')
@login_required
def dashboard():
    # Get user stats
    projects_count = current_user.projects.count()
    blog_posts_count = current_user.blog_posts.count()
    achievements_count = current_user.achievements.count()
    skills_count = current_user.skills.count()
    
    # Get recent activity
    recent_projects = current_user.projects.order_by(Project.created_at.desc()).limit(5).all()
    recent_posts = current_user.blog_posts.order_by(BlogPost.created_at.desc()).limit(5).all()
    
    # Get view stats
    view_stats = get_view_stats(current_user.id)
    
    return render_template('portfolio/dashboard.html',
                         projects_count=projects_count,
                         blog_posts_count=blog_posts_count,
                         achievements_count=achievements_count,
                         skills_count=skills_count,
                         recent_projects=recent_projects,
                         recent_posts=recent_posts,
                         view_stats=view_stats)

@portfolio_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.tagline = form.tagline.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        current_user.github = form.github.data
        current_user.linkedin = form.linkedin.data
        current_user.twitter = form.twitter.data
        
        # Handle profile picture upload
        if form.profile_pic.data:
            # Delete old profile picture if exists
            if current_user.profile_pic and current_user.profile_pic != 'default-profile.jpg':
                delete_file(current_user.profile_pic, 'profiles')
            
            # Save new profile picture
            filename = save_file(form.profile_pic.data, 'profiles')
            if filename:
                current_user.profile_pic = filename
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('portfolio.dashboard'))
    
    elif request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.bio.data = current_user.bio
        form.tagline.data = current_user.tagline
        form.location.data = current_user.location
        form.website.data = current_user.website
        form.github.data = current_user.github
        form.linkedin.data = current_user.linkedin
        form.twitter.data = current_user.twitter
    
    return render_template('portfolio/edit_profile.html', form=form)

@portfolio_bp.route('/projects')
@login_required
def projects():
    user_projects = current_user.projects.order_by(Project.created_at.desc()).all()
    return render_template('portfolio/projects.html', projects=user_projects)

@portfolio_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    
    if form.validate_on_submit():
        project = Project(
            user_id=current_user.id,
            title=form.title.data,
            slug=slugify(form.title.data),
            description=form.description.data,
            short_description=form.short_description.data,
            tech_stack=form.tech_stack.data,
            repo_url=form.repo_url.data,
            live_url=form.live_url.data,
            is_public=form.is_public.data,
            is_featured=form.is_featured.data
        )
        
        # Clean HTML in description
        project.clean_description()
        
        # Handle featured image upload
        if form.featured_image.data:
            filename = save_file(form.featured_image.data, 'projects')
            if filename:
                project.featured_image = filename
        
        db.session.add(project)
        db.session.commit()
        
        flash('Your project has been added!', 'success')
        return redirect(url_for('portfolio.projects'))
    
    return render_template('portfolio/add_project.html', form=form)

@portfolio_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check ownership
    if project.user_id != current_user.id:
        abort(403)
    
    form = ProjectForm()
    
    if form.validate_on_submit():
        project.title = form.title.data
        project.slug = slugify(form.title.data)
        project.description = form.description.data
        project.short_description = form.short_description.data
        project.tech_stack = form.tech_stack.data
        project.repo_url = form.repo_url.data
        project.live_url = form.live_url.data
        project.is_public = form.is_public.data
        project.is_featured = form.is_featured.data
        
        # Clean HTML in description
        project.clean_description()
        
        # Handle featured image upload
        if form.featured_image.data:
            # Delete old image if exists
            if project.featured_image:
                delete_file(project.featured_image, 'projects')
            
            # Save new image
            filename = save_file(form.featured_image.data, 'projects')
            if filename:
                project.featured_image = filename
        
        db.session.commit()
        flash('Your project has been updated!', 'success')
        return redirect(url_for('portfolio.projects'))
    
    elif request.method == 'GET':
        form.title.data = project.title
        form.description.data = project.description
        form.short_description.data = project.short_description
        form.tech_stack.data = project.tech_stack
        form.repo_url.data = project.repo_url
        form.live_url.data = project.live_url
        form.is_public.data = project.is_public
        form.is_featured.data = project.is_featured
    
    return render_template('portfolio/add_project.html', form=form, project=project, edit=True)

@portfolio_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Check ownership
    if project.user_id != current_user.id:
        abort(403)
    
    # Delete associated files
    if project.featured_image:
        delete_file(project.featured_image, 'projects')
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Your project has been deleted!', 'success')
    return redirect(url_for('portfolio.projects'))

@portfolio_bp.route('/blog')
@login_required
def blog():
    user_posts = current_user.blog_posts.order_by(BlogPost.created_at.desc()).all()
    return render_template('portfolio/blog.html', posts=user_posts)

@portfolio_bp.route('/blog/add', methods=['GET', 'POST'])
@login_required
def add_blog():
    form = BlogPostForm()
    
    if form.validate_on_submit():
        post = BlogPost(
            user_id=current_user.id,
            title=form.title.data,
            slug=slugify(form.title.data),
            content=form.content.data,
            excerpt=form.excerpt.data,
            is_published=form.is_published.data
        )
        
        # Clean HTML in content
        post.clean_content()
        
        # Handle featured image upload
        if form.featured_image.data:
            filename = save_file(form.featured_image.data, 'projects')  # Use projects folder for blog images too
            if filename:
                post.featured_image = filename
        
        db.session.add(post)
        db.session.commit()
        
        flash('Your blog post has been added!', 'success')
        return redirect(url_for('portfolio.blog'))
    
    return render_template('portfolio/add_blog.html', form=form)
# app/portfolio/routes.py
@portfolio_bp.route('/blog/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    # Check if current user owns this post
    if post.user_id != current_user.id:
        abort(403)
    
    form = BlogPostForm()  # Note: Changed from BlogForm to BlogPostForm
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.slug = slugify(form.title.data)
        post.content = form.content.data
        post.excerpt = form.excerpt.data
        post.is_published = form.is_published.data
        
        # Clean HTML in content
        post.clean_content()
        
        # Handle featured image upload
        if form.featured_image.data:
            # Delete old image if exists
            if post.featured_image:
                delete_file(post.featured_image, 'projects')
            
            # Save new image
            filename = save_file(form.featured_image.data, 'projects')
            if filename:
                post.featured_image = filename
        
        db.session.commit()
        flash('Your blog post has been updated!', 'success')
        return redirect(url_for('portfolio.blog'))
    
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.excerpt.data = post.excerpt
        form.is_published.data = post.is_published
    
    return render_template('portfolio/edit_blog.html', form=form, post=post)

@portfolio_bp.route('/blog/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    
    # Check ownership
    if post.user_id != current_user.id:
        abort(403)
    
    # Delete associated files
    if post.featured_image:
        delete_file(post.featured_image, 'projects')
    
    db.session.delete(post)
    db.session.commit()
    
    flash('Your blog post has been deleted!', 'success')
    return redirect(url_for('portfolio.blog'))


@portfolio_bp.route('/achievements')
@login_required
def achievements():
    user_achievements = current_user.achievements.order_by(Achievement.created_at.desc()).all()
    return render_template('portfolio/achievements.html', achievements=user_achievements)

@portfolio_bp.route('/achievements/add', methods=['GET', 'POST'])
@login_required
def add_achievement():
    form = AchievementForm()
    
    if form.validate_on_submit():
        achievement = Achievement(
            user_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            category=form.category.data,
            issuer=form.issuer.data
        )
        
        # Parse issue date
        if form.issue_date.data:
            try:
                achievement.issue_date = datetime.strptime(form.issue_date.data, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD.', 'warning')
        
        # Handle file upload
        if form.certificate_file.data:
            filename = save_file(form.certificate_file.data, 'achievements')
            if filename:
                achievement.file_path = filename
        
        db.session.add(achievement)
        db.session.commit()
        
        flash('Your achievement has been added!', 'success')
        return redirect(url_for('portfolio.achievements'))
    
    return render_template('portfolio/add_achievement.html', form=form)
@portfolio_bp.route('/achievements/<int:achievement_id>/delete', methods=['POST'])
@login_required
def delete_achievement(achievement_id):
    achievement = Achievement.query.get_or_404(achievement_id)
    
    # Check ownership
    if achievement.user_id != current_user.id:
        abort(403)
    
    # Delete associated files
    if achievement.file_path:
        delete_file(achievement.file_path, 'achievements')
    
    db.session.delete(achievement)
    db.session.commit()
    
    flash('Your achievement has been deleted!', 'success')
    return redirect(url_for('portfolio.achievements'))


@portfolio_bp.route('/skills')
@login_required
def skills():
    user_skills = current_user.skills.order_by(Skill.proficiency.desc(), Skill.name).all()
    form = SkillForm()
    return render_template('portfolio/skills.html', skills=user_skills, form=form)

@portfolio_bp.route('/skills/add', methods=['POST'])
@login_required
def add_skill():
    form = SkillForm()
    
    if form.validate_on_submit():
        # Check if skill already exists for user
        existing_skill = Skill.query.filter_by(
            user_id=current_user.id,
            name=form.name.data
        ).first()
        
        if existing_skill:
            flash('This skill already exists!', 'warning')
        else:
            skill = Skill(
                user_id=current_user.id,
                name=form.name.data,
                proficiency=form.proficiency.data
            )
            db.session.add(skill)
            db.session.commit()
            flash('Skill added successfully!', 'success')
    
    return redirect(url_for('portfolio.skills'))

@portfolio_bp.route('/skills/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check ownership
    if skill.user_id != current_user.id:
        abort(403)
    
    db.session.delete(skill)
    db.session.commit()
    
    flash('Skill deleted successfully!', 'success')
    return redirect(url_for('portfolio.skills'))

@portfolio_bp.route('/analytics')
@login_required
def analytics():
    stats = get_view_stats(current_user.id)
    
    # Get top viewed projects
    top_projects = current_user.projects.order_by(Project.views.desc()).limit(5).all()
    
    # Get recent views
    recent_views = ViewLog.query.filter(
        ViewLog.user_id == current_user.id
    ).order_by(
        ViewLog.timestamp.desc()
    ).limit(10).all()
    
    return render_template('portfolio/analytics.html',
                         stats=stats,
                         top_projects=top_projects,
                         recent_views=recent_views)

# Public Portfolio Routes
@portfolio_bp.route('/<username>')
def public_portfolio(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    # Log this view
    log_view('profile', user.id, request)
    
    # Get user's public projects
    projects = user.projects.filter_by(is_public=True)\
        .order_by(Project.created_at.desc()).all()
    
    # Get user's published blog posts
    blog_posts = user.blog_posts.filter_by(is_published=True)\
        .order_by(BlogPost.created_at.desc()).all()
    
    # Get user's achievements
    achievements = user.achievements.order_by(Achievement.created_at.desc()).all()
    
    # Get user's skills
    skills = user.skills.order_by(Skill.proficiency.desc()).all()
    
    return render_template('portfolio/public_portfolio.html',
                         user=user,
                         projects=projects,
                         blog_posts=blog_posts,
                         achievements=achievements,
                         skills=skills)

@portfolio_bp.route('/<username>/project/<slug>')
def project_detail(username, slug):
    user = User.query.filter_by(username=username).first_or_404()
    project = Project.query.filter_by(
        user_id=user.id,
        slug=slug,
        is_public=True
    ).first_or_404()
    
    # Log this view
    log_view('project', project.id, request)
    project.increment_views()
    
    return render_template('portfolio/project_detail.html',
                         user=user,
                         project=project)

@portfolio_bp.route('/<username>/blog/<slug>')
def blog_detail(username, slug):
    user = User.query.filter_by(username=username).first_or_404()
    post = BlogPost.query.filter_by(
        user_id=user.id,
        slug=slug,
        is_published=True
    ).first_or_404()
    
    # Log this view
    log_view('blog', post.id, request)
    post.views += 1
    db.session.commit()
    
    return render_template('portfolio/blog_detail.html',
                         user=user,
                         post=post)

# API Routes
@portfolio_bp.route('/api/profile/update', methods=['POST'])
@login_required
def api_update_profile():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        if 'full_name' in data:
            current_user.full_name = data['full_name']
        if 'bio' in data:
            current_user.bio = data['bio']
        if 'tagline' in data:
            current_user.tagline = data['tagline']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Profile updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@portfolio_bp.route('/api/projects', methods=['GET'])
def api_get_projects():
    username = request.args.get('username')
    
    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        projects = user.projects.filter_by(is_public=True).all()
    else:
        projects = Project.query.filter_by(is_public=True)\
            .order_by(Project.created_at.desc())\
            .limit(20).all()
    
    projects_data = [{
        'id': p.id,
        'title': p.title,
        'slug': p.slug,
        'description': p.short_description or p.description[:200] + '...',
        'tech_stack': p.tech_list,
        'views': p.views,
        'created_at': p.created_at.isoformat() if p.created_at else None,
        'user': {
            'username': p.user.username,
            'full_name': p.user.full_name,
            'profile_pic': p.user.profile_pic
        }
    } for p in projects]
    
    return jsonify({'projects': projects_data})

@portfolio_bp.route('/api/upload', methods=['POST'])
@login_required
def api_upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    subfolder = request.form.get('type', 'projects')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = save_file(file, subfolder)
    
    if filename:
        return jsonify({
            'success': True,
            'filename': filename,
            'url': f"/static/uploads/{subfolder}/{filename}"
        })
    else:
        return jsonify({'error': 'Invalid file type'}), 400