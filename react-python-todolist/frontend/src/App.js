import { useState, useEffect, useCallback } from "react";
import {
    Button,
    TextField,
    Card,
    CardMedia,
    CardContent,
    Checkbox,
    Typography,
} from "@mui/material";
import { useDropzone } from "react-dropzone";

function App() {
    const [todos, setTodos] = useState([]);
    const [newTask, setNewTask] = useState("");
    const [imageFile, setImageFile] = useState(null);
    const [preview, setPreview] = useState(null);

    // Load todos
    useEffect(() => {
        fetch("http://127.0.0.1:5000/api/todos")
            .then((res) => res.json())
            .then(setTodos);
    }, []);

    // --- Dropzone Setup ---
    const onDrop = useCallback((acceptedFiles) => {
        const file = acceptedFiles[0];
        setImageFile(file);
        setPreview(URL.createObjectURL(file));
    }, []);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: { "image/*": [] },
    });

    // --- CRUD Handlers ---
    const addTodo = async () => {
        if (!newTask.trim()) return;

        const formData = new FormData();
        formData.append("task", newTask);
        if (imageFile) formData.append("image", imageFile);

        const res = await fetch("http://127.0.0.1:5000/api/todos", {
            method: "POST",
            body: formData,
        });

        const data = await res.json();
        setTodos([...todos, data]);
        setNewTask("");
        setImageFile(null);
        setPreview(null);
    };

    const deleteTodo = async (id) => {
        await fetch(`http://127.0.0.1:5000/api/todos/${id}`, {
            method: "DELETE",
        });
        setTodos(todos.filter((t) => t.id !== id));
    };

    const toggleComplete = async (id, completed) => {
        const res = await fetch(`http://127.0.0.1:5000/api/todos/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ completed: !completed }),
        });
        const updated = await res.json();
        setTodos(todos.map((t) => (t.id === id ? updated : t)));
    };

    return (
        <div style={{ padding: "2rem" }}>
            <Typography variant="h4" gutterBottom>
                🧠 To-Do List with Image Upload
            </Typography>

            {/* Input Section */}
            <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <TextField
                    label="New Task"
                    variant="outlined"
                    value={newTask}
                    onChange={(e) => setNewTask(e.target.value)}
                    style={{ flexGrow: 1 }}
                />

                <div
                    {...getRootProps()}
                    style={{
                        border: "2px dashed gray",
                        padding: "0.5rem 1rem",
                        borderRadius: "10px",
                        cursor: "pointer",
                    }}
                >
                    <input {...getInputProps()} />
                    {isDragActive ? (
                        <p>Drop image here…</p>
                    ) : (
                        <p>{imageFile ? "✅ Image ready" : "📁 Drag or click image"}</p>
                    )}
                </div>

                <Button variant="contained" onClick={addTodo}>
                    Add
                </Button>
            </div>

            {/* Image Preview */}
            {preview && (
                <div style={{ marginTop: "1rem" }}>
                    <Typography variant="subtitle1">Preview:</Typography>
                    <img
                        src={preview}
                        alt="Preview"
                        style={{
                            maxWidth: "200px",
                            maxHeight: "200px",
                            borderRadius: "10px",
                            marginTop: "0.5rem",
                        }}
                    />
                </div>
            )}

            {/* Todo List */}
            <div
                style={{
                    marginTop: "2rem",
                    display: "grid",
                    gap: "1.5rem",
                    gridTemplateColumns: "repeat(auto-fit, minmax(300px, 350px))",
                }}
            >
                {todos.map((t) => (
                    <Card key={t.id} style={{ maxWidth: 350, margin: "0 auto" }}>
                        {t.thumbnail_url && (
                            <CardMedia
                                component="img"
                                height="200"
                                image={t.thumbnail_url}
                                alt={t.task}
                                sx={{ objectFit: "cover" }}
                            />
                        )}
                        <CardContent>
                            <Checkbox
                                checked={t.completed}
                                onChange={() => toggleComplete(t.id, t.completed)}
                            />
                            <Typography
                                variant="body1"
                                style={{
                                    textDecoration: t.completed ? "line-through" : "none",
                                    display: "inline-block",
                                }}
                            >
                                {t.task}
                            </Typography>
                            {t.image_url && (
                                <Button
                                    href={t.image_url}
                                    target="_blank"
                                    size="small"
                                    sx={{ mt: 1 }}
                                >
                                    View Full Image
                                </Button>
                            )}
                            <Button
                                size="small"
                                color="error"
                                onClick={() => deleteTodo(t.id)}
                                style={{ float: "right" }}
                            >
                                ❌
                            </Button>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}

export default App;
