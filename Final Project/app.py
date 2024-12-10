from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
#import pyttsx3
from PIL import Image, ImageDraw, ImageFont
import datetime
from sklearn.neighbors import NearestNeighbors
import pandas as pd
import os, re, json, pygame
from openai import OpenAI
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
client = OpenAI(api_key=config.OPENAI_API_KEY)

# Initialize pygame mixer
pygame.mixer.init()
is_playing = False  # Variable to keep track of the play/pause state
current_audio_page = 0
current_audio = ''

from werkzeug.utils import secure_filename

# Directory to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    history = db.relationship('UserHistory', backref='user', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    genre = db.Column(db.String(50))
    content = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)  # New field to track if the book is read

# Edit book route
@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.genre = request.form.get('genre', 'Unknown')
        book.content = request.form['content']

        db.session.commit()
        #flash("Book updated successfully!", "success")
        return redirect(url_for('home'))
    
    return render_template('edit_book.html', book=book)

# Delete book route
@app.route('/delete_book/<int:book_id>', methods=['GET'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    #flash("Book deleted successfully!", "danger")
    return redirect(url_for('home'))

@app.route('/mark_as_read/<int:book_id>', methods=['POST'])
def mark_as_read(book_id):
    book = Book.query.get_or_404(book_id)
    book.read = True  # Mark the book as read
    db.session.commit()
    #flash(f"{book.title} marked as read.", "success")
    return redirect(url_for('home'))

class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    date_read = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    rating = db.Column(db.Integer)
    book = db.relationship('Book', backref='history')

# Route to play or pause the music
@app.route('/control', methods=['POST'])
def control_music():
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False
    else:
        pygame.mixer.music.unpause() if pygame.mixer.music.get_busy() else pygame.mixer.music.play()
        is_playing = True
    return "OK"

# Routes
@app.route('/')
def home():
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    books = Book.query.filter_by(read=False).all()  # Show only unread books
    return render_template('index.html', books=books)

@app.route('/read/<int:book_id>', methods=['GET'])
def read_book(book_id):
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    book = Book.query.get_or_404(book_id)
    
    # Split content into pages of approximately 200-300 words while preserving new lines
    words = book.content.split(' ')
    page_size = 250  # Adjust for desired word count per page (200-300 words)
    pages = []
    
    current_page = ""
    word_count = 0

    for word in words:
        current_page += word + " "
        word_count += 1
        if word_count >= page_size:
            pages.append(current_page.strip())
            current_page = ""
            word_count = 0

    # Add remaining content as the last page
    if current_page:
        pages.append(current_page.strip())

    # Get mp3 pages of book
    audio_file = f'audio/{book_id}_0.mp3'
    if not os.path.exists(audio_file):
        page_num = 0
        for page in pages:
            with client.audio.speech.with_streaming_response.create(
                model="tts-1",
                voice="nova",
                input=page
            ) as response:
                response.stream_to_file(f'audio/{book_id}_{page_num}.mp3')
            page_num += 1

    pygame.mixer.music.load(audio_file)
    global current_audio_page, current_audio
    current_audio_page = 0
    current_audio = book_id

    return render_template('read.html', book=book, pages=pages)

# Route to play next page audio
@app.route('/next', methods=['POST'])
def next_track():
    global current_audio_page, current_audio, is_playing
    current_audio_page += 1
    pygame.mixer.music.load(f'audio/{current_audio}_{current_audio_page}.mp3')
    if is_playing:
        pygame.mixer.music.play()
    return "OK"

# Route to play previous page audio
@app.route('/previous', methods=['POST'])
def previous_track():
    global current_audio_page, current_audio, is_playing
    current_audio_page -= 1
    pygame.mixer.music.load(f'audio/{current_audio}_{current_audio_page}.mp3')
    if is_playing:
        pygame.mixer.music.play()
    return "OK"

@app.route('/generate_image', methods=['POST'])
def generate_image():
    """Endpoint to generate an image based on page text."""
    data = request.json
    page_text = data.get('page_text', '')

    # Use OpenAI to write an image description for Dall-E
    prompt = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an image prompt generator that picks the most important details from a page from a book and turns it into an image prompt for Dall-E. \
             Make it concise and format it so Dall-E can understand what image you want it to generate \
             The new page may start halfway through a sentence, so try your best to interpret the remaining information to use in your answer \
             In your output, specify for Dall-E to not include text in the image"},
            {
                "role": "user",
                "content": "Input book page: " + page_text,
            },
        ]
    )
    print(prompt.choices[0].message.content)

    # Generate the DALL-E image based on the page text
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt.choices[0].message.content,
        n=1,
        size="1024x1024",
        quality="standard",
    )
    image_url = response.data[0].url  # Return the URL of the generated image    
    print(image_url)
    return jsonify({'image_url': image_url})

@app.route('/history', methods=['GET', 'POST'])
def history():
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    query = Book.query.filter_by(read=True)  # Only show books marked as read

    # Get filter parameters
    author = request.args.get('author')
    genre = request.args.get('genre')
    date_read = request.args.get('date')
    search_query = request.form.get('query')  # Single search field for both title and author

    # Apply filters if provided
    if author:
        query = query.filter(Book.author.contains(author))
    if genre:
        query = query.filter(Book.genre.contains(genre))
    if date_read:
        # Assuming a date_read field in the Book model or UserHistory model
        query = query.filter(Book.date_read == date_read)
    if search_query:
        query = query.filter((Book.title.contains(search_query)) | (Book.author.contains(search_query)))

    # Execute the query
    history_books = query.order_by(Book.id.desc()).all()
    return render_template('history.html', history=history_books)

@app.route('/search_history', methods=['POST'])
def search_history():
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    title = request.form.get('title')
    author = request.form.get('author')
    
    query = UserHistory.query.join(Book)
    if title:
        query = query.filter(Book.title.contains(title))
    if author:
        query = query.filter(Book.author.contains(author))
    
    history = query.order_by(desc(UserHistory.date_read)).all()
    return render_template('history.html', history=history)

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False

    if request.method == 'POST':
        user_input = request.form.get('description')
        # Process user input and generate book recommendations (this is a placeholder)
        recommendations = get_recommendations_based_on_input(user_input)
    else:
        recommendations = get_recommendations_based_on_history()
    
    return render_template('recommendations.html', recommendations=recommendations)

# Recommendation functions
def get_recommendations_based_on_history():
    # Get history
    read_books = Book.query.filter_by(read=True).all()
        
    # Check if there are any read books
    if not read_books: return []
    # Transform read books into string
    read_books_str = ''
    for book in read_books:
        read_books_str += book.title + ' by ' + book.author + ', '

    # Get suggestions
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that has a lot of knowledge about books. \
             When you are given a list of books the reader has read, provide up to 10 book suggestions that the reader may like based on their read books. \
             Return the result as a python array of up to 10 dicts with the book title and author. \
             For example, if the reader read Harry Potter and the Sorcerer's Stone, return [{'title': 'Percy Jackson and the Olympians','author':'Rick Riordan'}]"},
            {
                "role": "user",
                "content": "User read history: " + read_books_str,
            },
        ]
    )

    # Convert suggestions
    rec_list = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a string to python list of dicts converter. \
             When you are given a list of books as a string, convert them to a list of dictionary objects in python. \
             For example, '1. Title: The Tell-Tale Heart \nAuthor: Edgar Allan Poe' becomes [{'Title': 'The Tell-Tale Heart','Author':'Edgar Allan Poe'}]"},
            {
                "role": "user",
                "content": response.choices[0].message.content,
            },
        ]
    )
    rec_list = '[' + rec_list.choices[0].message.content.split('[', 1)[1] 

    print(response.choices[0].message.content)
    print('\n')
    print(str(eval(rec_list)))
    return eval(rec_list)

def get_recommendations_based_on_input(input_description):
    # Placeholder function for NLP processing of user input
    return ["Book A", "Book B", "Book C"]

@app.route('/import_book_page')
def import_book_page():
    # Pause any audio
    global is_playing
    if is_playing:
        pygame.mixer.music.pause()
        is_playing = False
    return render_template('import_book.html')

@app.route('/import_book', methods=['POST'])
def import_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form.get('genre', 'Unknown')
    
    file = request.files['file']
    if file and file.filename.endswith('.txt'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        with open(file_path, 'r') as f:
            content = f.read()
        
        new_book = Book(title=title, author=author, genre=genre, content=content)
        db.session.add(new_book)
        db.session.commit()
        
        return redirect(url_for('home'))
    else:
        return "Only .txt files are allowed", 400
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Creates tables
    #db.create_all()  
    app.run(debug=True)
