================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:     Flask 3.1.1
Dependencies:  flask-cors 5.0.1
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — rotas, SQL e regra de negócio espalhados em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB:            SQLite (loja.db) — produtos, usuarios, pedidos, itens_pedido
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~781 lines of code

## Summary
CRITICAL: 4 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] SQL Injection
File: models.py:28, models.py:47-49, models.py:57-60, models.py:66, models.py:90, models.py:109-110, models.py:126-128, models.py:140, models.py:148-166, models.py:174, models.py:188-192, models.py:220-224, models.py:279-280, models.py:289-297; app.py:59-75
Description: Consultas de produto, usuário, login, pedido e busca concatenam valores na string SQL. O endpoint POST /admin/query executa o SQL recebido no corpo da requisição.
Impact: Um cliente lê ou altera qualquer tabela, inclusive senhas. O endpoint administrativo executa comando arbitrário sem restrição.
Recommendation: Trocar toda concatenação por parâmetro do sqlite3. O endpoint de SQL livre deve responder erro e não executar.

### [CRITICAL] Segredo hardcoded
File: app.py:8
Description: SECRET_KEY está fixa no fonte como 'minha-chave-super-secreta-123'. DEBUG também está ligado no código.
Impact: Quem tem o repositório forja sessão e reproduz o segredo de produção. Debug expõe o debugger do Werkzeug na rede (app.py:88, host 0.0.0.0).
Recommendation: Ler segredo, debug, porta e caminho do banco de variáveis de ambiente, sem literal versionado.

### [CRITICAL] Exposição de dado sensível
File: controllers.py:289; models.py:79-86; models.py:95-100; database.py:75-79
Description: O health check devolve secret_key. A listagem e a busca de usuário devolvem a coluna senha. O seed grava senha em texto puro (admin123, 123456, senha123).
Impact: Qualquer chamada a /health ou /usuarios revela segredo e senha reutilizável.
Recommendation: Serializer público sem senha, hash de senha no seed e no cadastro, health sem segredo.

### [CRITICAL] God Class
File: models.py:1-314
Description: Um único módulo executa SQL, regra de estoque, cálculo de relatório e formatação dos quatro domínios (produto, usuário, pedido e item).
Impact: Não há teste isolado por domínio. Qualquer alteração em pedido reabre o arquivo de produto.
Recommendation: Um model por domínio, só com persistência. A regra de pedido fica no controller.

### [HIGH] Estado global mutável
File: database.py:4-10
Description: Uma conexão SQLite de módulo, aberta com check_same_thread=False, é reutilizada por todos os requests.
Impact: Requests concorrentes compartilham cursor e transação. O check_same_thread esconde o problema em vez de resolvê-lo.
Recommendation: Abrir a conexão no escopo do request e fechá-la no teardown.

### [HIGH] Regra de negócio e efeito colateral no fluxo HTTP
File: controllers.py:188-220; controllers.py:247-250
Description: O handler de pedido dispara e-mail, SMS e push com print no meio da transação. O model também decide estoque e total (models.py:133-169). Não existe caso de uso separado da rota.
Impact: A regra não roda fora do request e o efeito colateral não tem dono. Falha de notificação se mistura com falha de persistência.
Recommendation: Controller orquestra validação, estoque e total; model só persiste; notificação é uma função chamada depois do commit.

### [MEDIUM] N+1 queries
File: models.py:171-201; models.py:203-233
Description: Para cada pedido, o código consulta itens e, para cada item, consulta o produto. relatorio_vendas (models.py:239-254) faz cinco idas ao banco para um único agregado.
Impact: A listagem de pedidos cresce com o quadrado dos itens. O relatório repete a mesma tabela.
Recommendation: Um JOIN de pedido, item e produto. Um único SELECT com agregação condicional para o relatório.

### [MEDIUM] Validação duplicada e erro interno vazado
File: controllers.py:24-54; controllers.py:64-91; controllers.py:10-12
Description: Criar e atualizar produto repetem a checagem de nome, preço e estoque. Cada handler captura Exception e devolve str(e) ao cliente.
Impact: A regra diverge entre os dois fluxos. O cliente recebe detalhe de SQL e de caminho interno.
Recommendation: Uma função de validação compartilhada e um error handler que registra a exceção e responde mensagem genérica.

### [LOW] Números mágicos no desconto
File: models.py:256-262
Description: Limiares 10000, 5000 e 1000 e taxas 0.1, 0.05 e 0.02 estão soltos no cálculo de faturamento.
Impact: O significado da regra não está no código e qualquer cópia futura diverge.
Recommendation: Constantes nomeadas no módulo do relatório.

### [LOW] Mapeamento de produto copiado
File: models.py:12-21; models.py:31-40; models.py:303-313
Description: O mesmo dicionário de colunas de produto é montado à mão em três funções.
Impact: Um campo novo precisa ser lembrado em cada cópia.
Recommendation: Uma função única de mapeamento da linha.

Deprecated APIs: nenhuma encontrada nesta varredura.

================================
Total: 10 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
