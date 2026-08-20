/**
 * Cadastro de Eleitores - Frontend
 */

const API = '/api/eleitores';
let debounceTimer = null;

// ─── Inicialização ────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    carregarEleitores();
});

// ─── Carregar Eleitores ───────────────────────────────────

async function carregarEleitores(busca = '') {
    try {
        const url = busca ? `${API}?busca=${encodeURIComponent(busca)}` : API;
        const resp = await fetch(url);

        if (resp.status === 401) {
            window.location.href = '/login';
            return;
        }

        const eleitores = await resp.json();

        renderizarTabela(eleitores);
        renderizarCards(eleitores);
        document.getElementById('total-count').textContent = eleitores.length;

        const empty = document.getElementById('empty-state');
        empty.style.display = eleitores.length === 0 ? 'block' : 'none';
    } catch (err) {
        toast('Erro ao carregar eleitores', 'error');
    }
}

// ─── Busca com Debounce ───────────────────────────────────

function buscarEleitores() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        const busca = document.getElementById('busca').value;
        carregarEleitores(busca);
    }, 300);
}

// ─── Renderizar Tabela (Desktop) ──────────────────────────

function renderizarTabela(eleitores) {
    const tbody = document.getElementById('tabela-eleitores');
    tbody.innerHTML = eleitores.map(e => `
        <tr>
            <td><strong>${e.numero_titulo || e.titulo_eleitoral}</strong></td>
            <td>${e.nome_completo}</td>
            <td>${e.cidade ? e.cidade + '/' + (e.estado || '') : '-'}</td>
            <td>${e.zona_eleitoral && e.secao_eleitoral ? e.zona_eleitoral + ' / ' + e.secao_eleitoral : '-'}</td>
            <td>${e.telefone || '-'}</td>
            <td>${e.criado_por_nome || '-'}</td>
            <td>
                <div class="actions">
                    <button class="btn btn-sm btn-primary" onclick="editarEleitor(${e.id})" title="Editar">✏️</button>
                    <button class="btn btn-sm btn-danger" onclick="confirmarExcluir(${e.id}, '${e.nome_completo.replace(/'/g, "\\'")}')" title="Excluir">🗑️</button>
                </div>
            </td>
        </tr>
    `).join('');
}

// ─── Renderizar Cards (Mobile) ────────────────────────────

function renderizarCards(eleitores) {
    const container = document.getElementById('cards-eleitores');
    container.innerHTML = eleitores.map(e => `
        <div class="eleitor-card">
            <div class="card-name">${e.nome_completo}</div>
            <div class="card-info">
                <div><span class="label">Nº Título:</span> ${e.numero_titulo || e.titulo_eleitoral}</div>
                <div><span class="label">Cidade:</span> ${e.cidade ? e.cidade + '/' + (e.estado || '') : '-'}</div>
                <div><span class="label">Zona/Seção:</span> ${e.zona_eleitoral && e.secao_eleitoral ? e.zona_eleitoral + ' / ' + e.secao_eleitoral : '-'}</div>
                <div><span class="label">Telefone:</span> ${e.telefone || '-'}</div>
                <div><span class="label">Bairro:</span> ${e.bairro || '-'}</div>
                <div><span class="label">Logradouro:</span> ${e.logradouro ? e.logradouro + ', ' + (e.numero || 'S/N') : '-'}</div>
                <div><span class="label">Email:</span> ${e.email || '-'}</div>
                <div><span class="label">Cadastrado por:</span> ${e.criado_por_nome || '-'}</div>
            </div>
            <div class="card-actions">
                <button class="btn btn-sm btn-primary" onclick="editarEleitor(${e.id})" style="flex:1;">✏️ Editar</button>
                <button class="btn btn-sm btn-danger" onclick="confirmarExcluir(${e.id}, '${e.nome_completo.replace(/'/g, "\\'")}')" style="flex:1;">🗑️ Excluir</button>
            </div>
        </div>
    `).join('');
}

// ─── Modal Cadastro/Edição ────────────────────────────────

function abrirModalCadastro() {
    document.getElementById('modal-title').textContent = 'Novo Eleitor';
    document.getElementById('edit-id').value = '';
    document.getElementById('form-eleitor').reset();
    document.getElementById('modal-form').classList.add('active');
}

function fecharModal() {
    document.getElementById('modal-form').classList.remove('active');
}

async function editarEleitor(id) {
    try {
        const resp = await fetch(`${API}/${id}`);
        const e = await resp.json();

        document.getElementById('modal-title').textContent = 'Editar Eleitor';
        document.getElementById('edit-id').value = e.id;

        // Preencher campos
        document.getElementById('numero_titulo').value = e.numero_titulo || e.titulo_eleitoral || '';
        document.getElementById('nome_completo').value = e.nome_completo || '';
        document.getElementById('data_nascimento').value = e.data_nascimento || '';
        document.getElementById('sexo').value = e.sexo || '';
        document.getElementById('telefone').value = e.telefone || '';
        document.getElementById('email').value = e.email || '';
        document.getElementById('cep').value = e.cep || '';
        document.getElementById('logradouro').value = e.logradouro || '';
        document.getElementById('numero').value = e.numero || '';
        document.getElementById('complemento').value = e.complemento || '';
        document.getElementById('bairro').value = e.bairro || '';
        document.getElementById('cidade').value = e.cidade || '';
        document.getElementById('estado').value = e.estado || '';
        document.getElementById('zona_eleitoral').value = e.zona_eleitoral || '';
        document.getElementById('secao_eleitoral').value = e.secao_eleitoral || '';
        document.getElementById('observacoes').value = e.observacoes || '';

        document.getElementById('modal-form').classList.add('active');
    } catch (err) {
        toast('Erro ao carregar dados do eleitor', 'error');
    }
}

// ─── Salvar Eleitor ───────────────────────────────────────

async function salvarEleitor() {
    const id = document.getElementById('edit-id').value;
    const numTitulo = document.getElementById('numero_titulo').value.trim();
    const nome = document.getElementById('nome_completo').value.trim();

    if (!numTitulo || !nome) {
        toast('Preencha o Nº do Título e o Nome Completo', 'error');
        return;
    }

    const data = {
        titulo_eleitoral: numTitulo,
        numero_titulo: numTitulo,
        nome_completo: nome,
        data_nascimento: document.getElementById('data_nascimento').value,
        sexo: document.getElementById('sexo').value,
        telefone: document.getElementById('telefone').value.trim(),
        email: document.getElementById('email').value.trim(),
        cep: document.getElementById('cep').value.trim(),
        logradouro: document.getElementById('logradouro').value.trim(),
        numero: document.getElementById('numero').value.trim(),
        complemento: document.getElementById('complemento').value.trim(),
        bairro: document.getElementById('bairro').value.trim(),
        cidade: document.getElementById('cidade').value.trim(),
        estado: document.getElementById('estado').value,
        zona_eleitoral: document.getElementById('zona_eleitoral').value.trim(),
        secao_eleitoral: document.getElementById('secao_eleitoral').value.trim(),
        observacoes: document.getElementById('observacoes').value.trim(),
    };

    try {
        const url = id ? `${API}/${id}` : API;
        const method = id ? 'PUT' : 'POST';

        const resp = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        });

        if (resp.status === 401) {
            window.location.href = '/login';
            return;
        }

        const result = await resp.json();

        if (resp.ok) {
            toast(result.mensagem, 'success');
            fecharModal();
            carregarEleitores();
        } else {
            toast(result.erro || 'Erro ao salvar', 'error');
        }
    } catch (err) {
        toast('Erro de conexão', 'error');
    }
}

// ─── Excluir Eleitor ──────────────────────────────────────

let deleteId = null;

function confirmarExcluir(id, nome) {
    deleteId = id;
    document.getElementById('confirm-nome').textContent = nome;
    document.getElementById('modal-confirm').classList.add('active');
    document.getElementById('btn-confirm-delete').onclick = excluirEleitor;
}

function fecharModalConfirm() {
    document.getElementById('modal-confirm').classList.remove('active');
    deleteId = null;
}

async function excluirEleitor() {
    if (!deleteId) return;

    try {
        const resp = await fetch(`${API}/${deleteId}`, { method: 'DELETE' });

        if (resp.status === 401) {
            window.location.href = '/login';
            return;
        }

        const result = await resp.json();

        if (resp.ok) {
            toast(result.mensagem, 'success');
            fecharModalConfirm();
            carregarEleitores();
        } else {
            toast(result.erro || 'Erro ao excluir', 'error');
        }
    } catch (err) {
        toast('Erro de conexão', 'error');
    }
}

// ─── Busca CEP (ViaCEP) ───────────────────────────────────

async function buscarCEP() {
    const cep = document.getElementById('cep').value.replace(/\D/g, '');
    if (cep.length !== 8) return;

    try {
        const resp = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
        const data = await resp.json();

        if (!data.erro) {
            document.getElementById('logradouro').value = data.logradouro || '';
            document.getElementById('bairro').value = data.bairro || '';
            document.getElementById('cidade').value = data.localidade || '';
            document.getElementById('estado').value = data.uf || '';
            toast('CEP encontrado!', 'info');
        }
    } catch (err) {
        // CEP não encontrado, ignora
    }
}

// ─── Toast ────────────────────────────────────────────────

function toast(mensagem, tipo = 'info') {
    const container = document.getElementById('toast-container');
    const el = document.createElement('div');
    el.className = `toast ${tipo}`;
    el.textContent = mensagem;
    container.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

// ─── Máscara CPF ──────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Máscara Nº Título (apenas números, 12 dígitos)
    const tituloInput = document.getElementById('numero_titulo');
    tituloInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.replace(/\D/g, '').substring(0, 12);
    });

    const telInput = document.getElementById('telefone');
    telInput.addEventListener('input', (e) => {
        let v = e.target.value.replace(/\D/g, '').substring(0, 11);
        if (v.length > 6) v = v.replace(/(\d{2})(\d{5})(\d{0,4})/, '($1) $2-$3');
        else if (v.length > 2) v = v.replace(/(\d{2})(\d{0,5})/, '($1) $2');
        e.target.value = v;
    });

    const cepInput = document.getElementById('cep');
    cepInput.addEventListener('input', (e) => {
        let v = e.target.value.replace(/\D/g, '').substring(0, 8);
        if (v.length > 5) v = v.replace(/(\d{5})(\d{0,3})/, '$1-$2');
        e.target.value = v;
    });

    // Fechar modais com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            fecharModal();
            fecharModalConfirm();
        }
    });

    // Fechar modal clicando fora
    document.getElementById('modal-form').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) fecharModal();
    });
    document.getElementById('modal-confirm').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) fecharModalConfirm();
    });
});

// ─── Exportar PDF ──────────────────────────────────────────

function exportarPDF() {
    window.location.href = '/api/export/pdf';
    toast('Gerando PDF...', 'info');
}

// ─── Exportar Excel ────────────────────────────────────────

function exportarExcel() {
    window.location.href = '/api/export/excel';
    toast('Gerando Excel...', 'info');
}
