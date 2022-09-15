from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy.sql import func
from flask import render_template ,redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine


db = SQLAlchemy()

app = Flask(__name__)
app.config['SECRET_KEY'] = '123456789234'

# db_cred = {
# 'user': 'root',		 # DATABASE USER
# 'pass': '',	 # DATABASE PASSWORD
# 'host': '127.0.0.1', # DATABASE HOSTNAME
# 'name': 'dbmsblogdatabase' # DATABASE NAME
# }
# app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://\
# {db_cred['user']}:{db_cred['pass']}@{db_cred['host']}/\
# {db_cred['name']}"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:harsha666@localhost/blogdatabase'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://bbngoayeibqzee:64f4aa265154ae5208b9a8f8011cc1b31d4f1dc0b06c67ad4091cc6ae69ff17b@ec2-44-205-63-142.compute-1.amazonaws.com:5432/d36q2crd30gejk'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db  = SQLAlchemy(app)


#login manager
login_manager = LoginManager(app)

login_manager.login_view = "logIn"

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


#database models

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    username = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone = True), default = func.now())
    posts = db.relationship('Post', backref='user', passive_deletes = True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)
    likes = db.relationship('Likes', backref='user', passive_deletes=True)
    replies = db.relationship('Reply', backref='user', passive_deletes=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(300), nullable = False)
    content = db.Column(db.Text, nullable = False)
    date_created = db.Column(db.DateTime(timezone = True), default = func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)
    likes = db.relationship('Likes', backref='post', passive_deletes=True)
    replies = db.relationship('Reply', backref='post', passive_deletes=True)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    replies = db.relationship('Reply', backref='comment', passive_deletes=True)


class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey(
        'user.id', ondelete="CASCADE"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'post.id', ondelete="CASCADE"), nullable=False)

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(300), nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id", ondelete="CASCADE"), nullable = False)
    comment_id = db.Column(db.Integer, db.ForeignKey("comment.id", ondelete="CASCADE"), nullable = False)

#table for maintaining update log of posts
class Update_log(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    post_id = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, nullable=False)
    post_title = db.Column(db.String(300), nullable = False)
    updated_date = db.Column(db.DateTime(timezone=True), default=func.now())



#authentication routes

@app.route("/signup", methods = ['GET', 'POST'])
def signUp():

    if request.method == 'POST':
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password1")
        confirm_password = request.form.get("password2")


        #extracting email to check wether the email and username already exist in the database
        #if the user is already exists then flash the message to the user that there is an account
        # already in that mail or username 
        email_exists = User.query.filter_by(email = email).first()
        user_name_exists = User.query.filter_by(username = username).first()

        if email_exists:
            flash("Email already in use.", category='error')
        elif user_name_exists:
            flash("username taken.", category='error')
        elif password!=confirm_password:
            flash('Password don\'t match.', category='error')
        elif len(username) < 2:
            flash('Username too short.', category='error')
        elif len(password) < 6:
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash('Email is invlaid.', category='error')
        else:


            #create a new user
            #sha256 is just an encryption method
                # hashedpass = generate_password_hash(password, method='sha256') ---

                #db = create_engine('mysql+pymysql://root:harsha666@localhost/blogdatabase', encoding='utf8')

                #-----------
                # db = create_engine('postgresql://pnczxxjujgbowc:4597bb69f36e5bab482200d7ac0178fbea321764eb1ef2a103aa1f5c37694fd1@ec2-44-207-133-100.compute-1.amazonaws.com:5432/df0o1s75k024ud', encoding='utf8')
                # connection = db.raw_connection()
                # try:
                #     cursor = connection.cursor()
                #     cursor.callproc("sign_up_user", [email, username, hashedpass])
                #     cursor.close()
                #     connection.commit()
                # finally:
                #     connection.close()
                #------------

               # db.engine.execute(f"CALL sign_up_user('{email}', '{username}', '{hashedpass}')")


                new_user = User(email = email, username = username, password = generate_password_hash(password, method='sha256'))

             #adding new user to database

                db.session.add(new_user)
                db.session.commit()
                login_user(new_user, remember=True)

                flash('User Created', category='success')

            #after adding redirect them to the home page where you can see all your post
            #redirecting the user after logging in
                return redirect(url_for('home'))

    
    return render_template("signup_form.html", user = current_user)


@app.route("/login", methods = ['GET', 'POST'])
def logIn():

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email = email).first()

        if user:
            if check_password_hash(user.password, password):
                flash('logged in', category= 'success')
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                flash('Password is incorrect.', category='error')
        else:
            flash('Email does not exist', category='error')


    return render_template("login_form.html", user = current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


#app routes


@app.route("/")
@app.route("/home")
@login_required
def home():
    posts = Post.query.all()
    return render_template("home.html", user = current_user, posts = posts)

@app.route("/posts")
def display_all_post():
    posts = Post.query.all()
    return render_template("all_posts.html", user = current_user, posts = posts)


#creating a new post
@app.route("/create_post", methods = ['GET', 'POST'])
@login_required
def createPost():
    if request.method == 'POST':
        post_title = request.form.get('blog_title')
        post_content = request.form.get('blog_content')

        if post_content:                                    
            #print(post_content)
            post = Post(title = post_title, content = post_content, author = current_user.id)
            db.session.add(post)
            db.session.commit()
            flash('post created', category='success')
            redirect(url_for('home'))
        else:
            flash('post content cannot be empty', category='error')

    return render_template("create_post2.html", user = current_user)

#deleting a particular post
@app.route("/delete_post/<id>")
@login_required
def delete_post(id):
    post = Post.query.filter_by(id = id).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif current_user.id != post.author:
        flash('You dont have permission to delete this post', category='error')
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted', category = 'success')
    
    return redirect(url_for('display_all_post'))


#updating a particular post
@app.route("/update_post/<id>", methods=['GET', 'POST'])
@login_required
def update_post(id):

    post = Post.query.filter_by(id = id).first()

    if not post:
        flash('Post does not exist.', category='error')
    elif current_user.id != post.author:
        flash('You dont have permission to delete this post', category='error')

    elif request.method == 'POST':
        post.title = request.form.get('blog_title')
        post.content = request.form.get('blog_content')
        db.session.commit()
        flash('Post Updated', category='success')

        return redirect(url_for('display_all_post'))

    

    return render_template("update_post.html", user = current_user, post = post)

#all posts of a particular user
@app.route("/posts/<user_id>")
@login_required
def display_all_post_of_particular_user(user_id):
    posts = Post.query.filter_by(author = user_id).all()

    #logic to get user name of the clicked post
    if not posts:
        flash('No posts created', category = 'error')
        return redirect(url_for('home'))
    else:
        first_post_of_user = Post.query.filter_by(author = user_id).first()
        username = first_post_of_user.user.username

    return render_template('posts.html', user = current_user, posts = posts, username = username)

#viewing particular post
@app.route("/view_post/<post_id>")
@login_required
def display_full_post(post_id):
    post = Post.query.filter_by(id = post_id).first()

    return render_template('view_post.html', user = current_user, post = post)


#creating a comment
@app.route("/create-comment/<post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    text = request.form.get('comment')

    if not text:
        flash('Comment cannot be empty.', category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment = Comment(
                text=text, author=current_user.id, post_id=post_id)
            db.session.add(comment)
            db.session.commit()
        else:
            flash('Post does not exist.', category='error')

    return redirect(url_for('display_full_post', post_id = post_id))

#deleting a comment
@app.route("/delete-comment/<comment_id>")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()

    if not comment:
        flash('Comment does not exist.', category='error')
    elif current_user.id != comment.author and current_user.id != comment.post.author:
        flash('You do not have permission to delete this comment.', category='error')
    else:
        post_id = comment.post_id
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('display_full_post', post_id = post_id))

#liking and unliking a post
@app.route("/like-post/<post_id>", methods=['GET'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Likes.query.filter_by(
        author=current_user.id, post_id=post_id).first()

    if not post:
        flash('Post does not exists', category='error')
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Likes(author=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return redirect(url_for('display_all_post'))

#creating a reply
@app.route("/create-reply/<post_id>/<comment_id>", methods=['POST'])
@login_required
def create_reply(post_id, comment_id):

    reply_text = request.form.get('reply')

    if not reply_text:
        flash('Reply cannot be empty', category='error')
    else:
        reply = Reply(text = reply_text, author = current_user.id, post_id = post_id, comment_id = comment_id)
        db.session.add(reply)
        db.session.commit()

    return redirect(url_for('display_full_post', post_id = post_id))

#deleting a reply
@app.route("/delete-reply/<reply_id>")
@login_required
def delete_reply(reply_id):

    reply = Reply.query.filter_by(id = reply_id).first()

    if not reply:
        flash('Reply does not exists!', category='error')
    else:
        post_id = reply.post_id
        db.session.delete(reply)
        db.session.commit()

    return redirect(url_for('display_full_post', post_id = post_id))

#displaying the updated log to user
@app.route("/update-log")
@login_required
def show_update_log():

    posts = Post.query.all()
    updated_posts = Update_log.query.filter_by(author_id = current_user.id)

    if not posts:
        flash('No posts', category='error')
        return redirect(url_for('home'))
    elif not updated_posts:
        flash('You have not updated any posts', category='error')
        return redirect(url_for('home'))


    return render_template('update_info.html', user = current_user, posts = posts, updated_posts = updated_posts)



if __name__ == '__main__':
    app.run(debug=True)