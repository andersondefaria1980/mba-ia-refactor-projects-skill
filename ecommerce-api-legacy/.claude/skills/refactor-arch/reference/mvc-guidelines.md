# Guidelines de Arquitetura MVC Alvo (Fase 3)

Define a arquitetura para a qual todo projeto deve convergir na Fase 3, independente da stack. "MVC" aqui é usado no sentido de API backend (sem template rendering na maioria dos casos): **Model** (dados), **View** (nesse contexto, as rotas/serializers de resposta — não HTML), **Controller** (orquestração da regra de negócio).

## Estrutura de diretórios alvo

```
src/
├── config/           # configuração centralizada (env vars, constantes de app), zero segredo hardcoded
├── models/           # 1 arquivo por entidade/domínio — acesso a dados e regras intrínsecas à entidade
├── views/            # Flask: routes.py (ou 1 blueprint por domínio) | Express: routes/*.js
│   (ou routes/)      # define os endpoints HTTP e delega ao controller — sem lógica de negócio aqui
├── controllers/       # 1 arquivo por domínio — orquestra models + regra de negócio, chamado pelas views/routes
├── middlewares/        # error handler centralizado, auth, logging de request
└── app.py / app.js    # composition root: cria a app, registra config/middlewares/rotas, nada de lógica de negócio
```

Adapte os nomes de pasta à convenção idiomática da stack (`views/` costuma virar `routes/` em Express — tudo bem, o que importa é a responsabilidade, não o nome literal da pasta) — mas **não pule nenhuma das 5 responsabilidades** (config, models, views/routes, controllers, error handling centralizado) nem misture duas responsabilidades no mesmo arquivo.

## Responsabilidade de cada camada

### Config
- Toda credencial, string de conexão, chave de API, feature flag vem de variável de ambiente (`os.environ` / `process.env`), nunca literal no código.
- Um único ponto de leitura/validação da config (ex: `config/settings.py`, `config/index.js`), importado por quem precisar — não espalhar `os.getenv(...)` pelo projeto inteiro.
- Fornecer um `.env.example` (sem valores reais) documentando as variáveis esperadas.

### Models
- Um arquivo por entidade/domínio (ex: `produto_model.py`, `user_model.js`), não um `models.py` genérico de 300+ linhas.
- Responsável por: schema/estrutura da entidade, queries de acesso a dados (sempre parametrizadas — nunca concatenação de string), e regras de validação/cálculo que são intrínsecas ao dado (ex: `is_overdue()`, `total_price()`).
- **Não** deve conter: rotas HTTP, orquestração multi-entidade (isso é Controller), formatação de resposta HTTP.
- Se o projeto usa ORM, o Model é a classe do ORM + métodos de domínio nela; se usa SQL cru, o Model é o módulo com as funções de acesso a dados daquela entidade.

### Views / Routes
- Define o mapeamento HTTP (método + path) para uma função de Controller.
- Faz apenas: parsing básico da requisição (body/query/params), chamada ao Controller correspondente, formatação da resposta HTTP (status code + serialização).
- **Não** deve conter: acesso direto a banco, cálculo de regra de negócio, validação de regra de domínio (validação de formato de request é aceitável aqui; validação de regra de negócio pertence ao Controller/Model).

### Controllers
- Orquestra o fluxo: recebe dados já parseados da rota, chama um ou mais Models/serviços, aplica a regra de negócio de orquestração (ex: "verificar estoque, criar pedido, decrementar estoque, dentro de uma transação"), retorna um resultado estruturado para a View formatar.
- É a camada testável por excelência — deve poder ser testada sem subir um servidor HTTP.
- Se a lógica de negócio for complexa/reaproveitável entre controllers, extraia para uma camada de `services/` chamada pelo controller — mas garanta que ela seja realmente importada e usada (não crie uma camada morta).

### Middlewares / Error Handling
- Handler de erro centralizado (um único lugar que captura exceções não tratadas e formata a resposta de erro), em vez de cada rota ter seu próprio `try/except`/`try/catch` genérico que vaza mensagem de exceção crua.
- Auth (quando aplicável) como middleware/decorator reutilizável, não checagem manual repetida em cada handler.
- CORS restrito a origens conhecidas, não aberto por padrão.

### Entry point / Composition root
- Um único arquivo (`app.py`/`app.js`) que: lê config, instancia a app do framework, registra middlewares, registra rotas, e (só se executado diretamente) sobe o servidor.
- Não deve conter definição de rota inline nem lógica de negócio.

## Regras gerais de dependência entre camadas

```
Views/Routes → Controllers → Models
                    ↓
              Services (opcional)
```

- Uma camada só pode depender da(s) camada(s) abaixo dela nesse diagrama — nunca o inverso (Model não conhece Controller; Controller não conhece detalhes de formatação HTTP).
- Toda dependência externa pesada (conexão de banco, cliente HTTP) deve ser instanciada uma vez no composition root ou em `config/`, e passada/injetada para quem precisa — não instanciada ad-hoc dentro de cada função/classe.

## Adaptação a projetos parcialmente organizados

Se o projeto já tem pastas como `models/`, `routes/`, `services/`, `utils/` (caso do "task-manager-api" tipo de projeto), a Fase 3 **não recria a estrutura do zero** — ela corrige o que está errado dentro da estrutura existente:
- Move lógica de negócio que está na rota para o Controller/Service correto.
- Conecta camadas que existem mas nunca são chamadas (ex: um `NotificationService` nunca instanciado) — ou remove se genuinamente não fizer sentido para o domínio, documentando a decisão no relatório final.
- Elimina duplicação substituindo por chamada ao método/função já existente no Model/Service.
- Preserva os endpoints e contratos de resposta existentes — refatoração de arquitetura não deve mudar o comportamento observável da API.
