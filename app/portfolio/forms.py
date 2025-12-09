from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length, URL, Optional
from app.extensions import csrf

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

    full_name = StringField('Full Name', 
                           validators=[Length(max=100)])
    bio = TextAreaField('Bio', 
                       validators=[Length(max=1000)])
    tagline = StringField('Tagline', 
                         validators=[Length(max=200)])
    location = StringField('Location', 
                          validators=[Length(max=100)])
    website = StringField('Website', 
                         validators=[Optional(), URL()])
    github = StringField('GitHub', 
                        validators=[Optional(), URL()])
    linkedin = StringField('LinkedIn', 
                          validators=[Optional(), URL()])
    twitter = StringField('Twitter', 
                         validators=[Optional(), URL()])
    profile_pic = FileField('Profile Picture',
                           validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                                  'Images only!')])
    submit = SubmitField('Update Profile')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', 
                       validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', 
                               validators=[DataRequired()])
    short_description = StringField('Short Description (for cards)', 
                                   validators=[Length(max=300)])
    tech_stack = StringField('Technologies (comma-separated)',
                            validators=[DataRequired()])
    repo_url = StringField('Repository URL', 
                          validators=[Optional(), URL()])
    live_url = StringField('Live Demo URL', 
                          validators=[Optional(), URL()])
    featured_image = FileField('Featured Image',
                              validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                                     'Images only!')])
    is_public = BooleanField('Make project public')
    is_featured = BooleanField('Feature this project')
    submit = SubmitField('Save Project')

class BlogPostForm(FlaskForm):
    title = StringField('Post Title', 
                       validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', 
                           validators=[DataRequired()])
    excerpt = StringField('Excerpt', 
                         validators=[Length(max=300)])
    featured_image = FileField('Featured Image',
                              validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                                     'Images only!')])
    is_published = BooleanField('Publish immediately')
    submit = SubmitField('Save Post')

class AchievementForm(FlaskForm):
    title = StringField('Title', 
                       validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    category = SelectField('Category', 
                          choices=[('certificate', 'Certificate'),
                                  ('award', 'Award'),
                                  ('publication', 'Publication'),
                                  ('other', 'Other')])
    issuer = StringField('Issuer/Organization', 
                        validators=[Length(max=100)])
    issue_date = StringField('Issue Date (YYYY-MM-DD)')
    certificate_file = FileField('Certificate File',
                                validators=[FileAllowed(['pdf', 'jpg', 'jpeg', 'png'], 
                                                       'PDF or Images only!')])
    submit = SubmitField('Add Achievement')

class SkillForm(FlaskForm):
    name = StringField('Skill Name', 
                      validators=[DataRequired(), Length(max=50)])
    proficiency = SelectField('Proficiency Level',
                            choices=[(1, 'Beginner'),
                                    (2, 'Intermediate'),
                                    (3, 'Advanced'),
                                    (4, 'Expert'),
                                    (5, 'Master')],
                            coerce=int)
    submit = SubmitField('Add Skill')