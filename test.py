from flask import Flask,redirect,url_for,render_template, request
import random
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask("__main__")
#change directory
#UPLOAD_FOLDER = '/Users/tonywang/Desktop/Interface/FloodNet/static'
#app.config['IMAGE_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
selected_all_paths = []
#set maximum number of time an image shown in the web interface
max_shown = 3

class Image(db.Model):
    imageID = db.Column(db.String(255), primary_key=True)
    #how many times image has been selected
    status = db.Column(db.Integer, default=0)
    #how many times image has been retrieve
    count = db.Column(db.Integer, default=0)
    #status / count, click thorugh rate
    ctr = db.Column(db.Float, default=0.0)
    #reach_max maximum number of time an image shown in the web interface
    reach_max = db.Column(db.Boolean, default=False)
    



@app.before_first_request
def create_tables():
    #rewrite db every run 
    if os.path.exists('database.db'):
        os.remove('database.db')
    db.create_all()
#app.debug = True
@app.route("/")
def home():
    image_paths = get_random_images(9)
    global selected_all_paths
    selected_all_paths = image_paths
    print(image_paths)
    return render_template("randomImage.html", image_paths=image_paths)

def get_random_images(num_images):
    image_folder = 'static'
    image_files = os.listdir(image_folder)
    image_files = [file for file in image_files if not file.startswith('.DS_Store')]
    random.shuffle(image_files)
    selected_images = image_files[:num_images]
    image_paths = [os.path.join(image_folder, img_file) for img_file in selected_images]

    # Filter out image paths where reach_max is True
    image_paths = [path for path in image_paths if not Image.query.filter_by(imageID=path, reach_max=True).first()]

    return image_paths








@app.route("/update_status", methods=["POST"])
def update_status():
    selected_paths = request.form.getlist("image_paths")
    selected_images = [path.split("|")[1] for path in selected_paths]
    print(selected_images,"HERE!!!!!!!!")
    # Update the database with the image paths
    for path in selected_paths:
        image_path, image_id = path.split("|")
        image = Image.query.get(image_id)
        if image:
            image.status += 1
            print(f"Updated image {image.imageID} - New status: {image.status}")
        else:
            new_image = Image(imageID=image_id, status=1)
            db.session.add(new_image)
            print(f"Added new image {new_image.imageID} - Status: {new_image.status}")

    for path in selected_all_paths:
        image_id = path
        image = Image.query.get(image_id)
        if image:
            image.count += 1
            image.ctr = image.status / image.count  # Calculate CTR
            #set up reach_max (maximum number of time an image shown in the web interface)
            if image.count > max_shown:
                image.reach_max = True
            print(f"Updated image {image.imageID} - New count: {image.count}")
        else:
            new_image = Image(imageID=image_id, count=1)
            db.session.add(new_image)
            print(f"Added new image {new_image.imageID} - Count: {new_image.count}")

    db.session.commit()
    
    return redirect(url_for("home"))



@app.route("/<name>")
def user(name):
    return f"Hello {name}!"

@app.route("/home")
def test():
    return render_template("home.html")

@app.route("/image_folder_content")
def image_folder_content():
    image_folder = app.config['IMAGE_FOLDER']
    image_files = os.listdir(image_folder)
    return "<br>".join(image_files)

@app.route("/database")
def view_database():
    images = Image.query.all()
    return render_template("database.html", images=images)
@app.route("/admin")
def admin():
    return redirect(url_for("user", name = "dawei"))
if __name__ == "__main__":
    app.run(debug=True)