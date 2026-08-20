#!/usr/bin/env python3
"""
Cadastro de Eleitores - Sistema de cadastro online
Funciona em computador e celular (design responsivo)
Com autenticação de usuário (login/senha)
"""

import os
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import (Flask, render_template, request, jsonify,
                   redirect, url_for, session, flash)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
DATABASE = os.environ.get('DATABASE_URL', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eleitores.db'))


# ─── Banco de Dados ───────────────────────────────────────────

def get_db():
    """Conecta ao banco SQLite"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria as tabelas se não existirem"""
    conn = get_db()

    # Tabela de usuários
    conn.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de eleitores
    conn.execute('''
        CREATE TABLE IF NOT EXISTS eleitores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo_eleitoral TEXT NOT NULL UNIQUE,
            nome_completo TEXT NOT NULL,
            cpf TEXT,
            data_nascimento TEXT,
            sexo TEXT,
            telefone TEXT,
            email TEXT,
            cep TEXT,
            logradouro TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            zona_eleitoral TEXT,
            secao_eleitoral TEXT,
            observacoes TEXT,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (created_by) REFERENCES usuarios(id)
        )
    ''')
    conn.commit()
    conn.close()


# ─── Autenticação ─────────────────────────────────────────────

def hash_senha(senha):
    """Gera hash da senha com salt"""
    import hashlib
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt.encode(), 100000)
    return f"{salt}:{h.hex()}"


def verificar_senha(senha, hash_completo):
    """Verifica se a senha confere com o hash"""
    import hashlib
    salt, h = hash_completo.split(':')
    h_check = hashlib.pbkdf2_hmac('sha256', senha.encode(), salt.encode(), 100000)
    return h_check.hex() == h


def login_required(f):
    """Decorator que exige login"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'erro': 'Acesso negado. Faça login.'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def get_usuario_logado():
    """Retorna dados do usuário logado"""
    if 'usuario_id' not in session:
        return None
    conn = get_db()
    user = conn.execute(
        'SELECT id, nome, email FROM usuarios WHERE id = ?',
        (session['usuario_id'],)
    ).fetchone()
    conn.close()
    return dict(user) if user else None


# ─── Rotas de Auth ────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        if not email or not senha:
            flash('Preencha e-mail e senha', 'error')
            return render_template('login.html')

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM usuarios WHERE email = ?', (email,)
        ).fetchone()
        conn.close()

        if user and verificar_senha(senha, user['senha_hash']):
            session['usuario_id'] = user['id']
            session['usuario_nome'] = user['nome']
            session['usuario_email'] = user['email']
            return redirect(url_for('index'))
        else:
            flash('E-mail ou senha incorretos', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/registro', methods=['GET', 'POST'])
def registro():
    """Página de registro"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmar = request.form.get('confirmar_senha', '')

        if not nome or not email or not senha:
            flash('Preencha todos os campos', 'error')
            return render_template('registro.html')

        if len(senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres', 'error')
            return render_template('registro.html')

        if senha != confirmar:
            flash('As senhas não conferem', 'error')
            return render_template('registro.html')

        conn = get_db()
        try:
            conn.execute(
                'INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)',
                (nome, email, hash_senha(senha))
            )
            conn.commit()

            # Login automático após registro
            user = conn.execute(
                'SELECT * FROM usuarios WHERE email = ?', (email,)
            ).fetchone()
            conn.close()

            session['usuario_id'] = user['id']
            session['usuario_nome'] = user['nome']
            session['usuario_email'] = user['email']

            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            conn.close()
            flash('Este e-mail já está cadastrado', 'error')
            return render_template('registro.html')

    return render_template('registro.html')


@app.route('/logout')
def logout():
    """Encerrar sessão"""
    session.clear()
    flash('Sessão encerrada', 'info')
    return redirect(url_for('login'))


# ─── Perfil do Usuário ────────────────────────────────────────

@app.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Página de perfil do usuário"""
    conn = get_db()
    usuario = conn.execute(
        'SELECT id, nome, email, created_at FROM usuarios WHERE id = ?',
        (session['usuario_id'],)
    ).fetchone()

    # Estatísticas do usuário
    stats = conn.execute(
        'SELECT COUNT(*) as total FROM eleitores WHERE created_by = ?',
        (session['usuario_id'],)
    ).fetchone()
    conn.close()

    if request.method == 'POST':
        acao = request.form.get('acao', '')

        if acao == 'atualizar_perfil':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()

            if not nome or not email:
                flash('Nome e e-mail são obrigatórios', 'error')
                return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))

            conn = get_db()
            try:
                conn.execute(
                    'UPDATE usuarios SET nome = ?, email = ? WHERE id = ?',
                    (nome, email, session['usuario_id'])
                )
                conn.commit()
                session['usuario_nome'] = nome
                session['usuario_email'] = email
                flash('Perfil atualizado com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash('Este e-mail já está em uso por outra conta', 'error')
            finally:
                conn.close()

            # Recarregar dados
            conn = get_db()
            usuario = conn.execute(
                'SELECT id, nome, email, created_at FROM usuarios WHERE id = ?',
                (session['usuario_id'],)
            ).fetchone()
            conn.close()

        elif acao == 'alterar_senha':
            senha_atual = request.form.get('senha_atual', '')
            nova_senha = request.form.get('nova_senha', '')
            confirmar = request.form.get('confirmar_senha', '')

            if not senha_atual or not nova_senha:
                flash('Preencha todos os campos de senha', 'error')
                return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))

            if len(nova_senha) < 6:
                flash('A nova senha deve ter no mínimo 6 caracteres', 'error')
                return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))

            if nova_senha != confirmar:
                flash('As senhas não conferem', 'error')
                return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))

            conn = get_db()
            user = conn.execute(
                'SELECT senha_hash FROM usuarios WHERE id = ?',
                (session['usuario_id'],)
            ).fetchone()
            conn.close()

            if not verificar_senha(senha_atual, user['senha_hash']):
                flash('Senha atual incorreta', 'error')
                return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))

            conn = get_db()
            conn.execute(
                'UPDATE usuarios SET senha_hash = ? WHERE id = ?',
                (hash_senha(nova_senha), session['usuario_id'])
            )
            conn.commit()
            conn.close()

            flash('Senha alterada com sucesso!', 'success')

    return render_template('perfil.html', usuario=dict(usuario), stats=dict(stats))


@app.route('/api/usuario/perfil', methods=['GET'])
@login_required
def api_perfil():
    """API: dados do perfil"""
    conn = get_db()
    user = conn.execute(
        'SELECT id, nome, email, created_at FROM usuarios WHERE id = ?',
        (session['usuario_id'],)
    ).fetchone()
    stats = conn.execute(
        'SELECT COUNT(*) as total FROM eleitores WHERE created_by = ?',
        (session['usuario_id'],)
    ).fetchone()
    conn.close()
    return jsonify({
        'id': user['id'],
        'nome': user['nome'],
        'email': user['email'],
        'created_at': user['created_at'],
        'eleitores_cadastrados': stats['total']
    })


# ─── Rotas Principais ─────────────────────────────────────────

@app.route('/')
@login_required
def index():
    """Página principal"""
    conn = get_db()
    eleitores = conn.execute(
        '''SELECT e.*, u.nome as criado_por_nome
           FROM eleitores e
           LEFT JOIN usuarios u ON e.created_by = u.id
           ORDER BY e.nome_completo ASC'''
    ).fetchall()
    total = len(eleitores)
    conn.close()
    return render_template('index.html',
                           eleitores=eleitores,
                           total=total,
                           usuario=get_usuario_logado())


# ─── API Eleitores (protegida) ────────────────────────────────

@app.route('/api/eleitores', methods=['GET'])
@login_required
def api_listar():
    """API: listar todos os eleitores"""
    busca = request.args.get('busca', '').strip()
    conn = get_db()

    if busca:
        eleitores = conn.execute(
            '''SELECT e.*, u.nome as criado_por_nome
               FROM eleitores e
               LEFT JOIN usuarios u ON e.created_by = u.id
               WHERE e.nome_completo LIKE ?
                  OR e.titulo_eleitoral LIKE ?
                  OR e.cpf LIKE ?
                  OR e.cidade LIKE ?
               ORDER BY e.nome_completo ASC''',
            (f'%{busca}%', f'%{busca}%', f'%{busca}%', f'%{busca}%')
        ).fetchall()
    else:
        eleitores = conn.execute(
            '''SELECT e.*, u.nome as criado_por_nome
               FROM eleitores e
               LEFT JOIN usuarios u ON e.created_by = u.id
               ORDER BY e.nome_completo ASC'''
        ).fetchall()

    conn.close()
    return jsonify([dict(e) for e in eleitores])


@app.route('/api/eleitores', methods=['POST'])
@login_required
def api_cadastrar():
    """API: cadastrar novo eleitor"""
    data = request.get_json()

    if not data.get('titulo_eleitoral') or not data.get('nome_completo'):
        return jsonify({'erro': 'Título eleitoral e nome são obrigatórios'}), 400

    conn = get_db()
    try:
        conn.execute('''
            INSERT INTO eleitores (
                titulo_eleitoral, nome_completo, cpf, data_nascimento,
                sexo, telefone, email, cep, logradouro, numero,
                complemento, bairro, cidade, estado,
                zona_eleitoral, secao_eleitoral, observacoes, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('titulo_eleitoral', '').strip(),
            data.get('nome_completo', '').strip(),
            data.get('cpf', '').strip(),
            data.get('data_nascimento', '').strip(),
            data.get('sexo', '').strip(),
            data.get('telefone', '').strip(),
            data.get('email', '').strip(),
            data.get('cep', '').strip(),
            data.get('logradouro', '').strip(),
            data.get('numero', '').strip(),
            data.get('complemento', '').strip(),
            data.get('bairro', '').strip(),
            data.get('cidade', '').strip(),
            data.get('estado', '').strip(),
            data.get('zona_eleitoral', '').strip(),
            data.get('secao_eleitoral', '').strip(),
            data.get('observacoes', '').strip(),
            session.get('usuario_id'),
        ))
        conn.commit()
        return jsonify({'sucesso': True, 'mensagem': 'Eleitor cadastrado com sucesso!'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'erro': 'Este título eleitoral já está cadastrado'}), 409
    finally:
        conn.close()


@app.route('/api/eleitores/<int:id>', methods=['GET'])
@login_required
def api_consultar(id):
    """API: consultar um eleitor"""
    conn = get_db()
    eleitor = conn.execute(
        '''SELECT e.*, u.nome as criado_por_nome
           FROM eleitores e
           LEFT JOIN usuarios u ON e.created_by = u.id
           WHERE e.id = ?''', (id,)
    ).fetchone()
    conn.close()
    if eleitor:
        return jsonify(dict(eleitor))
    return jsonify({'erro': 'Eleitor não encontrado'}), 404


@app.route('/api/eleitores/<int:id>', methods=['PUT'])
@login_required
def api_atualizar(id):
    """API: atualizar eleitor"""
    data = request.get_json()
    conn = get_db()

    eleitor = conn.execute('SELECT * FROM eleitores WHERE id = ?', (id,)).fetchone()
    if not eleitor:
        conn.close()
        return jsonify({'erro': 'Eleitor não encontrado'}), 404

    conn.execute('''
        UPDATE eleitores SET
            titulo_eleitoral = ?, nome_completo = ?, cpf = ?,
            data_nascimento = ?, sexo = ?, telefone = ?, email = ?,
            cep = ?, logradouro = ?, numero = ?, complemento = ?,
            bairro = ?, cidade = ?, estado = ?,
            zona_eleitoral = ?, secao_eleitoral = ?, observacoes = ?,
            updated_at = ?
        WHERE id = ?
    ''', (
        data.get('titulo_eleitoral', '').strip(),
        data.get('nome_completo', '').strip(),
        data.get('cpf', '').strip(),
        data.get('data_nascimento', '').strip(),
        data.get('sexo', '').strip(),
        data.get('telefone', '').strip(),
        data.get('email', '').strip(),
        data.get('cep', '').strip(),
        data.get('logradouro', '').strip(),
        data.get('numero', '').strip(),
        data.get('complemento', '').strip(),
        data.get('bairro', '').strip(),
        data.get('cidade', '').strip(),
        data.get('estado', '').strip(),
        data.get('zona_eleitoral', '').strip(),
        data.get('secao_eleitoral', '').strip(),
        data.get('observacoes', '').strip(),
        datetime.now().isoformat(),
        id
    ))
    conn.commit()
    conn.close()
    return jsonify({'sucesso': True, 'mensagem': 'Eleitor atualizado com sucesso!'})


@app.route('/api/eleitores/<int:id>', methods=['DELETE'])
@login_required
def api_excluir(id):
    """API: excluir eleitor"""
    conn = get_db()
    eleitor = conn.execute('SELECT * FROM eleitores WHERE id = ?', (id,)).fetchone()
    if not eleitor:
        conn.close()
        return jsonify({'erro': 'Eleitor não encontrado'}), 404

    conn.execute('DELETE FROM eleitores WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'sucesso': True, 'mensagem': 'Eleitor excluído com sucesso!'})


@app.route('/api/stats', methods=['GET'])
@login_required
def api_stats():
    """API: estatísticas"""
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) as c FROM eleitores').fetchone()['c']
    por_estado = conn.execute(
        'SELECT estado, COUNT(*) as c FROM eleitores WHERE estado != "" GROUP BY estado ORDER BY c DESC'
    ).fetchall()
    por_usuario = conn.execute(
        '''SELECT u.nome, COUNT(e.id) as c
           FROM eleitores e
           JOIN usuarios u ON e.created_by = u.id
           GROUP BY e.created_by ORDER BY c DESC'''
    ).fetchall()
    conn.close()
    return jsonify({
        'total': total,
        'por_estado': [{'estado': e['estado'], 'count': e['c']} for e in por_estado],
        'por_usuario': [{'nome': u['nome'], 'count': u['c']} for u in por_usuario]
    })


# ─── Iniciar ──────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("  CADASTRO DE ELEITORES")
    print(f"  Acesse: http://localhost:{port}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=port, debug=True)
else:
    # Para produção (gunicorn)
    init_db()
