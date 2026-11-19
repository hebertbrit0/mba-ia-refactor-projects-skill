# Catálogo de anti-patterns

Cada item tem severidade, por que importa, sinal portátil e exemplos de sintaxe. Os exemplos não esgotam as linguagens. Ao auditar, procure o sinal portátil e traduza para a stack detectada.

Severidades:

- **CRITICAL:** quebra segurança, vaza dado sensível ou mistura de forma total persistência, regra e borda HTTP no mesmo tipo.
- **HIGH:** viola MVC ou SOLID a ponto de impedir teste e mudança localizada, ou protege mal um fluxo sensível.
- **MEDIUM:** duplicação, performance moderada, validação ausente, API obsoleta.
- **LOW:** legibilidade, nome opaco, número mágico, import morto.

## 1. SQL Injection — CRITICAL

Consulta montada por concatenação ou interpolação de entrada do usuário, ou endpoint que executa SQL recebido no body.

Sinais: `"SELECT ..." +`, `f"SELECT ... {id}"`, `` `SELECT ... ${id}` ``, `"WHERE nome = '" + termo`, query vinda de `req.body.sql` / `request.json["sql"]` passada a `execute`.

Exemplos:

```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```

```javascript
db.all("SELECT * FROM users WHERE name = '" + name + "'")
```

```java
stmt.executeQuery("SELECT * FROM accounts WHERE id = " + id);
```

Impacto: leitura e escrita arbitrárias no banco. Recomendação: parâmetro preparado (`?`, `$1`, named parameter) da API do driver. Endpoint de SQL livre deve deixar de executar e responder erro explícito.

## 2. Segredo hardcoded — CRITICAL

Credencial, chave de API, senha de banco ou `SECRET_KEY` literal no fonte.

Sinais: `SECRET_KEY = "..."`, `password = "..."`, `apiKey = "pk_live_..."`, `smtp` com senha no construtor, connection string com usuário e senha no arquivo commitado.

Impacto: qualquer pessoa com o repositório autentica como a aplicação. Recomendação: variável de ambiente lida na composição da app; ausência de segredo gera valor efêmero de desenvolvimento ou falha explícita, nunca um literal versionado.

## 3. Exposição de dado sensível — CRITICAL

Resposta HTTP, log ou health check devolve senha, hash, segredo, cartão ou token de produção.

Sinais: campo `password` / `senha` / `pass` em serializer; `secret_key` dentro de JSON de health; `console.log` / `print` do número do cartão ou da chave do gateway.

Impacto: vazamento direto para cliente ou para agregador de log. Recomendação: serializer público sem segredo; log com identificador, nunca com PAN ou chave.

## 4. God Class / God Method — CRITICAL

Um tipo ou função concentra schema, SQL, regra de negócio, formatação e registro de rotas de vários domínios.

Sinais: arquivo único com dezenas de funções de domínios diferentes; método `setupRoutes` / `init` que abre banco, faz seed e declara todas as rotas; classe com nome `Manager`, `Util`, `App` que importa tudo.

Impacto: não há teste isolado; qualquer mudança recompila o sistema inteiro. Recomendação: um model e um controller por domínio; a rota só delega.

## 5. Regra de negócio na camada errada — HIGH

A borda HTTP calcula desconto, estoque, pagamento ou política de status; ou o model devolve `Response` / `res.send`.

Sinais: `if estoque < quantidade` dentro do handler de rota junto com SQL; controller que abre conexão e monta SQL; model que importa o framework HTTP.

Impacto: a regra não roda fora do request e se duplica no próximo endpoint. Recomendação: model faz persistência; controller orquestra o caso de uso; rota traduz status e body.

## 6. Operação sensível sem controle de acesso — HIGH

Rota que apaga dados, lê relatório financeiro, reseta o banco ou executa SQL sem qualquer verificação de identidade.

Sinais: `/admin`, `/reset`, relatório financeiro ou `DELETE` de agregado sem leitura de credencial, sessão ou token.

Impacto: qualquer cliente na rede executa a operação. Recomendação: quando o contrato público legado exige que a rota continue anônima para não quebrar clientes, registre o finding e não invente um esquema de auth que mude o status das chamadas atuais. Quando a rota é claramente operacional (SQL arbitrário), desligue a capacidade perigosa e responda erro estável.

## 7. Estado global mutável — HIGH

Conexão, cache ou totalizador em variável de módulo, compartilhada entre requests.

Sinais: `db_connection = None` no módulo, `let globalCache = {}`, `public static List`, singleton escrito em todo request, `check_same_thread=False` para "consertar" o uso cruzado de threads.

Impacto: condição de corrida e vazamento de dados entre usuários. Recomendação: conexão por request ou injetada no composition root; cache explícito com dono, se ainda for necessário.

## 8. Criptografia fraca — HIGH

Senha em texto puro, MD5/SHA1 sem sal, ou hash caseiro.

Sinais: `hashlib.md5`, `crypto.createHash("md5")`, loop que fatia Base64 e chama isso de hash, coluna `senha` gravada com o valor do request.

Impacto: vazamento do banco revela todas as senhas. Recomendação: função de senha da plataforma (`werkzeug.security`, `crypto.scrypt`, `bcrypt`, `password_hash` do PHP, `BCryptPasswordEncoder`). Atualize o seed para gravar o hash. Não devolva o hash na API.

## 9. N+1 queries — MEDIUM

Consulta dentro de loop sobre o resultado de outra consulta.

Sinais: `for row in rows:` seguido de `execute` / `query.get` / `db.get`; `forEach` com `await` de um `SELECT` por item; serializer que acessa relação lazy por elemento.

Impacto: latência cresce com o tamanho da lista. Recomendação: `JOIN`, eager load (`joinedload`, `include`, `JOIN FETCH`) ou agregação única.

## 10. Duplicação e validação ausente — MEDIUM

A mesma regra copiada em criar e atualizar, `except:` nu, ou erro interno com `str(exception)` no JSON.

Sinais: blocos idênticos de `if len(nome)`, `except:` / `catch (e) { res.send(e.message) }`, helper de validação existente e não chamado.

Impacto: uma correção precisa ser repetida e o cliente recebe detalhe interno. Recomendação: uma função de validação; handler único que loga a exceção e responde mensagem genérica.

## 11. API deprecated — MEDIUM

Uso de API marcada como obsoleta na linguagem ou no framework, com substituto oficial.

Sinais e substitutos (procure o equivalente se a stack for outra):

| Uso obsoleto | Substituto |
|---|---|
| `datetime.utcnow()` / `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)` |
| `new Buffer()` | `Buffer.from()` |
| `url.parse` | `new URL()` / `URL.parse` |
| `request` (biblioteca Node descontinuada) | `fetch` ou o cliente HTTP mantido pelo framework |
| `mysql_query` (PHP) | PDO ou mysqli com parâmetro |
| APIs anotadas `@Deprecated` / `@deprecated` | o método indicado no aviso |

Impacto: a próxima versão da linguagem quebra o boot. Recomendação: trocar pelo substituto moderno. Se o banco devolve data sem fuso, normalize num único helper documentado, sem espalhar a API velha.

Se a varredura não achar API obsoleta, escreva no relatório: "Deprecated APIs: nenhuma encontrada nesta varredura."

## 12. Número mágico — LOW

Limiar de negócio literal no meio do cálculo.

Sinais: `if total > 10000: desconto = total * 0.1`, `startsWith("4")` como regra de pagamento sem nome, prioridade `<= 2` repetida sem constante.

Impacto: o leitor não sabe o que o número significa e a regra diverge entre cópias. Recomendação: constante nomeada no módulo da regra.

## 13. Nome opaco — LOW

Identificador de uma letra, ou nome que esconde a unidade.

Sinais: `u`, `e`, `p`, `cid`, `cc`, `tmp`, `data2` em fluxo de pagamento ou pedido.

Impacto: a auditoria e o próximo bug levam mais tempo. Recomendação: nome do conceito (`email`, `courseId`, `cardNumber`).

## 14. Código morto e import não usado — LOW

Import, função ou dependência declarada que ninguém chama.

Sinais: `import json, os, sys` sem uso; função de validação paralela à validação inline; biblioteca no manifesto ausente dos imports.

Impacto: ruído e falsa sensação de proteção (a lib "está lá", mas a rota não a usa). Recomendação: apagar o que não é chamado ou passar a chamá-lo de um único lugar. Não adicione framework novo só para justificar a dependência.

## Como reportar

Um finding por ocorrência lógica (não uma linha por concatenação idêntica no mesmo arquivo). Agrupe concatenações do mesmo arquivo num finding e cite o intervalo ou as linhas representativas. Arquivo e linha têm de ser os do código lido, não uma estimativa.
