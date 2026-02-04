from functools import wraps
from flask import (
    render_template,
    request,
    session,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
)
from project.config import app, db
from project import models


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Please log in.")
            return jsonify({"status": 0, "message": "Please log in."}), 401
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """Searches the database for entries, then displays them."""
    entries = db.session.query(models.Post)
    return render_template("index.html", entries=entries)


@app.route("/add", methods=["POST"])
def add_entry():
    """Adds new post to the database."""
    if not session.get("logged_in"):
        abort(401)
    new_entry = models.Post(request.form["title"], request.form["text"], session.get("active_user"))
    db.session.add(new_entry)
    db.session.commit()
    flash("New entry was successfully posted")
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login/authentication/session management."""
    error = None
    if request.method == "POST":
        user = db.session.query(models.User).filter_by(name=request.form["username"]).first()
        if  not user or user.password != request.form["password"]:
            error = "Invalid username or password"
        else:
            session["logged_in"] = True
            session["active_user"] = user.name
            flash("You were logged in")
            ### Please work
            ### Trying using "username" from login fuction instead of models.User(request.form["name"]
            session["username"] = user.name # does it have to be this due to the model python?
            return redirect(url_for("index"))
    return render_template("login.html", error=error)

@app.route("/newuser", methods=["GET", "POST"])
def new_user():
    if request.method == "POST" and request.form.get("password") and request.form.get("username"):
        newuser = models.User(request.form["username"], request.form["password"])
        #This whole next few lines are a test to prevent from using the same name
        #Because I kept getting an error with "jacobbauch3"
        #variable define error, trying to fix that
        blehh = request.form["username"]
        #okay from copying below, let's check
        namecheck = db.session.query(models.User).filter_by(name=blehh).first()
        if namecheck:
            return render_template("newuser.html", error="Error, username in use already")
        # IT works! :D

        try:
            db.session.add(newuser)
            db.session.commit()
            session["logged_in"] = True
            session["active_user"] = user.name
            flash("New User Created")
            #Have to add a thing here too or else new users wouldn't have a display name
            #I have messed up here somehow with user.name again ... 
            session["username"] = newuser.name 
            #Does it need to be newuser.name because of the template newuser.html? May as well test
            return redirect(url_for("index"))
        except Exception as e:
            return render_template("newuser.html", error="Error when adding user: " + str(e))
    else:
        return render_template("newuser.html")

@app.route("/logout")
def logout():
    """User logout/authentication/session management."""
    session.pop("logged_in", None)
    session.pop("active_user", None)
    flash("You were logged out")
    return redirect(url_for("index"))


@app.route("/delete/<int:post_id>", methods=["GET"])
@login_required
def delete_entry(post_id):
    """Deletes post from database."""
    result = {"status": 0, "message": "Error"}
    try:
        new_id = post_id
        db.session.query(models.Post).filter_by(id=new_id).delete()
        db.session.commit()
        result = {"status": 1, "message": "Post Deleted"}
        flash("The entry was deleted.")
    except Exception as e:
        result = {"status": 0, "message": repr(e)}
    return jsonify(result)


@app.route("/search/", methods=["GET"])
def search():
    query = request.args.get("query")
    entries = db.session.query(models.Post)
    if query:
        return render_template("search.html", entries=entries, query=query)
    return render_template("search.html")


if __name__ == "__main__":
    app.run()


@app.route("/profile/<string:viewed_user>")
def view_profile(viewed_user):
    queried_user = db.session.query(models.User).filter_by(name=viewed_user).first()
    if not queried_user:
        flash("User \"%s\" does not exist" % viewed_user)
        return redirect(url_for("index"))
            
    entries = db.session.query(models.Post).filter_by(author=queried_user.name)
    return render_template("userpage.html", user=queried_user, entries=entries)