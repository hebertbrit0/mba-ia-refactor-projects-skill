# desafio-skills — Refatoração arquitetural com skill

Documentação da skill `refactor-arch` e da execução nos três projetos do repositório. A skill é a mesma nos três diretórios (`.claude/skills/refactor-arch/`) e não depende de uma linguagem ou framework.

Os projetos e os relatórios ficam na raiz deste repositório, ao lado desta pasta:

- `../code-smells-project/` — Python/Flask, API de e-commerce
- `../ecommerce-api-legacy/` — Node.js/Express, LMS com checkout
- `../task-manager-api/` — Python/Flask, Task Manager
- `../reports/audit-project-1.md`, `audit-project-2.md`, `audit-project-3.md`

## Análise Manual

A leitura abaixo foi feita antes da refatoração. A skill não cita esses projetos: eles só serviram para decidir quais sinais o catálogo precisava reconhecer em qualquer stack.

### code-smells-project (Python/Flask)

- **CRITICAL — SQL Injection.** `models.py` concatena id, nome, e-mail e senha nas queries, e `POST /admin/query` executa o SQL do body. Um cliente passa a ler e alterar o banco inteiro.
- **CRITICAL — Segredo hardcoded e vazado.** `SECRET_KEY` está em `app.py` e o health devolve a mesma chave. Senhas do seed estão em texto puro e a listagem de usuários devolve a coluna `senha`.
- **CRITICAL — God class.** `models.py` mistura SQL, estoque, relatório e formatação dos quatro domínios. Não dá para testar pedido sem carregar produto.
- **HIGH — Conexão global.** `database.py` guarda um `sqlite3` de módulo com `check_same_thread=False`. Requests compartilham a mesma transação.
- **HIGH — Efeito colateral no handler.** Criar pedido dá `print` de e-mail, SMS e push no meio do fluxo HTTP, e a regra de estoque mora no model.
- **MEDIUM — N+1.** Listar pedidos consulta itens e, para cada item, o produto. O relatório de vendas faz cinco queries na mesma tabela.
- **MEDIUM — Validação duplicada.** Criar e atualizar produto repetem os mesmos `if`, e o `except` devolve `str(e)` ao cliente.
- **LOW — Números mágicos.** Os limiares 10000, 5000 e 1000 e as taxas de desconto estão soltos no cálculo.
- **LOW — Mapeamento copiado.** O dicionário de produto é montado à mão em três funções.

### ecommerce-api-legacy (Node.js/Express)

- **CRITICAL — God class.** `AppManager.setupRoutes` cria schema, seed, checkout, relatório e delete.
- **CRITICAL — Segredo e cartão no log.** `utils.js` traz senha de banco, chave `pk_live_...` e SMTP. O checkout imprime o número do cartão e a chave.
- **HIGH — Hash caseiro.** `badCrypto` corta Base64 da senha. Não é função de senha.
- **HIGH — Estado global.** `globalCache` é um objeto de módulo escrito a cada checkout. O relatório financeiro não tem controle de acesso.
- **MEDIUM — N+1.** O relatório busca matrícula, usuário e pagamento dentro de callbacks aninhados.
- **MEDIUM — Delete incompleto.** Apagar usuário deixa matrícula e pagamento no banco. A própria resposta admite isso.
- **LOW — Nomes opacos.** `u`, `e`, `p`, `cid` e `cc` no checkout.
- **LOW — Prefixo mágico.** Cartão aprovado é o que começa com `"4"`, sem nome. `totalRevenue` é exportado e nunca lido.

### task-manager-api (Python/Flask, camadas parciais)

- **CRITICAL — Segredo hardcoded.** `SECRET_KEY` em `app.py` e senha SMTP `senha123` em `NotificationService`. O processo sobe com `debug=True` em `0.0.0.0`.
- **CRITICAL — Senha exposta e MD5.** `User.to_dict` devolve `password`. O hash é MD5 sem sal. O login devolve esse dict e o token `fake-jwt-token-<id>`.
- **HIGH — Rota no lugar do controller.** Validação, SQLAlchemy e a regra de atraso estão nos blueprints, embora `Task.is_overdue` já exista e não seja usada.
- **HIGH — Superfície aberta.** Delete de usuário, relatório e troca de role não verificam identidade.
- **MEDIUM — N+1.** A listagem busca usuário e categoria por task. O relatório conta tasks por usuário em loop. `/categories` conta tasks uma a uma.
- **MEDIUM — API obsoleta e validação morta.** `datetime.utcnow()` está espalhado (deprecado no Python 3.12). `process_task_data` não é chamado. `marshmallow` e `requests` estão no manifesto sem uso.
- **LOW — Imports mortos e `type(x) == list`.**
- **LOW — Constantes ignoradas.** `VALID_STATUSES` e os limites de título já estão no helper e as rotas repetem os literais.

## Construção da Skill

Ferramenta: Claude Code. A pasta é `.claude/skills/refactor-arch/` e o arquivo principal é `SKILL.md`. A mesma árvore foi copiada, sem edição, para os três projetos (`diff -rq` não acusou diferença).

O `SKILL.md` é o procedimento: ler os cinco references, imprimir a Fase 1 com o que foi detectado, auditar sem gravar arquivo, parar em `y/n`, e só então refatorar. A regra explícita é que stack ausente dos exemplos não autoriza recusa: o agente infere model, rota, controller, config e error handler.

| Arquivo | Papel |
|---|---|
| `references/01-project-analysis.md` | Como detectar linguagem, framework, banco, domínio e o tipo de arquitetura atual, por manifesto e por entry point |
| `references/02-antipattern-catalog.md` | 14 anti-patterns (CRITICAL a LOW), com sinal portátil e exemplo em mais de uma linguagem |
| `references/03-audit-report-template.md` | Relatório da Fase 2, ordenado por severidade, com arquivo e linha |
| `references/04-mvc-guidelines.md` | Responsabilidades fixas e um mapa ilustrativo (Flask, Django, FastAPI, Express, Nest, Spring, Laravel, Rails, ASP.NET, Gin) |
| `references/05-refactor-playbook.md` | 12 transformações com antes/depois em Python e JavaScript, e a ordem de traduzir o padrão em vez de colar o sample |

O catálogo cobre o que a análise manual mostrou de fato: SQL concatenado, segredo literal, dado sensível na resposta, God class, regra na borda HTTP, operação sensível sem controle, estado global, criptografia fraca, N+1, validação duplicada, API deprecated, número mágico, nome opaco e código morto. A detecção de API deprecated tem substituto moderno (`datetime.utcnow()` → `datetime.now(timezone.utc)`, `new Buffer()` → `Buffer.from()`, e o equivalente quando a stack for outra). Operação sensível não fica só no relatório: o playbook tem o padrão de controle de acesso, e a Fase 3 do `SKILL.md` manda corrigir o finding em vez de preservar a rota anônima.

A skill fica agnóstica porque nenhum reference cita estes três diretórios, nenhum fluxo assume Flask ou Express como único alvo, e a Fase 3 manda preservar o entry point e o contrato HTTP do projeto em que ela foi invocada. Exemplos em duas linguagens existem para o agente generalizar.

O ponto difícil foi separar o procedimento da árvore concreta. Um monólito Flask e um Express em memória não podem receber a mesma pasta `src/`. A guideline manda completar a camada que falta quando o projeto já tem `models/` e `routes/`, que foi o caso do task manager. O outro ponto foi corrigir vazamento (senha, cartão, SQL arbitrário) sem mudar método, caminho e status que os clientes já usam.

## Resultados

A Fase 2 parou para confirmação nos três relatórios. A execução deste desafio seguiu para a Fase 3 porque o pedido era entregar o refactor completo.

### Contagem da auditoria

- Projeto 1 — CRITICAL 4, HIGH 2, MEDIUM 2, LOW 2 (10). Relatório em `../reports/audit-project-1.md`.
- Projeto 2 — CRITICAL 2, HIGH 2, MEDIUM 2, LOW 2 (8). Relatório em `../reports/audit-project-2.md`.
- Projeto 3 — CRITICAL 2, HIGH 2, MEDIUM 2, LOW 2 (8). Inclui `datetime.utcnow()` como API deprecated. Relatório em `../reports/audit-project-3.md`.

Projetos 1 e 2 não usavam API obsoleta. O relatório registra isso em vez de inventar um finding.

### Estrutura antes e depois

Projeto 1 saiu de `app.py`, `controllers.py`, `models.py` e `database.py` para `config/`, `models/` por domínio, `controllers/` por domínio, `views/routes.py`, `middlewares/error_handler.py` e `app.py` como composition root.

Projeto 2 saiu de `src/app.js`, `src/AppManager.js` e `src/utils.js` para `src/config/`, `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/errorHandler.js` e `src/app.js`. O banco continua em memória.

Projeto 3 manteve `models/`, `routes/`, `services/` e `utils/`. Entrou `config/settings.py`, `controllers/` e `middlewares/error_handler.py`. As rotas ficaram finas.

### Checklist de validação

#### Projeto 1

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

##### Fase 2 — Auditoria

- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável) — nenhuma encontrada
- [x] Skill pausa e pede confirmação antes da Fase 3

##### Fase 3 — Refatoração

- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 2

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

##### Fase 2 — Auditoria

- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável) — nenhuma encontrada (`Buffer.from` já era o substituto moderno)
- [x] Skill pausa e pede confirmação antes da Fase 3

##### Fase 3 — Refatoração

- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### Projeto 3

##### Fase 1 — Análise

- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

##### Fase 2 — Auditoria

- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável)
- [x] Skill pausa e pede confirmação antes da Fase 3

##### Fase 3 — Refatoração

- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

### Logs após a refatoração

E-commerce Flask, `python app.py` em `127.0.0.1:5000`:

```
GET /health -> 200
{"status":"ok","database":"connected","counts":{"produtos":10,"usuarios":3,"pedidos":0},"debug":false}
POST /login {"email":"joao@email.com","senha":"123456"} -> 200
{"dados":{"email":"joao@email.com","id":2,"nome":"João Silva","tipo":"cliente"},"mensagem":"Login OK","sucesso":true}
DELETE /produtos/10 -> 200
{"mensagem":"Produto deletado","sucesso":true}
```

O health não devolve `secret_key`. O login com a senha do seed continua válido e a resposta não traz senha. `POST /admin/query` responde 403 e não executa SQL.

LMS Express, `npm start` na porta 3000:

```
LMS API rodando na porta 3000...
POST /api/checkout (cartão 4111...) -> 200 {"msg":"Sucesso","enrollment_id":2}
POST /api/checkout (cartão 5111...) -> 400 Pagamento recusado
POST /api/checkout {} -> 400 Bad Request
POST /api/checkout curso 99 -> 404 Curso não encontrado
GET /api/admin/financial-report -> 200 [{"course":"Clean Architecture","revenue":997,...},{"course":"Docker","revenue":497,...}]
DELETE /api/users/1 -> 200 Usuário deletado.
```

Depois do delete, o curso do usuário removido fica com `revenue: 0` e `students: []`. O log de boot não contém o número do cartão.

Task Manager, `PORT=5001 python app.py`:

```
GET /health -> 200 {"status":"ok","timestamp":"2026-11-19 11:02:00.737932"}
GET /tasks -> 200
GET /reports/summary -> 200
POST /login {"email":"maria@email.com","password":"abcd"} -> 200
{"message":"Login realizado com sucesso","token":"5AYRQCYOIZa_HsPy8w1GspnQXARP3TXMCRaD_o0B9pE","user":{"email":"maria@email.com","role":"user",...}}
```

O objeto `user` não tem `password`. O token não é `fake-jwt-token-<id>`. `GET /reports/summary`, `PUT /users/<id>` e `DELETE /users/<id>` sem `Authorization: Bearer` respondem 401. Com o token do login, o relatório responde 200. Trocar `role` ou apagar outro usuário sem papel admin responde 403.

### O que mudou entre as stacks

No Flask monolítico a Fase 3 criou as pastas, porque não havia camada. No Express a mesma skill separou a God class e trocou callback aninhado por função assíncrona, mantendo `:memory:` e os textos de `api.http`. No task manager, que já tinha model e blueprint, a Fase 3 não recriou a árvore: moveu o caso de uso para `controllers/`, trocou MD5 pelo hash do Werkzeug, substituiu `datetime.utcnow()` por um único helper em cima de `datetime.now(timezone.utc)` e passou a conferir o token do login nas rotas que a auditoria marcou como sem identidade. O método e o caminho HTTP ficaram nos três. O status anônimo de operação sensível não.

## Como Executar

Pré-requisito: [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado. A skill já está em `.claude/skills/refactor-arch/` dentro de cada projeto.

Na raiz do repositório:

```bash
cd code-smells-project
claude "/refactor-arch"

cd ../ecommerce-api-legacy
claude "/refactor-arch"

cd ../task-manager-api
claude "/refactor-arch"
```

A Fase 2 imprime o relatório e espera `y` antes de alterar arquivo. Os relatórios desta execução estão em `reports/`.

Subir as aplicações já refatoradas:

```bash
cd code-smells-project
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python app.py
# http://127.0.0.1:5000

cd ../ecommerce-api-legacy
npm install && npm start
# http://127.0.0.1:3000

cd ../task-manager-api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python seed.py
.venv/bin/python app.py
# http://127.0.0.1:5000
```

`SECRET_KEY`, `PORT`, `HOST`, `FLASK_DEBUG`, `DB_PATH`, `DATABASE_URL`, `PAYMENT_GATEWAY_KEY` e `SMTP_PASSWORD` saem do ambiente. Sem `SECRET_KEY`, o processo gera uma chave efêmera só para aquele boot.

Para validar, chame os caminhos que já existiam. No projeto 1, `/health`, `/produtos`, `/login` e `/pedidos` seguem públicos. `GET /relatorios/vendas` exige o token do `POST /login`. `DELETE /produtos/<id>` e `POST /admin/reset-db` exigem o token de um usuário `admin` (`admin@loja.com` / `admin123`); sem token a resposta é 401 e com um cliente é 403. No projeto 2, o checkout de `api.http` segue sem credencial e, sem `pwd`, responde 400. `GET /api/admin/financial-report` exige `Authorization: Bearer` de `POST /api/login` (`leonan@fullcycle.com.br` / `123`). `DELETE /api/users/:id` exige esse token e só apaga o próprio usuário; outro id responde 403. No projeto 3, `GET /tasks` segue público. `DELETE /tasks/<id>`, `DELETE /categories/<id>`, `/reports/summary`, a troca de role e o delete de usuário exigem o token de `POST /login`. `POST /users` com `role` diferente de `user` sem admin responde 403. Login do task manager, depois do seed: `joao@email.com` / `1234` (admin) e `maria@email.com` / `abcd` (user).
