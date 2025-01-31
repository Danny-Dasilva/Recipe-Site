import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             PostForm, RequestResetForm, ResetPasswordForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import json

@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('home.html', posts=posts)




@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_img', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

##delete this later
@app.route("/post/new1", methods=['GET', 'POST'])
@login_required
def new_post1():
    form = PostForm()
    if form.validate_on_submit():
        if form.picture1.data:
            form_picture_file = save_post_picture(form.picture1.data)
            form.picture1.data = form_picture_file
        ingredients = "666666"
        post = Post(title=form.title.data, ingredients=ingredients,steps=form.content.data, image=form.picture1.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'your post has been uploaded', 'success')
        return redirect(url_for('home'))
    
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

#delete this later
@app.route("/post2/<int:post_id>")
def post2(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post1.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update2", methods=['GET', 'POST'])
@login_required
def update_post2(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        print('6')
        form.title.data = post.title
        form.content.data = post.ingredients

    return render_template('create_post.html', title='Update Post',
                           post=post, legend='Update Post')


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        print('error')
        abort(403)
    print(request.method)
    if request.method == 'POST':
        form = PostForm()
        if form.picture1.data:
            form_picture_file = save_post_picture(form.picture1.data)
            form.picture1.data = form_picture_file
        
        data = request.json
        post.title = request.json.get('title')
        post.time = request.json.get('time')
        post.serves = request.json.get('serves')
        post.cal = request.json.get('cal')
        post.steps = request.json.get('steps')
        post.ingredients = request.json.get('ingredients')

        # post.image=form.picture1.data
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    elif request.method == 'GET':
        ingred = post.ingredients
        steps = post.steps
    return render_template('create_post.html', title='Update Post',
                           post=post, ingred=json.dumps(ingred), post_id=post_id, steps=json.dumps(steps), legend='Update Post')




@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))


@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)



@app.route('/your/flask/ingredients', methods=['POST'])
def ingredients():
    if request.method == 'POST':
       names = request.get_json()
       for i in names:
            print(names[i])			
    return '', 200

@app.route('/your/flask/steps', methods=['POST'])
def steps():
    
    if request.method == 'POST':
        
        form = PostForm()
        if form.picture1.data:
            form_picture_file = save_post_picture(form.picture1.data)
            form.picture1.data = form_picture_file
        
        #return redirect(url_for('home'))
        data = request.json
        title = request.json.get('title')
        time = request.json.get('time')
        serves = request.json.get('serves')
        cal = request.json.get('cal')
        steps = request.json.get('steps')
        igred = request.json.get('ingredients')
        print(title, time, serves, cal)
        print(steps)
        print(igred)
        

        post = Post(title=title, time=time, serves=serves, cal=cal, ingredients=igred,steps=steps, image=form.picture1.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(f'your post has been uploaded', 'success')
            		
    return '', 200

@app.route('/post/new')
@login_required
def new_post():	
    return render_template('java3.html')

@app.route("/test")
def test():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=6)
    return render_template('home1.html', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    data = post.ingredients
    x = zip(*[iter(data)]*2)
    return render_template('post.html', title=post.title, post=post, ingred=x)

