from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    current_app,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from lxml import etree
import requests
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24).hex()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class EditXMLForm(FlaskForm):
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Save Changes")


class XMLDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    filename = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)

    user = db.relationship("User", backref=db.backref("documents", lazy=True))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class CustomResolver(etree.Resolver):
    def resolve(self, url, id, context):
        if url.startswith("http://") or url.startswith("https://"):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return self.resolve_string(response.text, context)
            except requests.RequestException as e:
                raise etree.LxmlError(f"Failed to load URL: {e}")
        else:
            raise etree.LxmlError("External entity blocked")


parser = etree.XMLParser(load_dtd=True, no_network=False)
parser.resolvers.add(CustomResolver())


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username is already taken. Please choose a different one."
            )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


@app.route("/edit_document/<int:doc_id>", methods=["GET", "POST"])
@login_required
def edit_document(doc_id):
    document = XMLDocument.query.filter_by(
        id=doc_id, user_id=current_user.id
    ).first_or_404()
    form = EditXMLForm(content=document.content)
    result = None

    if form.validate_on_submit():
        document.content = form.content.data
        db.session.commit()
        flash("Changes saved successfully.", "success")

        try:
            xml_tree = etree.fromstring(document.content.encode("utf-8"), parser)
            result = etree.tostring(xml_tree).decode()
        except etree.XMLSyntaxError as e:
            flash(f"XML Execution failed: {str(e)}", "danger")
        except etree.LxmlError as e:
            flash(f"Blocked entity: {str(e)}", "danger")

        return render_template(
            "edit_document.html", form=form, document=document, result=result
        )

    return render_template(
        "edit_document.html", form=form, document=document, result=result
    )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    documents = XMLDocument.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", documents=documents)


@app.route("/document/<int:doc_id>")
@login_required
def view_document(doc_id):
    document = XMLDocument.query.filter_by(
        id=doc_id, user_id=current_user.id
    ).first_or_404()
    return render_template("view_document.html", document=document)


@app.route("/upload", methods=["POST"])
@login_required
def upload():
    xml_file = request.files["xmlfile"]
    if not xml_file:
        flash("No file provided", "danger")
        return redirect(url_for("dashboard"))

    content = xml_file.read().decode("utf-8")

    if "<!DOCTYPE" in content or "<!ENTITY" in content:
        flash("Unsafe XML content detected", "danger")
        return redirect(url_for("dashboard"))

    try:
        parser = etree.XMLParser(load_dtd=False, no_network=True)
        etree.fromstring(content.encode("utf-8"), parser)

        document = XMLDocument(
            user_id=current_user.id, filename=xml_file.filename, content=content
        )
        db.session.add(document)
        db.session.commit()
        flash("Document uploaded successfully.", "success")
    except etree.XMLSyntaxError:
        flash("Invalid XML", "danger")

    return redirect(url_for("dashboard"))


@app.route("/api/v1/get_flag", methods=["GET", "POST"])
def get_flag():
    if request.remote_addr != "127.0.0.1":
        return "Access allowed only from inner server", 403

    try:
        with open("flag.txt", "r") as file:
            flag = file.read().strip()
        return flag
    except IOError:
        return "Error reading flag file", 500


def clear_database():
    with app.app_context():
        User.query.delete()
        XMLDocument.query.delete()
        db.session.commit()
        print("Users and documents deleted.")


scheduler = BackgroundScheduler()
scheduler.add_job(func=clear_database, trigger="interval", minutes=10)
scheduler.start()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=3333)
