---
name: refactor-arch
description: Analisa qualquer codebase, audita anti-patterns de arquitetura, segurança e qualidade com severidade e localização exata, e refatora para MVC na stack detectada. Use quando o usuário pedir /refactor-arch, auditoria arquitetural ou refatoração para MVC.
---

# refactor-arch

Skill agnóstica de tecnologia. Funciona em qualquer linguagem e framework. Os exemplos nos arquivos de referência ilustram o método; não são uma lista fechada de stacks suportadas.

Se a stack detectada não aparecer nos exemplos, infira o equivalente: camada de dados, camada HTTP, fluxo da aplicação, configuração e tratamento de erro. Recusar o trabalho porque a stack "não é suportada" é falha desta skill.

Não presuma nomes de projeto, domínio de negócio nem layout de pastas. Descubra tudo a partir do repositório em que a skill foi invocada.

## Antes de agir

Leia, nesta ordem, e aplique:

1. `references/01-project-analysis.md`
2. `references/02-antipattern-catalog.md`
3. `references/03-audit-report-template.md`
4. `references/04-mvc-guidelines.md`
5. `references/05-refactor-playbook.md`

## Fase 1 — Análise

Não modifique arquivos.

1. Detecte linguagem, framework, dependências, banco e domínio com as heurísticas do reference 01.
2. Mapeie a arquitetura atual: monólito, camadas parciais ou MVC já presente.
3. Conte os arquivos de código-fonte analisados.
4. Imprima exatamente este bloco, preenchido com o que foi detectado (sem valor default de linguagem ou framework):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:     <framework e versão, se houver>
Dependencies:  <dependências relevantes>
Domain:        <domínio inferido das rotas, entidades e tabelas>
Architecture:  <descrição curta da organização atual>
Source files:  <N> files analyzed
DB:            <banco, tabelas ou "não detectado">
================================
```

## Fase 2 — Auditoria

Não modifique arquivos.

1. Cruze o código com o catálogo de anti-patterns. Procure o sinal portátil e, em seguida, o equivalente na stack detectada.
2. Cada finding precisa de severidade, título, arquivo e linhas exatas, descrição, impacto e recomendação.
3. Ordene CRITICAL, HIGH, MEDIUM, LOW.
4. Inclua API deprecated quando existir uso obsoleto, com o substituto moderno daquela stack. Se não houver, registre isso em uma linha no relatório.
5. Imprima o relatório no formato do reference 03.
6. Pare. Pergunte, e não continue sem resposta explícita:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Qualquer coisa diferente de confirmação clara (`y`, `yes`, `sim`) encerra a skill sem alterar arquivos.

## Fase 3 — Refatoração

Só começa depois da confirmação da Fase 2.

1. Escolha o layout MVC a partir das convenções da stack detectada (reference 04). Se o projeto já tiver camadas, complete o que falta. Não imponha uma árvore de outra stack.
2. Aplique os padrões do playbook (reference 05) traduzidos para a stack detectada. Não copie sample de outra linguagem.
3. Preserve método, caminho e o corpo de sucesso das rotas. Isso não preserva comportamento inseguro que a Fase 2 apontou. Todo finding CRITICAL e HIGH é corrigido no código. Operação sensível sem autenticação passa a exigir o token ou a sessão que o login deste projeto emite. Sem credencial a resposta é 401. Com credencial e sem permissão, 403. Deixar a rota anônima porque o contrato legado era anônimo é falha da Fase 3. Segredo não vaza. SQL arbitrário não executa.
4. Extraia configuração do código-fonte. Centralize o tratamento de erro. Deixe um entry point que só compõe as peças. O middleware de acesso fica na borda HTTP e chama o controller só depois de aceitar a credencial.
5. Valide:
   - a aplicação sobe com o comando de start do próprio projeto, sem erro de import ou de boot;
   - os endpoints originais respondem: os públicos como antes; os sensíveis com 401 sem credencial e com o status de sucesso quando a credencial é válida;
   - o token devolvido pelo login é lido por pelo menos uma rota que a Fase 2 marcou como sem controle de acesso;
   - os anti-patterns CRITICAL e HIGH tratados não permanecem no código alterado.
6. Imprima:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore resultante>

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```

Se a validação falhar, corrija e valide de novo antes de declarar a fase concluída. Não marque sucesso com endpoint quebrado ou com a aplicação sem subir.
