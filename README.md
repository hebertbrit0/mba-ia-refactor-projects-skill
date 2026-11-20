# Criação de Skills — Refatoração Arquitetural Automatizada

Ao longo do curso você aprendeu o que são Skills e como elas permitem que um agente de IA atue como um especialista em tarefas específicas. Agora imagine o seguinte cenário: você herdou 3 projetos legados com problemas de arquitetura, segurança e qualidade de código. Revisar e corrigir tudo manualmente levaria dias.

Neste desafio, você vai criar uma Skill que automatiza esse processo — analisando, auditando e refatorando qualquer projeto para o padrão MVC, independente da tecnologia.

## Objetivo

Você deve entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto

### Definição de Severidades

Para padronizar a sua auditoria e os relatórios gerados pela IA, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- **CRITICAL:** Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- **HIGH:** Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- **MEDIUM:** Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- **LOW:** Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

## Tecnologias obrigatórias

- **Ferramenta:** uma das três opções abaixo (não são aceitas outras ferramentas):
  - Claude Code
  - Gemini CLI
  - OpenAI Codex
- **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
- **Formato dos arquivos de referência:** Markdown
- **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

> **Nota sobre a ferramenta:** Os exemplos deste documento usam o Claude Code (`.claude/skills/`) como referência, pois é a ferramenta utilizada no curso. Se você optar por Gemini CLI ou Codex, adapte o nome da pasta e o comando de invocação conforme a convenção dela — o conceito de skill e a estrutura interna (SKILL.md + arquivos de referência) permanecem os mesmos.

## Requisitos

### 1. Análise Manual dos Projetos

Antes de criar a skill, você deve entender os problemas que ela vai resolver.

**Tarefas:**

- Analisar o projeto `code-smells-project/` (Python/Flask — API de E-commerce)
- Analisar o projeto `ecommerce-api-legacy/` (Node.js/Express — LMS API com fluxo de checkout)
- Analisar o projeto `task-manager-api/` (Python/Flask — API de Task Manager)

Para cada projeto, identificar e documentar no mínimo 5 problemas, incluindo pelo menos:

- 1 de severidade CRITICAL ou HIGH
- 2 de severidade MEDIUM
- 2 de severidade LOW

Documentar os achados na seção "Análise Manual" do seu `README.md`

> **Dica:** Não precisa encontrar todos os problemas — foque nos que têm maior impacto arquitetural. Use os projetos como insumo para entender quais padrões sua skill precisa detectar.

> **Por que 3 projetos?** Dois são Python/Flask (com níveis de organização diferentes) e um é Node.js/Express. Sua skill precisa funcionar nos 3 para provar que é verdadeiramente agnóstica de tecnologia — lidando tanto com código completamente desestruturado quanto com projetos que já possuem alguma separação de camadas.

### 2. Criação da Skill

Agora que você conhece os problemas, crie uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

**Tarefas:**

Criar a skill dentro do projeto `code-smells-project/` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Criar arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento | O que deve conter |
|---|---|
| Análise de projeto | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade |
| Template de relatório | Formato padronizado do relatório de auditoria (Fase 2) |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração | Padrões concretos de transformação para cada anti-pattern (com exemplos de código) |

> **Nota:** Você tem liberdade para organizar os arquivos de referência como preferir — pode usar os nomes e a quantidade de arquivos que fizer sentido para sua skill. O importante é que todas as 5 áreas de conhecimento estejam cobertas. O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados. O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

**Requisitos da skill:**

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos, independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

### 3. Execução da Skill

Execute sua skill nos 3 projetos e valide que ela funciona em todas as stacks.

#### Projeto 1 — code-smells-project (Python/Flask)

Invocar a skill no Claude Code:

```bash
claude "/refactor-arch"
```

> **Nota:** O comando acima é o exemplo com Claude Code. Se você estiver usando Gemini CLI ou Codex, utilize o comando equivalente para invocar uma skill na sua ferramenta.

- Verificar que a Fase 1 detecta corretamente a stack e imprime o resumo
- Verificar que a Fase 2 encontra no mínimo 5 dos problemas documentados na sua análise manual
- Confirmar a execução da Fase 3
- Verificar que a Fase 3:
  - Cria a estrutura de diretórios baseada em MVC
  - A aplicação inicia sem erros
  - Os endpoints originais continuam respondendo
- Salvar o relatório de auditoria (output da Fase 2) em `reports/audit-project-1.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 2 — ecommerce-api-legacy (Node.js/Express)

Prove que sua skill é reutilizável em outro projeto de backend, mas com stack diferente.

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `ecommerce-api-legacy/`
- Invocar a skill:

```bash
cd ../ecommerce-api-legacy
claude "/refactor-arch"
```

- Verificar que as 3 fases executam corretamente neste projeto
- Salvar o relatório em `reports/audit-project-2.md`
- Commitar o código refatorado do projeto no repositório

#### Projeto 3 — task-manager-api (Python/Flask)

Agora o teste com um projeto Python/Flask que já possui alguma organização de camadas (models, routes, services, utils).

- Copiar a pasta `.claude/skills/refactor-arch/` para dentro de `task-manager-api/`
- Invocar a skill:

```bash
cd ../task-manager-api
claude "/refactor-arch"
```

- Verificar que:
  - A Fase 1 detecta corretamente Python/Flask como stack e identifica o domínio de Task Manager
  - A Fase 2 identifica problemas mesmo em um projeto parcialmente organizado
  - A Fase 3 melhora a estrutura sem quebrar a aplicação (todos os endpoints devem continuar respondendo)
- Salvar o relatório em `reports/audit-project-3.md`
- Commitar o código refatorado do projeto no repositório

> **Nota:** Este projeto já possui alguma separação de camadas, mas isso não significa que a arquitetura está adequada. A skill deve identificar tanto problemas de código (segurança, performance, qualidade) quanto oportunidades de melhoria arquitetural. Se houver mudanças estruturais necessárias, a skill deve propô-las e executá-las.

#### Validação

Para cada projeto refatorado, valide o seguinte checklist:

```markdown
## Checklist de Validação

### Fase 1 — Análise
- [ ] Linguagem detectada corretamente
- [ ] Framework detectado corretamente
- [ ] Domínio da aplicação descrito corretamente
- [ ] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [ ] Relatório segue o template definido nos arquivos de referência
- [ ] Cada finding tem arquivo e linhas exatos
- [ ] Findings ordenados por severidade (CRITICAL → LOW)
- [ ] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [ ] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
- [ ] Estrutura de diretórios segue padrão MVC
- [ ] Configuração extraída para módulo de config (sem hardcoded)
- [ ] Models criados para abstrair dados
- [ ] Views/Routes separadas para visualização ou roteamento
- [ ] Controllers concentram o fluxo da aplicação
- [ ] Error handling centralizado
- [ ] Entry point claro
- [ ] Aplicação inicia sem erros
- [ ] Endpoints originais respondem corretamente
```

> **Dica:** Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Entregável

Repositório público no GitHub (fork do repositório base) contendo:

- Skill completa em `.claude/skills/refactor-arch/` (dentro dos 3 projetos)
- Código refatorado dos 3 projetos (resultado da execução da Fase 3, commitado no repositório)
- Relatórios de auditoria em `reports/` (3 arquivos)
- `README.md` atualizado

### Estrutura do repositório

Faça um fork do repositório base contendo os três projetos com code smells.

> **Nota:** A estrutura abaixo usa Claude Code como exemplo (`.claude/skills/`). Se estiver usando outra ferramenta, adapte os caminhos conforme a convenção dela.

```
desafio-skills/
├── README.md                              # Sua documentação
│
├── code-smells-project/                   # Projeto 1 — Python/Flask (API de E-commerce)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← SUA SKILL AQUI
│   │           ├── SKILL.md
│   │           └── (arquivos de referência)
│   ├── app.py
│   ├── controllers.py
│   ├── models.py
│   ├── database.py
│   └── requirements.txt
│
├── ecommerce-api-legacy/                  # Projeto 2 — Node.js/Express (LMS API com checkout)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── src/
│   │   ├── app.js
│   │   ├── AppManager.js
│   │   └── utils.js
│   ├── api.http
│   └── package.json
│
├── task-manager-api/                      # Projeto 3 — Python/Flask (API de Task Manager)
│   ├── .claude/
│   │   └── skills/
│   │       └── refactor-arch/             # ← CÓPIA DA SKILL
│   │           └── ...
│   ├── app.py
│   ├── database.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
│
└── reports/                               # Relatórios gerados
    ├── audit-project-1.md                 # Saída da Fase 2 no projeto 1
    ├── audit-project-2.md                 # Saída da Fase 2 no projeto 2
    └── audit-project-3.md                 # Saída da Fase 2 no projeto 3
```

**O que você vai criar:**

- `.claude/skills/refactor-arch/` — A skill completa (SKILL.md + arquivos de referência)
- Código refatorado dos 3 projetos — resultado da execução da Fase 3, commitado no repositório
- `reports/audit-project-{1,2,3}.md` — Relatório de auditoria de cada projeto
- `README.md` — Documentação do seu processo

**O que já vem pronto:**

- `code-smells-project/` — API de E-commerce Python/Flask com code smells intencionais
- `ecommerce-api-legacy/` — LMS API Node.js/Express (com fluxo de checkout) e problemas de implementação
- `task-manager-api/` — API de Task Manager Python/Flask com organização parcial e problemas de segurança/qualidade

> **Dica:** Cada projeto contém problemas intencionais de diferentes severidades (CRITICAL, HIGH, MEDIUM, LOW), incluindo falhas de segurança, violações arquiteturais e problemas de qualidade de código. Parte do desafio é identificá-los por conta própria através da análise manual do código.

### README.md deve conter

**A) Seção "Análise Manual":**

- Lista dos problemas identificados manualmente em cada projeto
- Classificação por severidade
- Justificativa de por que cada problema é relevante

**B) Seção "Construção da Skill":**

- Decisões de design: como estruturou o SKILL.md e os arquivos de referência
- Quais anti-patterns incluiu no catálogo e por quê
- Como garantiu que a skill é agnóstica de tecnologia
- Desafios encontrados e como resolveu

**C) Seção "Resultados":**

- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
- Comparação antes/depois da estrutura de cada projeto
- Checklist de validação preenchido para cada projeto
- Screenshots ou logs mostrando as aplicações rodando após refatoração
- Observações sobre como a skill se comportou em stacks diferentes

**D) Seção "Como Executar":**

- Pré-requisitos (a ferramenta escolhida — Claude Code, Gemini CLI ou Codex — instalada e configurada)
- Comandos para executar a skill em cada projeto
- Como validar que a refatoração funcionou

### Ordem de execução sugerida

**1. Analisar os projetos manualmente**

Leia o código dos três projetos e documente os problemas encontrados.

**2. Criar a skill**

Escreva o SKILL.md e os arquivos de referência.

**3. Executar nos 3 projetos**

```bash
# Projeto 1
cd code-smells-project
claude "/refactor-arch"

# Projeto 2
cd ../ecommerce-api-legacy
claude "/refactor-arch"

# Projeto 3
cd ../task-manager-api
claude "/refactor-arch"
```

Salve a saída da Fase 2 de cada projeto em `reports/audit-project-{1,2,3}.md`.

**4. Iterar**

Se a skill não detectou problemas suficientes ou a refatoração falhou, ajuste os arquivos de referência e execute novamente. É normal precisar de 2-4 iterações.

## Critérios de Aceite

A skill deve atingir os seguintes mínimos em **todos os 3 projetos**:

| Critério | Requisito |
|---|---|
| Fase 1 detecta stack corretamente | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 encontra >= 5 findings | OBRIGATÓRIO (3/3 projetos) |
| Fase 2 inclui pelo menos 1 CRITICAL ou HIGH | OBRIGATÓRIO (3/3 projetos) |
| Fase 3 aplicação funciona após refatoração | OBRIGATÓRIO (3/3 projetos) |

**IMPORTANTE:** Todos os critérios devem ser atingidos nos 3 projetos, não apenas em um!

> **Sobre o projeto 3 (task-manager-api):** Este projeto já possui alguma organização. "aplicação funciona" significa que a API inicia sem erros e todos os endpoints continuam respondendo corretamente.

## Referências

- [Claude Code: Skills](https://docs.anthropic.com/en/docs/claude-code/skills) — Documentação oficial sobre como criar e estruturar Skills
- [Claude Code: Overview](https://docs.anthropic.com/en/docs/claude-code/overview) — Visão geral do Claude Code e suas capacidades
- [The Complete Guide to Building Skills for Claude (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Guia completo da Anthropic sobre construção de Skills
- [Equipping Agents for the Real World with Agent Skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) — Blog oficial da Anthropic sobre Agent Skills

---

## Dicas Finais

- **Comece pela análise manual** — entender os problemas profundamente é essencial para criar uma skill que os detecte.
- **O SKILL.md é um prompt** — ele instrui o agente sobre o que fazer, enquanto os arquivos de referência fornecem o conhecimento de domínio.
- **Seja específico nos sinais de detecção** — "código ruim" não ajuda; "query SQL dentro de loop for" é acionável.
- **Teste incrementalmente** — não tente criar a skill perfeita de primeira.
- **A skill deve ser copiável** — se ela só funciona em um projeto específico, está acoplada demais. Teste nos 3 projetos para validar.
- **Projetos diferentes exigem adaptação** — a Fase 3 de um projeto já parcialmente organizado não vai ter as mesmas transformações de um monolito. Sua skill deve se adaptar ao contexto.
- **Pedir confirmação na Fase 2 é obrigatório** — o humano deve revisar o relatório antes de qualquer modificação.
- **Consulte as referências do curso** — revise a documentação oficial da ferramenta escolhida e os materiais das aulas para relembrar a estrutura e anatomia de uma skill.

## Análise Manual

A leitura abaixo foi feita antes da refatoração. A skill não contém esses projetos: eles só serviram para decidir quais sinais o catálogo precisava reconhecer em qualquer stack.

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

O catálogo cobre o que a análise manual mostrou de fato, não uma lista genérica de “código ruim”: SQL concatenado, segredo literal, dado sensível na resposta, God class, regra na borda HTTP, operação sensível sem controle, estado global, criptografia fraca, N+1, validação duplicada, API deprecated, número mágico, nome opaco e código morto. A detecção de API deprecated tem substituto moderno (`datetime.utcnow()` → `datetime.now(timezone.utc)`, `new Buffer()` → `Buffer.from()`, e o equivalente quando a stack for outra). Operação sensível não fica só no relatório: o playbook tem o padrão de controle de acesso, e a Fase 3 do `SKILL.md` manda corrigir o finding em vez de preservar a rota anônima.

A skill fica agnóstica porque nenhum reference cita estes três diretórios, nenhum fluxo assume Flask ou Express como único alvo, e a Fase 3 manda preservar o entry point e o contrato HTTP do projeto em que ela foi invocada. Exemplos em duas linguagens existem para o agente generalizar, não para limitar.

O ponto difícil foi separar o procedimento da árvore concreta. Um monólito Flask e um Express em memória não podem receber a mesma pasta `src/`. A guideline manda completar a camada que falta quando o projeto já tem `models/` e `routes/`, que foi o caso do task manager. O outro ponto foi corrigir vazamento (senha, cartão, SQL arbitrário) sem mudar método, caminho e status que os clientes já usam.

## Resultados

A Fase 2 parou para confirmação nos três relatórios. A execução deste desafio seguiu para a Fase 3 porque o pedido era entregar o refactor completo.

### Contagem da auditoria

- Projeto 1 — CRITICAL 4, HIGH 2, MEDIUM 2, LOW 2 (10). Relatório em `reports/audit-project-1.md`.
- Projeto 2 — CRITICAL 2, HIGH 2, MEDIUM 2, LOW 2 (8). Relatório em `reports/audit-project-2.md`.
- Projeto 3 — CRITICAL 2, HIGH 2, MEDIUM 2, LOW 2 (8). Inclui `datetime.utcnow()` como API deprecated. Relatório em `reports/audit-project-3.md`.

Projetos 1 e 2 não usavam API obsoleta. O relatório registra isso em vez de inventar um finding.

### Estrutura antes e depois

Projeto 1 saiu de `app.py`, `controllers.py`, `models.py` e `database.py` para `config/`, `models/` por domínio, `controllers/` por domínio, `views/routes.py`, `middlewares/error_handler.py` e `app.py` como composition root.

Projeto 2 saiu de `src/app.js`, `src/AppManager.js` e `src/utils.js` para `src/config/`, `src/models/`, `src/controllers/`, `src/routes/`, `src/middlewares/errorHandler.js` e `src/app.js`. O banco continua em memória.

Projeto 3 manteve `models/`, `routes/`, `services/` e `utils/`. Entrou `config/settings.py`, `controllers/` e `middlewares/error_handler.py`. As rotas ficaram finas.

### Checklist de validação

#### Projeto 1

### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável) — nenhuma encontrada
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
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

### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável) — nenhuma encontrada (`Buffer.from` já era o substituto moderno)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
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

### Fase 1 — Análise
- [x] Linguagem detectada corretamente
- [x] Framework detectado corretamente
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (se aplicável)
- [x] Skill pausa e pede confirmação antes da Fase 3

### Fase 3 — Refatoração
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