function alternarAba(aba, el) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('ativa'));
    document.querySelectorAll('.form').forEach(f => f.classList.remove('ativo'));
    el.classList.add('ativa');
    document.getElementById('form-' + aba).classList.add('ativo');
}

// Versão usada pelos links "Já tem conta?" / "Não tem conta?"
function irParaAba(aba) {
    const tab = [...document.querySelectorAll('.tab')]
        .find(t => t.textContent.trim().toLowerCase().includes(aba === 'login' ? 'entrar' : 'cadastrar'));
    alternarAba(aba, tab);
}

function mostrarMsg(id, texto, tipo) {
    const el = document.getElementById(id);
    el.textContent = texto;
    el.className = 'msg ' + tipo;
}

async function fazerLogin() {
    const email = document.getElementById('login-email').value.trim();
    const senha = document.getElementById('login-senha').value;

    if (!email || !senha) {
        mostrarMsg('msg-login', 'Preencha email e senha.', 'erro');
        return;
    }

    const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, senha })
    });

    const dados = await res.json();

    if (res.ok) {
        mostrarMsg('msg-login', 'Login realizado! Redirecionando...', 'ok');
        // Vai direto para o dashboard após login
        setTimeout(() => { window.location.href = '/dashboard'; }, 600);
    } else {
        mostrarMsg('msg-login', dados.erro, 'erro');
    }
}

async function fazerCadastro() {
    const nome  = document.getElementById('cad-nome').value.trim();
    const email = document.getElementById('cad-email').value.trim();
    const senha = document.getElementById('cad-senha').value;

    if (!nome || !email || !senha) {
        mostrarMsg('msg-cadastro', 'Preencha todos os campos.', 'erro');
        return;
    }

    const res = await fetch('/cadastro', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome, email, senha })
    });

    const dados = await res.json();

    if (res.ok) {
        mostrarMsg('msg-cadastro', 'Conta criada! Faça seu login.', 'ok');
        // Limpa os campos do cadastro
        document.getElementById('cad-nome').value = '';
        document.getElementById('cad-email').value = '';
        document.getElementById('cad-senha').value = '';
        // Vai automaticamente para a aba de login após 1 segundo
        setTimeout(() => {
            irParaAba('login');
            mostrarMsg('msg-login', 'Conta criada com sucesso! Entre agora.', 'ok');
        }, 1000);
    } else {
        mostrarMsg('msg-cadastro', dados.erro, 'erro');
    }
}
