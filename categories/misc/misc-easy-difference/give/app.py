from flask import Flask, render_template, request, redirect, url_for, flash
import os
import random

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

unique_images = [
    {"id": 1, "src": "static/images/image1.jpg"},
    {"id": 2, "src": "static/images/image2.jpg"},
    {"id": 3, "src": "static/images/image3.jpg"},
    {"id": 4, "src": "static/images/image4.jpg"},
    {"id": 5, "src": "static/images/image5.jpg"},
    {"id": 6, "src": "static/images/image6.jpg"},
    {"id": 7, "src": "static/images/image7.jpg"},
    {"id": 8, "src": "static/images/image8.jpg"},
    {"id": 9, "src": "static/images/image9.jpg"},
]

all_images = unique_images * 5


@app.route("/")
def index():
    random.shuffle(all_images)
    return render_template("index.html", images=all_images)


@app.route("/submit", methods=["POST"])
def submit():
    selected = request.form.getlist("image")
    print(selected)

    if len(selected) != 10:
        flash("Please select 10 images.", "error")
        return redirect(url_for("index"))

    try:
        selected_numbers = [float(num) for num in selected]
    except ValueError:
        flash("incorrect input", "error")
        return redirect(url_for("index"))

    if len(set(selected_numbers)) != 10:
        flash("All selected images should be unique.", "error")
        return redirect(url_for("index"))

    for num in selected_numbers:
        if (num > 9) or (num < 1):
            flash("Please select images from the arrived.", "error")
            return redirect(url_for("index"))

    try:
        with open("flag.txt", "r") as file:
            flag = file.read().strip()
    except FileNotFoundError:
        flash("Flag not found.", "error")
        return redirect(url_for("index"))
    print(flag)
    flash(f"Congratulations! Put your flag: {flag}", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7331)
