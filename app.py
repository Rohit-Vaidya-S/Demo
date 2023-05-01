import datetime
from flask import Flask, render_template, request, url_for, redirect, flash, session
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__, template_folder='../templates')
client = MongoClient("mongodb+srv://Microblog:Microblog@atlascluster.6du93ie.mongodb.net/test")
app.db = client.microblog
entries = []
userInfo = []
app.secret_key = "abcdefgh"  
posts_limit = 6

@app.route("/", methods=["GET", "POST"])
def userLogin():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")        
        user = app.db.userInfo.find_one({"email": email, "password": password})
        if user:
            session['user'] = email
            total_entries = app.db.entries.count_documents({})
            total_pages = (total_entries + posts_limit - 1) 
            return render_template('home.html', total_pages=total_pages)
        else:
            flash('You have to first SignUp!')
            return render_template('userSignUp.html')
    return render_template('userLogin.html')
    
@app.route("/signUp", methods=["GET", "POST"])
def userSignUp():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        admin = request.form.get('admin')
        if email in app.db.userInfo.find({'email': email}):
            flash("User with email {email} already exists!")
            return redirect(url_for('userLogin'))

        userInfo.append((name,email,password))
        app.db.userInfo.insert_one({"name":name, "email": email, "password": password, "admin":admin})
        flash("Signed up successfully, please enter email and password")
        return render_template('userLogin.html') 
    else:
        return render_template('userSignUp.html')


@app.route("/home", methods=["GET", "POST"])
@app.route("/home/<int:page>", methods=["GET", "POST"])
def home(page=1):
    if 'user' not in session:
        return redirect(url_for('userLogin'))

    if request.method == "POST":
        entry_content = request.form.get("content")
        formatted_data = datetime.datetime.today().strftime("%Y-%m-%d")
        entry_id = ObjectId()
        app.db.entries.insert_one({"content": entry_content, "date": formatted_data, "_id": entry_id, "is_deleted": False})

    total_entries = app.db.entries.count_documents({"is_deleted": False})
    total_pages = (total_entries + posts_limit - 1)
    print(total_pages)
    entries_with_date = [
        (
            entry['content'],
            entry['date'],
            datetime.datetime.strptime(entry['date'], "%Y-%m-%d").strftime("%b %d"),
            entry['_id']
        )
        for entry in app.db.entries.find({"is_deleted": False}).sort("date", -1).skip((page - 1) * posts_limit).limit(posts_limit)
    ]
    
    return render_template("home.html", entries=entries_with_date, page=page, total_pages=total_pages)


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        keyword = request.form['keyword']
        total_entries = app.db.entries.count_documents({"content": {"$regex": f".*{keyword}.*", "$options": "i"}})
        total_pages = (total_entries + posts_limit - 1)
        entries_with_date = [
            (
                entry['content'],
                entry['date'],
                datetime.datetime.strptime(entry['date'], "%Y-%m-%d").strftime("%b %d"),
                entry['_id']
            )
            for entry in app.db.entries.find({"content": {"$regex": f".*{keyword}.*", "$options": "i"}}).sort("date", -1)
        ]
        return render_template("home.html", entries=entries_with_date, total_pages=total_pages)
    return render_template('search.html')


@app.route("/delete/<id>", methods=["GET","POST"])
def delete(id):
    user = app.db.userInfo.find_one({"email": session['user']})
    if not user or not user.get('admin'):
        return "Only admins can delete it.", 404

    entry = app.db.entries.find_one({"_id": ObjectId(id)})
    if not entry:
        return "Entry not found", 404

    app.db.entries.update_one({"_id": ObjectId(id)}, {"$set": {"is_deleted": True}})
    return redirect(url_for('home'))


@app.route("/update/<id>", methods=["GET", "POST"])
def update(id):
    entry = app.db.entries.find_one({"_id": ObjectId(id)})
    if not entry:
        return "Entry not found", 404

    if request.method == "POST":
        new_content = request.form.get("content")
        formatted_data = datetime.datetime.today().strftime("%Y-%m-%d")
        app.db.entries.update_one(
            {"_id": ObjectId(id)},
            {"$set": {"content": new_content, "date": formatted_data}}
        )
        entries = app.db.entries.find().sort("date", -1)

        entries_with_date = [
            (
                entry["content"],
                entry["date"],
                datetime.datetime.strptime(entry["date"], "%Y-%m-%d").strftime("%b %d"),
                entry["_id"]
            )
            for entry in entries
        ]
        return redirect(url_for('home', entries=entries_with_date))
    return render_template("update.html", entry=entry)

@app.route("/calendar", methods=["GET", "POST"])
def calendar():
    return render_template("calendar.html")

@app.route("/about", methods=["GET", "POST"])
def about():
    return render_template("about.html")

@app.route("/how", methods=["GET", "POST"])
def how():
    return render_template("how.html")

@app.route("/hello")
def hello():
    return render_template("hello.html")

if __name__ == '__main__':
    app.run(port="5000", debug=True)