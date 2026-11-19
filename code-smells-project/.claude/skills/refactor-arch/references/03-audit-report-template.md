# Template de relatório de auditoria

Use este formato na Fase 2. Preencha stack, projeto e contagens com o resultado da Fase 1. Não deixe placeholder na saída.

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome do diretório analisado>
Stack:   <linguagem> + <framework>
Files:   <N> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [CRITICAL] <título curto>
File: <caminho relativo>:<linha ou intervalo>
Description: <o que o código faz>
Impact: <consequência concreta>
Recommendation: <qual padrão do playbook aplicar>

### [HIGH] <título curto>
File: <caminho>:<linhas>
Description: ...
Impact: ...
Recommendation: ...

### [MEDIUM] <título curto>
File: <caminho>:<linhas>
Description: ...
Impact: ...
Recommendation: ...

### [LOW] <título curto>
File: <caminho>:<linhas>
Description: ...
Impact: ...
Recommendation: ...

Deprecated APIs: <finding já listado acima, ou "nenhuma encontrada nesta varredura.">

================================
Total: <n> findings
================================
```

Regras:

- Ordenação fixa: CRITICAL, depois HIGH, MEDIUM e LOW. Dentro da mesma severidade, o mais grave primeiro.
- `File` usa caminho relativo à raiz do projeto analisado e linhas reais.
- Cada finding referencia um anti-pattern do catálogo pelo comportamento, não por um número solto.
- O total é a soma das quatro severidades.
- Depois do relatório, imprima a pergunta de confirmação e pare:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
