from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'notes.db'

# Create the database tables
def create_tables():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Create the notes table
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                audio TEXT,
                video TEXT,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
                )''')

    # Create the users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE
                )''')

    conn.commit()
    conn.close()

# API endpoint to create a note
@app.route('/notes', methods=['POST'])
def create_note():
    data = request.form
    title = data.get('title')
    content = data.get('content')
    audio = request.files.get('audio')
    video = request.files.get('video')
    user_id = data.get('user_id')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Insert the note into the database
    c.execute("INSERT INTO notes (title, content, audio, video, user_id) VALUES (?, ?, ?, ?, ?)",
              (title, content, audio.filename if audio else None, video.filename if video else None, user_id))
    note_id = c.lastrowid

    conn.commit()
    conn.close()

    return jsonify({'note_id': note_id}), 201

# API endpoint to get a note by ID
@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    # Retrieve the note from the database
    c.execute("SELECT * FROM notes WHERE id=?", (note_id,))
    note = c.fetchone()

    conn.close()

    if note:
        note_data = {
            'note_id': note[0],
            'title': note[1],
            'content': note[2],
            'audio': note[3],
            'video': note[4],
            'user_id': note[5]
        }
        return jsonify(note_data)
    else:
        return jsonify({'error': 'Note not found'}), 404

# API endpoint to query notes
@app.route('/notes', methods=['GET'])
def query_notes():
    user_id = request.args.get('user_id')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if user_id:
        # Filter notes by user ID
        c.execute("SELECT * FROM notes WHERE user_id=?", (user_id,))
    else:
        # Retrieve all notes
        c.execute("SELECT * FROM notes")

    notes = c.fetchall()

    conn.close()

    note_list = []
    for note in notes:
        note_data = {
            'note_id': note[0],
            'title': note[1],
            'content': note[2],
            'audio': note[3],
            'video': note[4],
            'user_id': note[5]
        }
        note_list.append(note_data)

    return jsonify(note_list)

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
