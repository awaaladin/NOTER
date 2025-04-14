from flask import Blueprint, render_template, request, flash, jsonify, redirect ,url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json


views = Blueprint('views', __name__, template_folder='templates')


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    # This should always run, regardless of request method
    q = request.args.get('q')
    notes_query = Note.query.filter_by(user_id=current_user.id)
    if q:
        notes_query = notes_query.filter(Note.data.ilike(f"%{q}%"))
    notes = notes_query.order_by(Note.date.desc()).all()

    return render_template("home.html", user=current_user, notes=notes)




@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            
    return jsonify({})



@views.route('/edit-note/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("Unauthorized.", category="error")
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        note.data = request.form.get('note')
        db.session.commit()
        flash("Note updated!", category="success")
        return redirect(url_for('views.home'))

    return render_template("edit_note.html", note=note, user=current_user)


@views.route('/search', methods=['GET'])
@login_required
def search_notes():
    query = request.args.get('q', '')
    if query:
        results = Note.query.filter(Note.user_id == current_user.id, Note.data.ilike(f'%{query}%')).all()
    else:
        results = Note.query.filter_by(user_id=current_user.id).all()

    return render_template('home.html', user=current_user, notes=results)


@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note_direct(note_id):
    note = Note.query.get_or_404(note_id)
    if note.user_id != current_user.id:
        flash("You are not authorized to delete this note.", category="error")
        return redirect(url_for('views.home'))

    db.session.delete(note)
    db.session.commit()
    flash("Note deleted.", category="success")
    return redirect(url_for('views.home'))

