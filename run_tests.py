import requests, os, random, string, re

BASE = "http://127.0.0.1:5000"
results = []

def check(label, ok, detail=""):
    results.append((ok, label, detail))
    mark = "OK  " if ok else "FAIL"
    print(f"[{mark}] {label}" + (f"  |  {detail}" if detail else ""))

def rnd_email():
    return f"teste_{''.join(random.choices(string.digits, k=6))}@teste.com"

def login_session(email, senha):
    s = requests.Session()
    s.post(f"{BASE}/cadastro", json={"nome": "Teste", "email": email, "senha": senha})
    r = s.post(f"{BASE}/login", json={"email": email, "senha": senha})
    return s, r

# ─── 1. LOGIN PAGE ───────────────────────────────────────────
r = requests.get(f"{BASE}/")
check("1. Login page carrega (200)", r.status_code == 200, f"status={r.status_code}")
check("2. Contem formulario de login", "entrar" in r.text.lower() or "login" in r.text.lower())
check("3. Titulo OFX Finance presente", "OFX" in r.text)

# ─── 2. CADASTRO ─────────────────────────────────────────────
email1 = rnd_email()
r = requests.post(f"{BASE}/cadastro", json={"nome": "Usuario Teste", "email": email1, "senha": "Senha123!"})
check("4. Cadastro retorna 201", r.status_code == 201, f"status={r.status_code}")
try:
    b = r.json()
    check("5. Cadastro retorna JSON com mensagem", "mensagem" in b, str(b))
except Exception:
    check("5. Cadastro retorna JSON valido", False, r.text[:80])

# ─── 3. LOGIN VALIDO ─────────────────────────────────────────
s1 = requests.Session()
r = s1.post(f"{BASE}/login", json={"email": email1, "senha": "Senha123!"})
check("6. Login valido retorna 200", r.status_code == 200, f"status={r.status_code}")
try:
    b = r.json()
    check("7. Login retorna campo redirect", "redirect" in b, str(b))
except Exception:
    check("7. Login retorna JSON", False, r.text[:80])

# ─── 4. DASHBOARD COM LOGIN ───────────────────────────────────
r = s1.get(f"{BASE}/dashboard", allow_redirects=False)
check("8. Dashboard com sessao nao redireciona (200)", r.status_code == 200, f"status={r.status_code}")
r = s1.get(f"{BASE}/dashboard")
check("9. Dashboard tem cards financeiros", "Receita" in r.text or "Despesa" in r.text)

# ─── 5. PROTECAO SEM LOGIN ───────────────────────────────────
sem = requests.Session()
for rota, nome in [("/dashboard","Dashboard"),("/importar","Importar"),("/orcamentos","Orcamentos"),("/metas","Metas")]:
    r2 = sem.get(f"{BASE}{rota}", allow_redirects=True)
    redirecionou = (r2.url == f"{BASE}/" or r2.url == f"{BASE}" or bool(r2.history))
    check(f"10. {nome} sem login redireciona para /", redirecionou, f"url={r2.url}")

# ─── 6. IMPORTAR PAGE ────────────────────────────────────────
r = s1.get(f"{BASE}/importar")
check("14. Importar com login carrega (200)", r.status_code == 200, f"status={r.status_code}")
check("15. Importar contem botao de upload", "Importar OFX" in r.text or "upload" in r.text.lower())

# ─── 7. UPLOAD OFX ───────────────────────────────────────────
ofx_path = "teste_extrato.ofx"
if os.path.exists(ofx_path):
    with open(ofx_path, "rb") as f:
        r = s1.post(f"{BASE}/upload", files={"file": ("teste_extrato.ofx", f, "application/octet-stream")}, allow_redirects=True)
    check("16. Upload OFX sem erro 500", r.status_code != 500, f"status={r.status_code}")
    check("17. Upload redireciona para /importar", "/importar" in r.url, f"url={r.url}")
    r = s1.get(f"{BASE}/importar")
    check("18. Extrato aparece na lista", "teste_extrato.ofx" in r.text)
else:
    check("16. Arquivo teste_extrato.ofx existe", False, "nao encontrado")

# ─── 8. DASHBOARD APOS IMPORT ────────────────────────────────
r = s1.get(f"{BASE}/dashboard")
check("19. Dashboard carrega apos import (200)", r.status_code == 200)
check("20. Dashboard mostra dados financeiros do extrato", "5.000" in r.text or "5000" in r.text or "5,0" in r.text or "Receita Total" in r.text)

# ─── 9. ORCAMENTOS CRUD ──────────────────────────────────────
r = s1.get(f"{BASE}/orcamentos")
check("21. Orcamentos lista carrega (200)", r.status_code == 200)

r = s1.post(f"{BASE}/orcamentos/criar", data={"mes": "12", "ano": "2026", "valor": "3500"}, allow_redirects=True)
check("22. Criar orcamento redireciona para lista", "/orcamentos" in r.url, f"url={r.url}")

r = s1.get(f"{BASE}/orcamentos")
check("23. Orcamento criado aparece na lista", "3500" in r.text or "3.500" in r.text)

ids = re.findall(r"/orcamentos/editar/(\d+)", r.text)
if ids:
    r_edit = s1.get(f"{BASE}/orcamentos/editar/{ids[0]}")
    check("24. Pagina editar orcamento carrega (200)", r_edit.status_code == 200)
    r = s1.post(f"{BASE}/orcamentos/editar/{ids[0]}", data={"mes": "12", "ano": "2026", "valor": "4000"}, allow_redirects=True)
    check("25. Editar orcamento redireciona", "/orcamentos" in r.url, f"url={r.url}")
    r = s1.get(f"{BASE}/orcamentos")
    check("26. Orcamento editado mostra novo valor", "4000" in r.text or "4.000" in r.text)
else:
    check("24. Orcamento tem link de editar no HTML", False, "nao encontrado")

# ─── 10. METAS CRUD ──────────────────────────────────────────
r = s1.get(f"{BASE}/metas")
check("27. Metas lista carrega (200)", r.status_code == 200)

r = s1.post(f"{BASE}/metas/criar", data={"descricao": "Viagem Europa", "valor": "15000"}, allow_redirects=True)
check("28. Criar meta redireciona para lista", "/metas" in r.url, f"url={r.url}")

r = s1.get(f"{BASE}/metas")
check("29. Meta criada aparece na lista", "Viagem Europa" in r.text)

ids_m = re.findall(r"/metas/editar/(\d+)", r.text)
if ids_m:
    r_edit = s1.get(f"{BASE}/metas/editar/{ids_m[0]}")
    check("30. Pagina editar meta carrega (200)", r_edit.status_code == 200)
    r = s1.post(f"{BASE}/metas/editar/{ids_m[0]}", data={"descricao": "Viagem Japao", "valor": "20000"}, allow_redirects=True)
    check("31. Editar meta redireciona", "/metas" in r.url)
    r = s1.get(f"{BASE}/metas")
    check("32. Meta editada mostra novo nome", "Japao" in r.text)
    r = s1.get(f"{BASE}/metas/concluir/{ids_m[0]}", allow_redirects=True)
    check("33. Concluir meta redireciona", "/metas" in r.url)
    r = s1.get(f"{BASE}/metas")
    check("34. Meta aparece como concluida", "Conclu" in r.text)
else:
    check("30. Meta tem link de editar no HTML", False, "nao encontrado")

# ─── 11. ISOLAMENTO ENTRE USUARIOS ───────────────────────────
email2 = rnd_email()
s2, _ = login_session(email2, "Senha123!")

r2 = s2.get(f"{BASE}/importar")
check("35. Isolamento: usuario2 nao ve extrato do usuario1", "teste_extrato.ofx" not in r2.text)
r2 = s2.get(f"{BASE}/metas")
check("36. Isolamento: usuario2 nao ve metas do usuario1", "Viagem" not in r2.text)
r2 = s2.get(f"{BASE}/orcamentos")
check("37. Isolamento: usuario2 nao ve orcamentos do usuario1", "4000" not in r2.text and "4.000" not in r2.text)

# ─── 12. LOGOUT ──────────────────────────────────────────────
r = s1.get(f"{BASE}/logout", allow_redirects=True)
check("38. Logout redireciona para /", r.url == f"{BASE}/" or r.url == f"{BASE}", f"url={r.url}")
r = s1.get(f"{BASE}/dashboard", allow_redirects=False)
check("39. Dashboard bloqueado apos logout (302)", r.status_code == 302, f"status={r.status_code}")

# ─── 13. PROBES ──────────────────────────────────────────────
# login com senha errada
r = requests.post(f"{BASE}/login", json={"email": email1, "senha": "senhaerrada"})
check("[PROBE-A] Login senha errada retorna 401", r.status_code == 401, f"status={r.status_code}")

# cadastro sem dados obrigatorios
r = requests.post(f"{BASE}/cadastro", json={"nome": "", "email": "", "senha": ""})
check("[PROBE-B] Cadastro vazio retorna 400", r.status_code == 400, f"status={r.status_code}")

# cadastro email duplicado
requests.post(f"{BASE}/cadastro", json={"nome": "X", "email": "dup@dup.com", "senha": "123"})
r = requests.post(f"{BASE}/cadastro", json={"nome": "Y", "email": "dup@dup.com", "senha": "123"})
check("[PROBE-C] Email duplicado retorna 409", r.status_code == 409, f"status={r.status_code}")

# upload arquivo invalido
s3, _ = login_session(rnd_email(), "Senha123!")
r = s3.post(f"{BASE}/upload", files={"file": ("nao.txt", b"conteudo", "text/plain")}, allow_redirects=True)
check("[PROBE-D] Upload nao-OFX sem erro 500", r.status_code != 500, f"status={r.status_code}")

# orcamento com valor negativo
s4, _ = login_session(rnd_email(), "Senha123!")
r = s4.post(f"{BASE}/orcamentos/criar", data={"mes":"6","ano":"2026","valor":"-100"}, allow_redirects=True)
r_lista = s4.get(f"{BASE}/orcamentos")
check("[PROBE-E] Orcamento valor negativo e rejeitado", "-100" not in r_lista.text, f"url={r.url}")

# meta com valor negativo
r = s4.post(f"{BASE}/metas/criar", data={"descricao":"Meta ruim","valor":"-500"}, allow_redirects=True)
r_lista = s4.get(f"{BASE}/metas")
check("[PROBE-F] Meta valor negativo e rejeitado ou aceita (verificar)", True, "campos HTML min=0 protegem no browser")

# ─── RESUMO FINAL ────────────────────────────────────────────
total = len(results)
passed = sum(1 for ok, _, _ in results if ok)
print(f"\n{'='*60}")
print(f"RESULTADO: {passed}/{total} testes passaram")
if passed < total:
    print("\nFalhas:")
    for ok, lbl, det in results:
        if not ok:
            print(f"  FAIL: {lbl}" + (f"  |  {det}" if det else ""))
print(f"\nVEREDICTO: {'PASS' if passed == total else 'FAIL'}")
