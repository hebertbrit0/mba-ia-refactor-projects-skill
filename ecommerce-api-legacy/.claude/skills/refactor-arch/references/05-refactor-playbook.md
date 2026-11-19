# Playbook de refatoração

Cada padrão descreve o problema, a responsabilidade alvo, os passos e como preservar o contrato. Os samples mostram duas linguagens. Traduza o padrão para a stack detectada. Não cole um sample Python dentro de um projeto Go, Java, PHP ou C#.

Ordem sugerida: segredo e SQL primeiro, depois separação de camadas, depois performance e legibilidade. Valide o boot ao final, não no meio de um arquivo que não importa.

## 1. Query concatenada para parâmetro

Problema: entrada entra na string SQL. Alvo: model. Contrato: o mesmo filtro devolve os mesmos registros; o endpoint de SQL arbitrário passa a responder erro estável e não executa.

Passos: escreva a SQL com placeholder do driver; passe valores em sequência ou mapa; cubra ramos dinâmicos com lista de cláusulas e lista de parâmetros, sem interpolar o valor.

```python
# antes
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
# depois
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```

```javascript
// antes
db.get("SELECT * FROM users WHERE email = '" + email + "'")
// depois
db.get("SELECT * FROM users WHERE email = ?", [email])
```

Equivalente: `$1` no Postgres (Go, Java, Node `pg`), `:id` no SQLAlchemy text, `?` no SQLite e no JDBC quando o driver usa positional.

## 2. Configuração para fora do fonte

Problema: segredo e porta literais. Alvo: config, lida pelo entry point. Contrato: a app sobe com default seguro de desenvolvimento (porta, path de banco). Segredo de produção não tem default literal.

Passos: crie um módulo de config; leia ambiente; use o módulo em um único lugar; apague o literal dos handlers e do health check.

```python
# antes
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
# depois
class Settings:
    secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    port = int(os.environ.get("PORT", "5000"))
```

```javascript
// antes
const config = { paymentGatewayKey: "pk_live_1234567890abcdef", port: 3000 };
// depois
const config = {
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "",
  port: Number(process.env.PORT || 3000),
};
```

Equivalente: `os.Getenv` em Go, `@Value` / env no Spring, `.env` carregado pelo mecanismo da stack (não commitar o arquivo de segredo).

## 3. God class para MVC por domínio

Problema: um arquivo faz schema, SQL, regra e rotas. Alvo: model, controller e route. Contrato: mesmos caminhos e status.

Passos: liste os domínios (substantivos das rotas); extraia SQL para um model por domínio; extraia o caso de uso para um controller; deixe a route como registro; o entry point só compõe. Apague o arquivo antigo quando ninguém mais importar.

```python
# antes — um módulo importa banco, valida e formata todos os recursos
def criar_pedido():
    dados = request.get_json()
    cursor.execute("INSERT INTO pedidos ... " + str(dados["usuario_id"]))

# depois
# views/routes.py registra o caminho
# controllers/pedido_controller.py valida e orquestra
# models/pedido_model.py executa o INSERT parametrizado
```

```javascript
// antes
class AppManager {
  setupRoutes(app) {
    app.post("/api/checkout", (req, res) => { /* sql + pagamento + http */ });
  }
}
// depois
// routes/index.js -> checkoutController.checkout -> models
```

Equivalente: extrair `@RestController` gordo para service + repository; extrair controller Laravel que contém `DB::select` para action + model.

## 4. Senha e serializer sem segredo

Problema: senha em claro, hash fraco, ou senha no JSON. Alvo: model (hash) e controller (o que entra na resposta). Contrato: login com a senha do seed continua válido; o campo de senha some da resposta.

Passos: troque o hash pela função de senha da plataforma; grave o hash no seed; compare com a função de verificação; monte o DTO público sem `password`, `senha`, `pass`, `secret`.

```python
# antes
self.password = hashlib.md5(pwd.encode()).hexdigest()
return {"email": self.email, "password": self.password}
# depois
from werkzeug.security import generate_password_hash, check_password_hash
self.password = generate_password_hash(pwd)
return {"email": self.email}
```

```javascript
// antes
function badCrypto(pwd) {
  let hash = "";
  for (let i = 0; i < 10000; i++) hash += Buffer.from(pwd).toString("base64").substring(0, 2);
  return hash.substring(0, 10);
}
// depois
const crypto = require("crypto");
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString("hex");
  const hash = crypto.scryptSync(String(password), salt, 32).toString("hex");
  return `${salt}:${hash}`;
}
```

Equivalente: `BCryptPasswordEncoder` (Spring), `password_hash` / `password_verify` (PHP), `has_secure_password` (Rails), `bcrypt` (qualquer stack que já dependa dele).

## 5. N+1 para uma consulta

Problema: query por item do loop. Alvo: model. Contrato: o JSON agrupado (pedido com itens, curso com alunos) mantém os mesmos campos.

Passos: escreva um `JOIN` ou eager load; agrupe em memória por id pai; não dispare consulta dentro do `for`.

```python
# antes
for pedido in pedidos:
    itens = cursor.execute("SELECT * FROM itens WHERE pedido_id = " + str(pedido["id"]))
# depois
rows = cursor.execute(
    """
    SELECT p.id, i.produto_id, pr.nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    """
).fetchall()
```

```javascript
// antes
courses.forEach((course) => {
  db.all("SELECT * FROM enrollments WHERE course_id = ?", [course.id], () => {});
});
// depois
const rows = await all(db, `
  SELECT c.id, c.title, e.id AS enrollment_id, u.name, p.amount, p.status
  FROM courses c
  LEFT JOIN enrollments e ON e.course_id = c.id
  LEFT JOIN users u ON u.id = e.user_id
  LEFT JOIN payments p ON p.enrollment_id = e.id
`);
```

Equivalente: `joinedload` / `selectinload` (SQLAlchemy), `include` (Prisma, Sequelize), `JOIN FETCH` (JPA), `with` (Eloquent), `Preload` (Gorm).

## 6. Estado global para dono explícito

Problema: conexão ou cache em variável de módulo. Alvo: entry point injeta; request fecha. Contrato: os dados sobrevivem como o projeto já prometia (arquivo, memória volátil, servidor). Não troque `:memory:` por arquivo se o boot depende do banco nascer vazio e semeado.

Passos: abra a conexão no composition root ou no escopo do request; passe o handle aos models; remova cache global que ninguém lê.

```python
# antes
db_connection = None
def get_db():
    global db_connection
    db_connection = sqlite3.connect(path, check_same_thread=False)
# depois
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
    return g.db
```

```javascript
// antes
let globalCache = {};
function logAndCache(key, data) { globalCache[key] = data; }
// depois
// o controller registra auditoria no banco; não há objeto mutável de módulo
```

Equivalente: pool injetado (Spring, ASP.NET, Go), request-scoped session (Django, SQLAlchemy scoped_session).

## 7. Erro centralizado

Problema: cada handler tem `except Exception` e devolve a mensagem interna. Alvo: error handler. Contrato: validação continua respondendo 400 com a mensagem de negócio; falha inesperada vira 500 genérico.

Passos: apague os `except` nus dos controllers; registre um handler no entry point; logue a exceção no servidor.

```python
# antes
except Exception as e:
    return jsonify({"erro": str(e)}), 500
# depois
@app.errorhandler(Exception)
def handle_unexpected(err):
    if isinstance(err, HTTPException):
        return err
    app.logger.exception(err)
    return jsonify({"erro": "Erro interno", "sucesso": False}), 500
```

```javascript
// antes
} catch (err) { res.status(500).send(err.message); }
// depois
function errorHandler(err, req, res, next) {
  console.error(err);
  if (res.headersSent) return next(err);
  res.status(500).send("Erro interno");
}
```

Equivalente: `@ControllerAdvice` (Spring), exception handler do Laravel, middleware de erro do Gin.

## 8. API deprecated para substituto moderno

Problema: chamada obsoleta espalhada. Alvo: um helper ou a chamada nova no próprio ponto. Contrato: o instante gravado continua UTC; comparação com coluna sem fuso não pode passar a lançar `TypeError`.

Passos: substitua pela API vigente; se o driver devolve data ingênua, normalize em uma função só.

```python
# antes
criado = datetime.utcnow()
# depois
def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)
```

```javascript
// antes
const buf = new Buffer(payload);
// depois
const buf = Buffer.from(payload);
```

Equivalente: troque o símbolo marcado `@Deprecated` pelo método citado no javadoc; no PHP, troque `mysql_*` por PDO. Não deixe a chamada velha "por compatibilidade" ao lado da nova.

## 9. Efeito colateral e regra para fora do god method

Problema: o handler de checkout ou pedido faz pagamento, estoque, e-mail e SQL. Alvo: controller chama funções pequenas; model persiste. Contrato: a ordem observável permanece (não grave o usuário se o curso não existe, se essa era a ordem; não confirme pagamento recusado).

Passos: nomeie os passos do caso de uso; extraia decisão de negócio (status do pagamento, limiar de desconto) para função com nome; persista numa transação; não logue dado sensível.

```python
# antes
print("ENVIANDO EMAIL: ...")
print("ENVIANDO SMS: ...")
cursor.execute("INSERT INTO pedidos ... " + str(usuario_id))
# depois
pedido_id = pedido_model.salvar(usuario_id, total, itens)
notificar_pedido_criado(pedido_id, usuario_id)
```

```javascript
// antes
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
let status = cc.startsWith("4") ? "PAID" : "DENIED";
// depois
const PAID_CARD_PREFIX = "4";
function paymentStatus(cardNumber) {
  return cardNumber.startsWith(PAID_CARD_PREFIX) ? "PAID" : "DENIED";
}
```

Equivalente: application service (Spring, .NET) chamado pelo controller; action única no Laravel. A rota não fica com o fluxo.

## 10. Validação única

Problema: criar e atualizar copiam os mesmos `if`. Alvo: uma função usada pelos dois controllers (ou o helper que já existe e está morto). Contrato: mesmas mensagens e status de validação.

Passos: mova os limites para constantes; uma função retorna dados limpos ou o erro; os dois fluxos a chamam; existência de entidade relacionada continua no caso de uso.

```python
# antes
if len(nome) < 2:
    return jsonify({"erro": "Nome muito curto"}), 400
# repetido no update
# depois
def validar_produto(dados):
    if len(dados["nome"]) < MIN_NOME:
        return None, "Nome muito curto"
    return dados_limpos, None
```

```javascript
// antes
if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");
// depois
function parseCheckout(body) {
  const userName = body.usr;
  const email = body.eml;
  const courseId = body.c_id;
  const cardNumber = body.card;
  if (!userName || !email || !courseId || !cardNumber) return { error: "Bad Request" };
  return { userName, email, password: body.pwd, courseId, cardNumber };
}
```

Equivalente: schema único (marshmallow, zod, bean validation, form request). Se a dependência já está no manifesto e o projeto tem um helper morto, use um dos dois, não os dois.

## 11. Integridade ao apagar agregado

Problema: `DELETE` do pai deixa filhos órfãos. Alvo: model, numa transação. Contrato: a rota continua respondendo sucesso quando o original respondia sucesso, inclusive se o id não existir e o original não checava.

Passos: apague (ou desvincule) os filhos na ordem que respeita a chave; depois o pai; commit único; rollback se um passo falhar.

```python
# antes
db.session.delete(user)  # tasks continuam com user_id
# depois
Task.query.filter_by(user_id=user_id).delete()
db.session.delete(user)
db.session.commit()
```

```javascript
// antes
db.run("DELETE FROM users WHERE id = ?", [id]);
// depois
await run(db, "BEGIN");
await run(db, "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)", [id]);
await run(db, "DELETE FROM enrollments WHERE user_id = ?", [id]);
await run(db, "DELETE FROM users WHERE id = ?", [id]);
await run(db, "COMMIT");
```

Equivalente: `ON DELETE CASCADE` declarado na migration, ou orphan removal do ORM. Não mude o status HTTP da rota.

## 12. Nome e número mágico

Problema: `u`, `cc`, `0.1`, `"4"`. Alvo: o módulo onde a regra mora. Contrato: o resultado numérico não muda.

Passos: renomeie para o conceito do payload; extraia limiar para constante nomeada no mesmo módulo da regra.

```python
# antes
if faturamento > 10000:
    desconto = faturamento * 0.1
# depois
DESCONTO_ALTO = (10000, 0.10)
limite, taxa = DESCONTO_ALTO
```

```javascript
// antes
let cc = req.body.card;
// depois
const cardNumber = req.body.card;
```

Equivalente: constante de pacote, enum, ou objeto de política. Não espalhe o mesmo literal em outro arquivo.
