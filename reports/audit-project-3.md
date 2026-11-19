================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.0.0
Dependencies:  flask-sqlalchemy 3.1.1, flask-cors 4.0.0, marshmallow 3.20.1, requests 2.31.0, python-dotenv 1.0.0
Domain:        Task Manager API (tasks, usuários, categorias, relatórios)
Architecture:  Camadas parciais — models, routes, services e utils existem, mas a rota concentra validação, persistência e regra, e não há controller
Source files:  15 files analyzed
DB:            SQLite (tasks.db) via SQLAlchemy — users, categories, tasks
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask
Files:   15 analyzed | ~1170 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] Segredo hardcoded
File: app.py:13; services/notification_service.py:8-10
Description: SECRET_KEY está fixa como 'super-secret-key-123'. NotificationService guarda usuário e senha de SMTP (taskmanager@gmail.com / senha123) no construtor.
Impact: O repositório entrega o segredo de sessão e uma senha de e-mail. Debug ligado com host 0.0.0.0 (app.py:34) amplia o alcance.
Recommendation: Ler segredo, debug, host, porta e SMTP do ambiente. Sem credencial, o envio de e-mail não tenta login com senha de código.

### [CRITICAL] Exposição de senha e hash fraco
File: models/user.py:16-32; routes/user_routes.py:207-210
Description: to_dict inclui password. O hash é MD5 sem sal. O login devolve esse dict e um token previsível fake-jwt-token-<id>.
Impact: GET /users/<id>, POST /users e POST /login entregam o hash. MD5 não resiste a um vazamento do banco, e o token se falsifica sem senha.
Recommendation: Hash de senha da plataforma (Werkzeug), serializer sem password, token imprevisível.

### [HIGH] Regra de negócio na rota
File: routes/task_routes.py:11-299; routes/user_routes.py:10-211; routes/report_routes.py:12-223
Description: Os blueprints validam, consultam o banco, calculam atraso e montam o JSON. Não existe camada de controller. A mesma decisão de overdue está copiada na rota mesmo com Task.is_overdue no model.
Impact: A regra não vive num caso de uso. Corrigir o atraso exige achar cada cópia.
Recommendation: Rota só delega. Controller orquestra. Model responde is_overdue e persiste.

### [HIGH] Operação sensível sem barreira e debug aberto
File: app.py:34; routes/user_routes.py:134-151; routes/report_routes.py:12
Description: Não há verificação de identidade em delete de usuário, relatórios ou alteração de role. O processo sobe com debug=True em 0.0.0.0.
Impact: Qualquer cliente na rede apaga usuário e lê produtividade. O debugger do Werkzeug não pode ficar exposto.
Recommendation: Debug e host vêm do ambiente, desligados por padrão. O contrato atual das rotas continua anônimo para não mudar o status das chamadas existentes; o dado sensível sai da resposta.

### [MEDIUM] N+1 queries
File: routes/task_routes.py:41-57; routes/report_routes.py:53-68; routes/report_routes.py:157-164; routes/user_routes.py:22
Description: A listagem de tasks busca usuário e categoria dentro do loop. O relatório de produtividade carrega as tasks de cada usuário. /categories conta tasks com uma query por categoria. task_count do usuário usa a relação lazy.
Impact: A latência sobe com a quantidade de tasks e usuários.
Recommendation: joinedload nas relações many-to-one e contagem agregada com GROUP BY.

### [MEDIUM] API deprecated e validação duplicada
File: models/task.py:15-16; models/user.py:14; models/category.py:11; routes/task_routes.py:31; routes/report_routes.py:35; services/notification_service.py:35; seed.py:66; utils/helpers.py:38
Description: datetime.utcnow() está deprecado desde o Python 3.12 e aparece em model, rota, serviço, helper e seed. A validação de task está inline nas rotas enquanto process_task_data em utils/helpers.py:57-108 não é chamada. marshmallow e requests estão no requirements.txt e não têm nenhum import.
Impact: A próxima versão do Python quebra o boot. Duas validações divergem, e a dependência não protege a rota.
Recommendation: Um helper utcnow() em cima de datetime.now(timezone.utc). As rotas de criar e atualizar passam a usar process_task_data. Dependência sem uso sai do manifesto.

### [LOW] Import morto e comparação de tipo por identidade
File: app.py:7; routes/task_routes.py:7; routes/user_routes.py:6; routes/report_routes.py:8; utils/helpers.py:3-7; routes/task_routes.py:141
Description: json, os, sys, time, hashlib, math e re entram em módulos que não usam todos. Tags são testadas com type(tags) == list.
Impact: Ruído na leitura e uma comparação que falha para subclasse de list.
Recommendation: Apagar o import não usado e usar isinstance(tags, list).

### [LOW] Constantes ignoradas
File: utils/helpers.py:110-117; routes/task_routes.py:110; routes/task_routes.py:177
Description: VALID_STATUSES, MIN_TITLE_LENGTH e DEFAULT_PRIORITY já existem no helper, mas as rotas repetem os literais ['pending', ...] e os limites 3, 200, 1 e 5.
Impact: Mudar um status válido em um arquivo deixa o outro desatualizado.
Recommendation: A validação única lê essas constantes.

Deprecated APIs: datetime.utcnow() em models, routes, services, helpers e seed. Substituto: datetime.now(timezone.utc), normalizado para UTC sem fuso porque o SQLite devolve datetime ingênuo.

================================
Total: 8 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
