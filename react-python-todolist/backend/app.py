from cloudinary.api import transformation
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import cv2
import cloudinary
import cloudinary.uploader

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# app.config["UPLOAD_FOLDER"] = "uploads"
# os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# Model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    public_id = db.Column(db.String(200))

    def to_dict(self):
        return {
            "id": self.id,
            "task": self.task,
            "completed": self.completed,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
        }


with app.app_context():
    db.create_all()


# --- CRUD ROUTES ---
@app.route("/api/todos", methods=["GET"])
def get_todos():
    todos = Todo.query.all()
    return jsonify([t.to_dict() for t in todos])


@app.route("/api/todos", methods=["POST"])
def add_todo():
    task = request.form.get("task")
    image = request.files.get("image")

    image_url = None
    thumbnail_url = None
    public_id = None

    if image:
        '''
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(image_path)
            # Example: OpenCV grayscale conversion
            img = cv2.imread(image_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(image_path, gray)
        '''
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            image,
            folder="todo_images",
            transformation=[{"width": 800, "height": 800, "crop": "limit"}]     # auto resize large images
        )
        image_url = upload_result.get("secure_url")
        public_id = upload_result.get("public_id")
        # Generate thumbnail (200px wide)
        thumbnail_url = cloudinary.CloudinaryImage(upload_result["public_id"]).build_url(width=200, height=200, crop="fill")

    todo = Todo(task=task, image_url=image_url, thumbnail_url=thumbnail_url, public_id=public_id)
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@app.route("/api/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    data = request.get_json()
    todo.task = data.get("task", todo.task)
    todo.completed = data.get("completed", todo.completed)
    db.session.commit()
    return jsonify(todo.to_dict()), 200


@app.route("/api/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({"error": "Todo not found"}), 404

    '''
        if todo.image_path and os.path.exists(todo.image_path):
        os.remove(todo.image_path)
    '''
    # Delete from Cloudinary (if image exists)
    if todo.public_id:
        try:
            cloudinary.uploader.destroy(todo.public_id)
        except Exception as e:
            print(f"Failed to delete image from Cloudinary: {e}")

    db.session.delete(todo)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@app.route("/uploads/<path:filename>")
def get_uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
