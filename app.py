from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Créer les dossiers nécessaires
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('data', exist_ok=True)

# Fichiers de données
PLAYERS_FILE = 'data/players.json'
BRACKET_FILE = 'data/bracket.json'
ADMIN_FILE = 'data/admin.json'

# Initialiser les fichiers JSON s'ils n'existent pas
def init_data_files():
    if not os.path.exists(PLAYERS_FILE):
        with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
    if not os.path.exists(BRACKET_FILE):
        with open(BRACKET_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'quarterfinals': [],
                'semifinals': [],
                'final': None,
                'winner': None
            }, f)
    if not os.path.exists(ADMIN_FILE):
        with open(ADMIN_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'username': 'admin',
                'password': generate_password_hash('admin123')  # Changez en production
            }, f)

init_data_files()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_players():
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_players(players):
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

def get_bracket():
    with open(BRACKET_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_bracket(bracket):
    with open(BRACKET_FILE, 'w', encoding='utf-8') as f:
        json.dump(bracket, f, ensure_ascii=False, indent=2)

def is_admin():
    return session.get('admin_logged_in', False)

def get_max_players():
    return 8

@app.route('/')
def index():
    players = get_players()
    registered_count = len([p for p in players if p.get('status') == 'validated'])
    max_players = get_max_players()
    is_full = registered_count >= max_players
    return render_template('index.html', 
                         registered_count=registered_count, 
                         max_players=max_players,
                         is_full=is_full)

@app.route('/register', methods=['GET', 'POST'])
def register():
    players = get_players()
    registered_count = len([p for p in players if p.get('status') == 'validated'])
    max_players = get_max_players()
    
    if registered_count >= max_players:
        flash('Le tournoi est complet ! Les inscriptions sont fermées.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        pseudo = request.form.get('pseudo', '').strip()
        contact = request.form.get('contact', '').strip()
        
        if not pseudo:
            flash('Le pseudo eFootball est obligatoire !', 'error')
            return render_template('register.html')
        
        # Vérifier si le pseudo existe déjà
        existing_pseudo = any(p.get('pseudo', '').lower() == pseudo.lower() for p in players)
        if existing_pseudo:
            flash('Ce pseudo est déjà inscrit !', 'error')
            return render_template('register.html')
        
        # Gérer l'upload du screenshot
        screenshot_filename = None
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                screenshot_filename = unique_filename
        
        # Créer le joueur
        new_player = {
            'id': str(uuid.uuid4()),
            'pseudo': pseudo,
            'contact': contact,
            'screenshot': screenshot_filename,
            'status': 'pending',  # pending, validated, rejected
            'registered_at': datetime.now().isoformat()
        }
        
        players.append(new_player)
        save_players(players)
        
        flash('Inscription enregistrée ! Votre paiement sera validé par l\'administrateur.', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/bracket')
def bracket():
    players = get_players()
    validated_players = [p for p in players if p.get('status') == 'validated']
    bracket_data = get_bracket()
    
    # Si on a 8 joueurs validés, générer le bracket automatiquement
    if len(validated_players) == 8 and not bracket_data.get('quarterfinals'):
        # Générer les matchs de quart de finale
        quarterfinals = []
        for i in range(0, 8, 2):
            quarterfinals.append({
                'player1': validated_players[i]['pseudo'],
                'player2': validated_players[i+1]['pseudo'],
                'score1': 0,
                'score2': 0,
                'winner': None
            })
        bracket_data['quarterfinals'] = quarterfinals
        save_bracket(bracket_data)
    
    return render_template('bracket.html', bracket=bracket_data, players=validated_players)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        with open(ADMIN_FILE, 'r', encoding='utf-8') as f:
            admin_data = json.load(f)
        
        if username == admin_data['username'] and check_password_hash(admin_data['password'], password):
            session['admin_logged_in'] = True
            flash('Connexion réussie !', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Identifiants incorrects !', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Déconnexion réussie !', 'success')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not is_admin():
        flash('Accès refusé. Veuillez vous connecter.', 'error')
        return redirect(url_for('admin_login'))
    
    players = get_players()
    bracket_data = get_bracket()
    validated_players = [p for p in players if p.get('status') == 'validated']
    pending_players = [p for p in players if p.get('status') == 'pending']
    
    return render_template('admin_dashboard.html', 
                         players=players, 
                         bracket=bracket_data,
                         validated_players=validated_players,
                         pending_count=len(pending_players))

@app.route('/admin/validate/<player_id>', methods=['POST'])
def validate_player(player_id):
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    players = get_players()
    player = next((p for p in players if p['id'] == player_id), None)
    
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    action = request.json.get('action')  # 'validate' or 'reject'
    
    if action == 'validate':
        # Vérifier qu'on n'a pas déjà 8 joueurs validés
        validated_count = len([p for p in players if p.get('status') == 'validated'])
        if validated_count >= get_max_players():
            return jsonify({'error': 'Le tournoi est complet (8 joueurs)'}), 400
        
        player['status'] = 'validated'
        flash(f'Joueur {player["pseudo"]} validé !', 'success')
    elif action == 'reject':
        player['status'] = 'rejected'
        flash(f'Joueur {player["pseudo"]} refusé.', 'info')
    
    save_players(players)
    
    # Si on atteint 8 joueurs validés, générer le bracket
    validated_players = [p for p in players if p.get('status') == 'validated']
    if len(validated_players) == 8:
        bracket_data = get_bracket()
        if not bracket_data.get('quarterfinals'):
            quarterfinals = []
            for i in range(0, 8, 2):
                quarterfinals.append({
                    'player1': validated_players[i]['pseudo'],
                    'player2': validated_players[i+1]['pseudo'],
                    'score1': 0,
                    'score2': 0,
                    'winner': None
                })
            bracket_data['quarterfinals'] = quarterfinals
            save_bracket(bracket_data)
    
    return jsonify({'success': True, 'status': player['status']})

@app.route('/admin/update-bracket', methods=['POST'])
def update_bracket():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    
    bracket_data = get_bracket()
    data = request.json
    
    # Mettre à jour les scores des quarts de finale (préserver les noms des joueurs)
    if 'quarterfinals' in data and bracket_data.get('quarterfinals'):
        for i, match_data in enumerate(data['quarterfinals']):
            if i < len(bracket_data['quarterfinals']):
                # Préserver les noms des joueurs existants
                bracket_data['quarterfinals'][i]['score1'] = match_data.get('score1', 0)
                bracket_data['quarterfinals'][i]['score2'] = match_data.get('score2', 0)
        
        # Déterminer les gagnants
        for match in bracket_data['quarterfinals']:
            if match.get('score1', 0) > match.get('score2', 0):
                match['winner'] = match['player1']
            elif match.get('score2', 0) > match.get('score1', 0):
                match['winner'] = match['player2']
            else:
                match['winner'] = None
        
        # Générer les demi-finales si tous les quarts sont terminés
        winners = [m['winner'] for m in bracket_data['quarterfinals'] if m.get('winner')]
        if len(winners) == 4 and not bracket_data.get('semifinals'):
            bracket_data['semifinals'] = [
                {'player1': winners[0], 'player2': winners[1], 'score1': 0, 'score2': 0, 'winner': None},
                {'player1': winners[2], 'player2': winners[3], 'score1': 0, 'score2': 0, 'winner': None}
            ]
    
    # Mettre à jour les demi-finales (préserver les noms des joueurs)
    if 'semifinals' in data and bracket_data.get('semifinals'):
        for i, match_data in enumerate(data['semifinals']):
            if i < len(bracket_data['semifinals']):
                # Préserver les noms des joueurs existants
                bracket_data['semifinals'][i]['score1'] = match_data.get('score1', 0)
                bracket_data['semifinals'][i]['score2'] = match_data.get('score2', 0)
        
        # Déterminer les gagnants
        for match in bracket_data['semifinals']:
            if match.get('score1', 0) > match.get('score2', 0):
                match['winner'] = match['player1']
            elif match.get('score2', 0) > match.get('score1', 0):
                match['winner'] = match['player2']
            else:
                match['winner'] = None
        
        # Générer la finale si les deux demi-finales sont terminées
        winners = [m['winner'] for m in bracket_data['semifinals'] if m.get('winner')]
        if len(winners) == 2 and not bracket_data.get('final'):
            bracket_data['final'] = {
                'player1': winners[0],
                'player2': winners[1],
                'score1': 0,
                'score2': 0,
                'winner': None
            }
    
    # Mettre à jour la finale (préserver les noms des joueurs)
    if 'final' in data and bracket_data.get('final'):
        bracket_data['final']['score1'] = data['final'].get('score1', 0)
        bracket_data['final']['score2'] = data['final'].get('score2', 0)
        
        if bracket_data['final'].get('score1', 0) > bracket_data['final'].get('score2', 0):
            bracket_data['final']['winner'] = bracket_data['final']['player1']
            bracket_data['winner'] = bracket_data['final']['player1']
        elif bracket_data['final'].get('score2', 0) > bracket_data['final'].get('score1', 0):
            bracket_data['final']['winner'] = bracket_data['final']['player2']
            bracket_data['winner'] = bracket_data['final']['player2']
        else:
            bracket_data['final']['winner'] = None
            bracket_data['winner'] = None
    
    save_bracket(bracket_data)
    return jsonify({'success': True, 'bracket': bracket_data})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)

