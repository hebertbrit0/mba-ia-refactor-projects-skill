# Guidelines de arquitetura MVC

As responsabilidades são fixas. O layout de pastas muda com o framework detectado e com o que o repositório já tem.

## Responsabilidades

| Camada | Faz | Não faz |
|---|---|---|
| Model | Lê e grava dados, mapeia linha/documento para estrutura, esconde o SQL ou a query do ORM | Não conhece HTTP, status code nem formato de erro da API |
| View / Route | Registra método e caminho, lê input, chama o controller, devolve status e body | Não calcula regra de negócio nem acessa o banco |
| Controller | Orquestra um caso de uso: valida entrada, chama models, aplica regra, decide o resultado | Não monta SQL e não é um arquivo único para o sistema inteiro |
| Config | Expõe opções lidas do ambiente (segredo, porta, caminho do banco, debug) | Não contém literal de produção |
| Error handler | Converte falha inesperada em resposta estável e registra a causa no log | Não devolve stack trace nem `str(erro)` ao cliente |
| Entry point | Compõe config, banco, rotas e handler e sobe o processo | Não declara regra de domínio |

## Regra de adaptação

1. Leia a árvore atual antes de criar pasta.
2. Se já existem `models/`, `routes/`, `controllers/` ou o equivalente do framework, preencha a camada que falta e mova código para ela.
3. Se tudo está em poucos arquivos, crie as pastas no idioma da stack (veja o mapa). Não embrulhe um projeto Python em pastas de Java.
4. Preserve o entry point que o manifesto já aponta (`main`, `scripts.start`, `python app.py`), ou atualize o manifesto no mesmo passo.
5. Um controller por domínio (recurso ou caso de uso coeso), não um controller por função.
6. Módulos de apoio que o projeto já usa (`services/`, `utils/`) continuam, desde que não virem um segundo god class. Notificação e hash podem viver ali se o controller apenas os chama.

## Mapa ilustrativo

O mapa mostra onde cada responsabilidade costuma morar. Stack ausente: escolha o equivalente mais próximo e siga as responsabilidades da tabela.

| Stack | Model | Route / View | Controller | Config | Entry point |
|---|---|---|---|---|---|
| Flask | módulo ou `db.Model` em `models/` | `add_url_rule` ou `Blueprint` em `views/` ou `routes/` | funções em `controllers/` | `config/settings.py` lendo `os.environ` | `app.py` chama `create_app()` |
| Django | `models.py` do app | `urls.py` | view/controller em módulo próprio, sem ORM na url | `settings.py` com `env` | `manage.py` / `wsgi.py` |
| FastAPI | módulo de persistência | `APIRouter` | funções de caso de uso injetadas na rota | objeto `Settings` (env) | `main.py` |
| Express | módulos em `models/` ou repositório | `Router` em `routes/` | funções em `controllers/` | `config/settings.js` lendo `process.env` | `app.js` ou `server.js` |
| NestJS | provider de persistência | controller HTTP fino | service de caso de uso | `ConfigModule` | `main.ts` |
| Spring Boot | `@Entity` + repositório | — | `@RestController` fino + `@Service` | `application.yml` e env | classe `@SpringBootApplication` |
| Laravel | Eloquent em `app/Models` | `routes/api.php` | `app/Http/Controllers` | `.env` + `config/` | `public/index.php` |
| Rails | `app/models` | `config/routes.rb` | `app/controllers` | `config/` + credentials | `config.ru` |
| ASP.NET | entidades + repositório | minimal route ou controller route | controller + service | `appsettings` + env | `Program.cs` |
| Gin / Echo | pacote de repositório | registro de rotas | handler que chama o caso de uso | pacote `config` | `main.go` |

## Contrato externo

Refatorar por dentro. Por fora, método e caminho permanecem. O corpo de sucesso permanece, exceto campo que vaza senha, segredo ou cartão. Finding de segurança da Fase 2 muda o status de quem chama sem credencial: operação sensível sem token ou sessão responde 401, e ação privilegiada sem permissão responde 403. Preservar o status anônimo antigo não é parte do contrato.

Comando de validação é o do projeto (`npm start`, `python app.py`, `go run`, `dotnet run`, `php artisan serve`). Não troque de framework para "facilitar" a validação.

## O que não fazer

- Não gerar a árvore de uma stack dentro de outra.
- Não mover código de um projeto parcialmente organizado para um layout de tutorial se as pastas atuais já expressam o idioma do framework.
- Não adicionar dependência nova quando a plataforma já oferece hash, env e data.
- Não declarar a Fase 3 concluída sem boot e sem chamada aos endpoints que existiam antes.
