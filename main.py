from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import math


with open("config.json", 'r') as c:
    perams = json.load(c)["perams"]




app = Flask(__name__)
app.secret_key="super-secret-key"

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME= "chandannathji@gmail.com",
    MAIL_PASSWORD= "chandan2426"
)
mail=Mail(app)
local_host = True
if(local_host):
    app.config['SQLALCHEMY_DATABASE_URI'] = perams["local_uri"]
    
else:

    app.config['SQLALCHEMY_DATABASE_URI'] = perams["prod_uri"]
    

db = SQLAlchemy(app)




class Posts(db.Model):
    
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    subtitle = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    
    


@app.route("/")
def home():
    post=Posts.query.filter_by().all()
    posts=[]
    for i in range(len(post)):
        posts.append(post[len(post)-(i+1)])


    last=math.ceil(len(posts)/int(perams["no_of_posts"]))
    page=request.args.get('page')
    
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    
    posts=posts[(page-1)*int(perams["no_of_posts"]): (page-1)*int(perams["no_of_posts"])+int(perams["no_of_posts"])]
   
    if page==1:
        prev="#"
        next="/?page="+ str(page+1)
    elif page==last:
        prev="/?page="+ str(page-1)
        next="#"
    else:
        prev="/?page="+ str(page-1)
        next="/?page="+ str(page+1)





    return render_template('index.html', perams=perams, posts=posts,prev=prev, next=next)










@app.route("/about")
def about():
    return render_template('about.html', perams=perams)


@app.route("/dashboard", methods=['GET','POST'])
def login():
    if (('user' in session) and session['user']==perams['admin_user'] and session['pass']==perams['admin_pass']):
        
        posts=Posts.query.all()
        return render_template('/dashboard.html', perams=perams,posts=posts)

    elif request.method=='POST':
        
        username=request.form.get('uname')
        userpass=request.form.get('upass')
        

        if (username==perams['admin_user'] and userpass==perams['admin_pass']):
            
            session['user']=username
            session['pass']=userpass
            posts=Posts.query.all()
            return render_template('/dashboard.html', perams=perams,posts=posts)
        else:
            
            return render_template('login.html', perams=perams)
    else:
        
        return render_template('login.html', perams=perams)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/dashboard")


@app.route("/edit/<string:sno>" , methods=['GET', 'POST'])
def edit(sno):
    if (('user' in session) and session['user']==perams['admin_user'] and session['pass']==perams['admin_pass']):
        
        if request.method=="POST":
            box_title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()
            no=sno

           

            if sno=='0':

              
                post = Posts(title=box_title, subtitle=subtitle, slug=slug, content=content, date=date)
                db.session.add(post)
                db.session.commit()
               
                return redirect("/dashboard")
            else:
                
                post=Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.subtitle = subtitle
                post.slug = slug
                post.content = content
                post.date = date
                
                db.session.commit()
                return redirect('/edit/'+sno) 
       
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', perams=perams, sno=sno,post=post)

    else:
        return render_template('login.html', perams=perams)

@app.route("/delete/<string:sno>" , methods=['GET', 'POST'])

def delete(sno):
    if (('user' in session) and session['user']==perams['admin_user'] and session['pass']==perams['admin_pass']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect("/dashboard")







@app.route("/post/<string:post_slug>", methods=['GET'])
def post_data(post_slug):

    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html', perams=perams, post=post)
    

@app.route("/uploder", methods=['GET', 'POST'])
def uploder():
   if (('user' in session) and session['user']==perams['admin_user'] and session['pass']==perams['admin_pass']):

        if request.method=='POST':
            f=request.files['file']
            f.save(os.path.join(perams['location'],secure_filename(f.filename)))
            render_template("dashboard.html",perams=perams)
            return redirect("dashboard")
            


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        '''Add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        mail.send_message("New Message from website", sender=email ,recipients=["yourmail@gmail.com"],body=f"Name: {name}\nPhone: {phone}\n{message}")
        return redirect("/")
    return render_template('contact.html', perams=perams)


app.run(debug=True)
