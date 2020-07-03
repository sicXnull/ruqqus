import time
import jinja2
import pyotp
from flask import *

from ruqqus.helpers.wrappers import *
import ruqqus.classes
from ruqqus.classes import *
from ruqqus.mail import *
from ruqqus.__main__ import app, limiter

#take care of misc pages that never really change (much)
@app.route('/assets/<path:path>')
@limiter.exempt
def static_service(path):
    resp = make_response(send_from_directory('./assets', path))
    resp.headers.add("Cache-Control", "public")

    if request.path.endswith('.css'):
        resp.headers.add("Content-Type", "text/css")
    return resp

@app.route("/robots.txt", methods=["GET"])
def robots_txt():
    return send_file("./assets/robots.txt")

@app.route("/slurs.txt", methods=["GET"])
def slurs():
    return send_file("./assets/slurs.txt")

@app.route("/settings", methods=["GET"])
@auth_required
def settings(v):
    return redirect("/settings/profile")

@app.route("/settings/profile", methods=["GET"])
@auth_required
def settings_profile(v):
    return render_template("settings_profile.html",
                           v=v)

@app.route("/help/titles", methods=["GET"])
@auth_desired
def titles(v):
    titles = [x for x in g.db.query(Title).order_by(text("id asc")).all()]
    return render_template("/help/titles.html",
                           v=v,
                           titles=titles)

@app.route("/help/terms", methods=["GET"])
@auth_desired
def help_terms(v):
    
    cutoff=int(environ.get("tos_cutoff",0))

    return render_template("/help/terms.html",
                           v=v,
                           cutoff=cutoff)

@app.route("/help/badges", methods=["GET"])
@auth_desired
def badges(v):
    badges=[x for x in g.db.query(BadgeDef).order_by(text("rank asc, id asc")).all()]
    return render_template("help/badges.html",
                           v=v,
                           badges=badges)

@app.route("/help/admins", methods=["GET"])
@auth_desired
def help_admins(v):

    admins = g.db.query(User).filter(User.admin_level>1, User.id > 1).order_by(User.id.asc()).all()
    admins=[x for x in admins]

    exadmins = g.db.query(User).filter_by(admin_level=1).order_by(User.id.asc()).all()
    exadmins=[x for x in exadmins]

    return render_template("help/admins.html",
                           v=v,
                           admins=admins,
                           exadmins=exadmins
                           )

@app.route("/settings/security", methods=["GET"])
@auth_required
def settings_security(v):
    return render_template("settings_security.html",
                           v=v,
                           mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
                           error=request.args.get("error") or None,
                           msg=request.args.get("msg") or None
                          )

@app.route("/assets/favicon.ico", methods=["GET"])
def favicon():
    return send_file("./assets/images/logo/favicon.png")

@app.route("/my_info",methods=["GET"])
@auth_required
def my_info(v):
    return render_template("my_info.html", v=v)

@app.route("/about/<path:path>")
def about_path(path):
    return redirect(f"/help/{path}")

@app.route("/help/<path:path>", methods=["GET"])
@auth_desired
def help_path(path, v):
    try:
        return render_template(safe_join("help", path+".html"), v=v)
    except jinja2.exceptions.TemplateNotFound:
        abort(404)


@app.route("/help", methods=["GET"])
@auth_desired
def help_home(v):
    return render_template("help.html", v=v)


@app.route("/help/submit_contact", methods=["POST"])
@is_not_banned
@validate_formkey
def press_inquiry(v):

    data=[(x, request.form[x]) for x in request.form if x !="formkey"]
    data.append(("username",v.username))
    data.append(("email",v.email))

    data=sorted(data, key=lambda x: x[0])

    if request.form.get("press"):
        email_template="email/press.html"
    else:
        email_template="email/contactform.html"

    try:
        send_mail(environ.get("admin_email"),
                  "Press Submission",
                  render_template(email_template,
                                  data=data
                                  ),
                  plaintext=str(data)
                  )
    except:
            return render_template("/help/press.html",
                           error="Unable to save your inquiry. Please try again later.",
                           v=v)

    return render_template("/help/press.html",
                           msg="Your inquiry has been saved.",
                           v=v)