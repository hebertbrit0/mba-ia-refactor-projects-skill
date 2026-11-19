# Análise de projeto

Procedimento de detecção. Os nomes abaixo são sinais, não um catálogo fechado. Se o repositório usar outra linguagem ou framework, aplique o mesmo método.

## Linguagem

1. Conte extensões de código-fonte (ignore dependências vendorizadas, `vendor/`, `node_modules/`, `.venv/`, `dist/`, `build/`).
2. Confirme com o manifesto:
   - `requirements.txt`, `pyproject.toml`, `Pipfile` → Python
   - `package.json` → JavaScript ou TypeScript (veja `typescript` nas deps ou arquivos `.ts`)
   - `go.mod` → Go
   - `pom.xml`, `build.gradle`, `build.gradle.kts` → Java ou Kotlin
   - `composer.json` → PHP
   - `Gemfile` → Ruby
   - `*.csproj`, `*.sln` → C#
   - `Cargo.toml` → Rust
3. A linguagem principal é a que concentra as rotas e o entry point, não a que tem mais arquivos de config.

## Framework

Procure, nesta ordem: dependência declarada no manifesto, import no entry point, decorators ou atributos de rota.

| Sinal no manifesto ou no import | Framework |
|---|---|
| `flask` | Flask |
| `django` | Django |
| `fastapi` | FastAPI |
| `express` | Express |
| `@nestjs/core` | NestJS |
| `spring-boot` | Spring Boot |
| `laravel/framework` | Laravel |
| `rails` | Ruby on Rails |
| `Microsoft.AspNetCore` | ASP.NET Core |
| `github.com/gin-gonic/gin` | Gin |
| `github.com/labstack/echo` | Echo |
| `actix-web`, `axum` | Actix ou Axum |

Leia a versão pinada no manifesto quando existir (`flask==3.1.1`, `"express": "^4.18.2"`). Se não houver versão, registre o nome sem inventar número.

Framework não listado: leia o entry point, identifique quem registra rotas e use esse nome.

## Banco de dados

Sinais, em qualquer stack:

- Driver ou ORM no manifesto (`sqlite3`, `psycopg`, `mysql2`, `mongoose`, `sqlalchemy`, `prisma`, `typeorm`, `gorm`, `sequelize`, `eloquent`).
- String de conexão ou caminho de arquivo (`sqlite:///`, `:memory:`, `postgres://`, `mongodb://`).
- SQL embutido (`CREATE TABLE`, `SELECT`, `INSERT`) ou migrations.
- Anotações de entidade (`@Entity`, `db.Model`, `ActiveRecord`).

Liste as tabelas ou coleções encontradas nos `CREATE TABLE`, models ou migrations. Se não houver persistência, escreva "não detectado".

## Domínio

Infira a partir de substantivos repetidos em rotas, tabelas, models e payloads. Exemplos de leitura, não de escopo:

- rotas `/produtos`, `/pedidos` e tabelas com esses nomes → API de comércio;
- rotas `/courses`, `/checkout` → API de cursos com pagamento;
- rotas `/tasks`, `/users` → API de tarefas.

Descreva o domínio em uma frase. Não reutilize a descrição de um projeto anterior.

## Arquitetura atual

Classifique com uma frase:

- **Monólito sem camadas:** regra de negócio, SQL e rotas nos mesmos poucos arquivos.
- **Camadas parciais:** existem pastas (`models`, `routes`, `services`, `utils`), mas uma responsabilidade está no lugar errado (rota com SQL e regra, model com HTTP, serviço com segredo).
- **MVC reconhecível:** model, rota/view e controller já separados; a auditoria procura buracos, não recria a árvore.

Conte arquivos de código-fonte da aplicação. Não conte lockfile, markdown, nem dependências instaladas.

## Saída

Preencha o bloco da Fase 1 só com fatos lidos do repositório. Versão, domínio e número de arquivos inventados invalidam a fase.
