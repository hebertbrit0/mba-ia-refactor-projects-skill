================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript
Framework:     Express 4.18.2
Dependencies:  sqlite3 5.1.6
Domain:        LMS API com fluxo de checkout (usuários, cursos, matrículas, pagamentos)
Architecture:  Monolítica — schema, seed, checkout, relatório e delete concentrados em uma classe
Source files:  3 files analyzed
DB:            SQLite em memória — users, courses, enrollments, payments, audit_logs
================================

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript + Express
Files:   3 analyzed | ~181 lines of code

## Summary
CRITICAL: 2 | HIGH: 2 | MEDIUM: 2 | LOW: 2

## Findings

### [CRITICAL] God Class
File: src/AppManager.js:1-141
Description: A classe AppManager abre o banco, cria o schema, faz o seed e registra checkout, relatório financeiro e delete de usuário dentro de setupRoutes.
Impact: Pagamento, persistência e HTTP não podem ser testados separados. Qualquer ajuste no relatório mexe no checkout.
Recommendation: Model por agregado, controller por caso de uso e rotas que só delegam. O entry point compõe o banco e as rotas.

### [CRITICAL] Segredo hardcoded e dado sensível em log
File: src/utils.js:1-7; src/AppManager.js:45
Description: dbPass, paymentGatewayKey e a senha de SMTP estão literais no módulo de config. O checkout imprime o número completo do cartão e a chave do gateway.
Impact: O repositório entrega credencial de produção. O log vira cópia do cartão.
Recommendation: Ler segredo do ambiente e não logar PAN nem chave. A decisão de pagamento usa só o prefixo, sem escrever o número.

### [HIGH] Criptografia fraca
File: src/utils.js:17-23
Description: badCrypto repete Base64 da senha dez mil vezes e devolve dez caracteres. Não há sal nem função de derivação.
Impact: A coluna pass não protege a senha se o banco vazar. O mesmo texto gera o mesmo prefixo.
Recommendation: crypto.scrypt (ou equivalente da plataforma) com sal aleatório.

### [HIGH] Estado global mutável
File: src/utils.js:9-15
Description: globalCache é um objeto de módulo escrito a cada checkout. totalRevenue é exportado e nunca lido. A conexão nasce dentro da classe, mas o cache não tem dono nem limite.
Impact: Dados de um checkout ficam no processo e podem ser lidos por outro fluxo. O estado morto confunde a leitura.
Recommendation: Remover o cache global. Auditoria fica na tabela audit_logs. A conexão é criada no entry point e injetada.

### [MEDIUM] N+1 e callback hell no relatório
File: src/AppManager.js:80-128
Description: Para cada curso o código busca matrículas; para cada matrícula busca usuário e pagamento, aninhando callbacks e contadores manuais.
Impact: O tempo do relatório cresce com cursos vezes alunos, e um contador errado responde duas vezes ou nunca.
Recommendation: Um JOIN de courses, enrollments, users e payments, agrupado em memória.

### [MEDIUM] Delete sem integridade
File: src/AppManager.js:131-136
Description: DELETE /api/users/:id apaga só users. Matrículas e pagamentos permanecem, e a própria resposta admite o dado sujo. O erro do driver é ignorado.
Impact: Relatório financeiro continua contando pagamento de usuário que não existe mais.
Recommendation: Apagar pagamentos, matrículas e usuário na mesma transação.

### [LOW] Nomes opacos no checkout
File: src/AppManager.js:29-33
Description: O corpo do checkout é lido para u, e, p, cid e cc.
Impact: O fluxo de pagamento não diz o que cada campo é sem voltar no api.http.
Recommendation: userName, email, password, courseId e cardNumber.

### [LOW] Número mágico na decisão de pagamento
File: src/AppManager.js:46
Description: Cartão aprovado é o que começa com "4", literal no meio do handler.
Impact: A regra de negócio não tem nome e se perde na próxima cópia do fluxo.
Recommendation: Constante PAID_CARD_PREFIX ao lado da função paymentStatus.

Deprecated APIs: nenhuma encontrada nesta varredura. O código já usa Buffer.from, não new Buffer.

================================
Total: 8 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
