# Tech Challenge - Fase 1: Plataforma "ToggleMaster"

Bem-vindo à primeira fase do Tech Challenge do curso de DevOps! Neste projeto, construiremos uma plataforma de *Feature Flag as a Service* chamada **ToggleMaster**.

## 📖 Cenário

A **DevOps Solutions Inc.** precisa de uma forma para que seus times de desenvolvimento possam lançar novas funcionalidades de forma segura e controlada. A solução é o **ToggleMaster**, uma plataforma interna que permitirá ativar ou desativar features em produção sem a necessidade de um novo deploy.

Nesta primeira fase, nosso foco é criar e implantar o MVP (Produto Mínimo Viável) da plataforma, que consiste em uma API monolítica simples para gerenciar as *feature flags*.

## 🎯 Objetivos da Fase 1

O objetivo principal é aplicar os conceitos fundamentais de DevOps e Cloud. Ao final desta fase, você deverá ser capaz de:

- Analisar uma aplicação monolítica e discutir suas vantagens e desvantagens.
- Desenhar uma arquitetura de nuvem inicial para uma aplicação web na AWS.
- Provisionar manualmente recursos essenciais na AWS (VPC, EC2, RDS, Security Groups).
- Realizar o deploy de uma aplicação, configurando a conexão com um banco de dados externo.
- Compreender e aplicar práticas básicas de segurança na AWS (IAM, Security Groups).

## 🛠️ Pré-requisitos

Antes de começar, garanta que você tenha:

- [Docker](https://www.docker.com/products/docker-desktop/) e Docker Compose instalados.
- Uma conta na [AWS Academy](https://awsacademy.instructure.com/) (você também pode usar o [Free Tier](https://aws.amazon.com/free/) para a maioria das tarefas).
- Um cliente de API como [Postman](https://www.postman.com/) ou [Insomnia](https://insomnia.rest/), ou conhecimento em `curl`.

### Instalando o Docker

Escolha o guia para o seu sistema operacional.

#### 🐧 Para Linux (Ubuntu, Debian, CentOS)

O método mais simples é usar o script de conveniência oficial do Docker.

1.  **Baixe o script de instalação:**
    ```bash
    curl -fsSL [https://get.docker.com](https://get.docker.com) -o get-docker.sh
    ```
2.  **Execute o script para instalar o Docker:**
    ```bash
    sudo sh get-docker.sh
    ```
3.  **Adicione seu usuário ao grupo do Docker (Passo Pós-Instalação Importante):**
    Para poder executar comandos `docker` sem precisar usar `sudo` toda vez, adicione seu usuário ao grupo `docker`.
    ```bash
    sudo usermod -aG docker $USER
    ```
    > **Atenção:** Após executar o comando acima, você precisa **fazer logout e login novamente** na sua sessão (ou reiniciar a máquina) para que a alteração tenha efeito.

#### 🪟 Para Windows ou 🍏 Para macOS

A forma recomendada é instalar o **Docker Desktop**, que é uma aplicação gráfica que inclui o Docker Engine, o `docker compose` e outras ferramentas.

1.  Acesse a página oficial e baixe o instalador: **[Docker Desktop](https://www.docker.com/products/docker-desktop/)**
2.  Siga as instruções do instalador gráfico. Ele cuidará de toda a configuração para você.

> **Nota sobre o `docker-compose`:** As versões mais recentes do Docker (instaladas pelos métodos acima) já vêm com o `docker compose` como um plugin. O comando moderno é `docker compose` (com espaço). A versão antiga, `docker-compose` (com hífen), está sendo descontinuada. Este projeto usará a sintaxe moderna.

---

## 🚀 Como Executar Localmente (com Docker)

Para facilitar o desenvolvimento, o projeto está configurado para rodar com Docker Compose. Ele irá subir a aplicação e um banco de dados MySQL com um único comando.

1.  **Clone o repositório:**
    ```bash
    git clone <url-do-seu-repositorio>
    ```

2.  **Navegue até a pasta do projeto:**
    ```bash
    cd toggle-master-monolith
    ```

3.  **Construa e inicie os contêineres:**
    ```bash
    docker-compose up --build
    ```

4.  **Verifique se a aplicação está no ar:**
    Abra um novo terminal e execute o seguinte comando `curl`:
    ```bash
    curl http://localhost:5000/health
    ```
    Você deve receber a seguinte resposta:
    ```json
    {
      "status": "ok"
    }
    ```

5.  **Para encerrar a execução:**
    No terminal onde o `docker-compose` está rodando, pressione `Ctrl + C`. Em seguida, para garantir que os contêineres e a rede sejam removidos, execute:
    ```bash
    docker-compose down
    ```

### Endpoints da API

Você pode usar o Postman ou `curl` para interagir com a API rodando localmente (`http://localhost:5000`) ou na sua instância EC2 (`http://<ip-publico-ec2>:5000`).

| Método | Endpoint                    | Body (Exemplo)                           | Descrição                      |
| :----- | :-------------------------- | :--------------------------------------- | :------------------------------- |
| `POST` | `/flags`                    | `{"name": "new-feature", "is_enabled": true}` | Cria uma nova feature flag.      |
| `GET`  | `/flags`                    | N/A                                      | Lista todas as flags existentes. |
| `GET`  | `/flags/<nome-da-flag>`     | N/A                                      | Retorna o status de uma flag.    |
| `PUT`  | `/flags/<nome-da-flag>`     | `{"is_enabled": false}`                  | Atualiza o status de uma flag.   |

#### Exemplos com `curl`

Abra seu terminal e utilize os comandos abaixo para interagir com a API.

**1. Criar uma nova flag (`new-feature`)**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"name": "new-feature", "is_enabled": true}' \
  http://localhost:5000/flags
```

**Saída esperada:** 
```bash
{
  "message": "Flag 'new-feature' created successfully"
}
```

**2. Listar todas as flags:**
```bash
curl -X GET http://localhost:5000/flags
```

**Saída esperada:** 
```bash
[
  {
    "is_enabled": true,
    "name": "new-feature"
  }
]
```

**3. Consultar uma flag específica (`new-feature`):**
```bash
curl -X GET http://localhost:5000/flags/new-feature
```

**Saída esperada:** 
```bash
{
  "is_enabled": true,
  "name": "new-feature"
}
```

**4. Atualizar uma flag (desativar a `new-feature`):**
```bash
curl -X PUT \
  -H "Content-Type: application/json" \
  -d '{"is_enabled": false}' \
  http://localhost:5000/flags/new-feature
```

**Saída esperada:** 
```bash
{
  "message": "Flag 'new-feature' updated"
}
```

## 💻 O Desafio

Sua missão é pegar esta aplicação monolítica e implantá-la na AWS. O ambiente local com Docker serve para você entender e testar a aplicação, mas a entrega final deve ser a aplicação rodando na nuvem.

**Suas tarefas são:**

1.  **Análise da Aplicação:** Estude o arquivo `app.py` e os demais arquivos para entender a estrutura básica de como a aplicação funciona, principalmente o `Dockerfile` e `Docker compose`.
2.  **Arquitetura na Nuvem:** Desenhe a arquitetura de implantação e estime os custos.
3.  **Deploy Manual na AWS:** Crie a infraestrutura (EC2, RDS, etc.) e siga o guia de instalação abaixo para implantar a aplicação.

---

## ⚙️ Guia de Instalação e Deploy na EC2

Este guia assume que você já criou uma instância EC2 e um banco de dados RDS, e que consegue se conectar à sua EC2 via SSH.

> **Importante:** Lembre-se de configurar o **Security Group** da sua instância EC2 para permitir tráfego de entrada na porta `5000` (para a aplicação) e na porta `22` (para o SSH). O Security Group do RDS deve permitir tráfego na porta `3306` vindo do Security Group da sua EC2.

Escolha a opção correspondente ao sistema operacional da sua instância EC2.

### Opção A: Para Amazon Linux 2 ou Amazon Linux 2023

1.  **Atualize o sistema e instale as ferramentas:**
    ```bash
    sudo yum update -y
    sudo yum install -y git python3 python3-pip
    ```

2.  **Clone o repositório do seu projeto:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd toggle-master-monolith
    ```

3.  **Crie e ative um ambiente virtual para o Python:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # Seu prompt do terminal deve mudar, indicando que o ambiente virtual está ativo.
    ```

4.  **Instale as dependências da aplicação:**
    ```bash
    pip install -r requirements.txt
    ```

### Opção B: Para Ubuntu Server 20.04 / 22.04 LTS

1.  **Atualize o sistema e instale as ferramentas:**
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y git python3-pip python3-venv
    ```

2.  **Clone o repositório do seu projeto:**
    ```bash
    git clone <url-do-seu-repositorio>
    cd toggle-master-monolith
    ```

3.  **Crie e ative um ambiente virtual para o Python:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    # Seu prompt do terminal deve mudar, indicando que o ambiente virtual está ativo.
    ```

4.  **Instale as dependências da aplicação:**
    ```bash
    pip install -r requirements.txt
    ```

---

### Executando a Aplicação (Comandos iguais para ambos os sistemas)

Após instalar as dependências, siga estes passos para configurar e rodar a aplicação.

1.  **Exporte as variáveis de ambiente:**
    A aplicação precisa saber como se conectar ao banco de dados RDS. Execute os comandos `export` abaixo, substituindo os valores pelos dados do seu RDS.

    > **⚠️ AVISO DE SEGURANÇA:** Estes comandos armazenam as credenciais apenas na sessão atual do terminal. **NUNCA** salve suas senhas e endpoints diretamente no código ou em scripts versionados no Git!

    ```bash
    export DB_HOST='<aqui-vai-o-endpoint-do-seu-rds>'
    export DB_NAME='<nome-do-banco-de-dados-que-voce-criou>'
    export DB_USER='<usuario-admin-do-rds>'
    export DB_PASSWORD='<senha-do-usuario-admin>'
    ```

2.  **Inicie a aplicação com Gunicorn:**
    Gunicorn é um servidor WSGI recomendado para produção. O comando `0.0.0.0` faz com que a aplicação escute em todas as interfaces de rede da EC2, tornando-a acessível publicamente.

    ```bash
    gunicorn --bind 0.0.0.0:5000 app:app
    ```

3.  **Verifique o acesso:**
    A aplicação estará rodando. Agora você pode acessá-la usando o IP Público ou o DNS Público da sua instância EC2, seguido da porta `5000`.
    Exemplo: `http://54.207.111.222:5000/health`

> **Nota:** O comando `gunicorn` acima executa a aplicação no *foreground*. Se você fechar sua sessão SSH, a aplicação irá parar. Em um ambiente de produção real, usaríamos um gerenciador de processos como `systemd` para rodar a aplicação como um serviço, mas para este desafio, rodar no foreground é suficiente.

### Alternativa: Executando em Produção com Docker

Se preferir rodar a aplicação em um contêiner na EC2 (em vez do Gunicorn direto no host), use o `docker-compose.prod.yaml`. Diferente do `docker-compose.yaml` de desenvolvimento, ele não sobe um banco de dados local: a aplicação se conecta a um MySQL externo (o seu RDS), e o código roda a partir da imagem construída (sem *bind mount* do diretório local).

A aplicação suporta duas formas de obter as credenciais do banco:

- **AWS Secrets Manager (recomendado):** defina `DB_SECRET_NAME` (e `AWS_REGION`) — a aplicação busca `host`, `port`, `dbname`, `username` e `password` diretamente do secret via `boto3`, usando a IAM Role da instância EC2. Nenhuma senha fica em texto plano no `.env`.
- **Variáveis de ambiente tradicionais:** se `DB_SECRET_NAME` não estiver definida, a aplicação usa `DB_HOST`/`DB_PORT`/`DB_NAME`/`DB_USER`/`DB_PASSWORD` normalmente (mesmo comportamento de antes).

#### Configurando o AWS Secrets Manager

1.  **Crie o secret no Secrets Manager** (tipo "Credentials for RDS database" ou um secret genérico) com as chaves `host`, `port`, `dbname`, `username` e `password` apontando para o seu RDS. Anote o nome/ARN do secret (ex.: `togglemaster-prd-db-credentials`).

2.  **Crie uma IAM Role para a EC2** com uma política permitindo `secretsmanager:GetSecretValue` restrita ao ARN do secret criado, e associe essa Role à instância EC2 (via *Instance Profile*).

3.  **Ajuste o hop limit do IMDS**, necessário para que um contêiner Docker (que adiciona um salto de rede) consiga acessar as credenciais da IAM Role via metadata service:
    ```bash
    aws ec2 modify-instance-metadata-options \
      --instance-id <id-da-instancia> \
      --http-put-response-hop-limit 2 \
      --http-endpoint enabled
    ```

4.  **Crie o arquivo `.env`** a partir do `.env.example`, preenchendo `DB_SECRET_NAME` e `AWS_REGION` (deixe os campos da Opção 2 comentados/vazios):
    ```bash
    cp .env.example .env
    ```
    > **⚠️ AVISO DE SEGURANÇA:** O `.env` já está no `.gitignore`. Nunca versione esse arquivo com credenciais reais — com Secrets Manager, ele nem precisa conter senhas.

5.  **Suba a aplicação:**
    ```bash
    docker compose -f docker-compose.prod.yaml up -d --build
    ```

6.  **Verifique o acesso:**
    ```bash
    curl http://localhost:5000/health
    ```

---

## 🤖 Deploy Automático via GitHub Actions (OIDC + SSM)

Além do deploy manual acima, o repositório tem um workflow
(`.github/workflows/deploy.yml`) que atualiza a aplicação na EC2
automaticamente a cada push na `main` (ou sob demanda via
`workflow_dispatch`). Ele não usa SSH nem access keys: o workflow assume,
via **OIDC**, uma IAM Role temporária e envia o comando de deploy
(`git pull` + `docker compose up --build`) para a instância através do
**AWS Systems Manager (SSM) Run Command**.

### Pré-requisitos

1.  A IAM Role de deploy precisa existir — ela é criada pelo Terraform do
    repositório [`fiap-aws-toggle-master-deploy-role`](https://github.com/Aws-Fiap/fiap-aws-toggle-master-deploy-role).
    Siga o README daquele repositório para aplicá-lo (`ec2_instance_id` da
    sua instância) e obter o ARN da role.
2.  A instância EC2 precisa ter o **SSM Agent** rodando e um **IAM
    Instance Profile** com a policy gerenciada `AmazonSSMManagedInstanceCore`
    anexado (permite a instância receber comandos do SSM — isso é
    independente da IAM Role de Secrets Manager já usada pela aplicação).
3.  O código já deve estar clonado num diretório da instância (com
    `git remote` apontando para este repositório) e o `.env` já
    configurado, como descrito nas seções acima.
4.  Crie o GitHub Environment `production` em **Settings → Environments**
    (é o que a trust policy da IAM Role exige) e, em **Settings → Secrets
    and variables → Actions → Variables**, configure:
    - `AWS_DEPLOY_ROLE_ARN` = ARN gerado pelo `fiap-aws-toggle-master-deploy-role`.
    - `AWS_REGION` = `us-east-1` (opcional — é o default do workflow).
    - `EC2_INSTANCE_ID` = ID da instância (ex.: `i-0123456789abcdef0`).
    - `APP_DIR` = caminho absoluto do código na instância (ex.: `/home/ec2-user/toggle-master-monolith`).

Com isso configurado, todo push na `main` roda, na instância: `docker
compose -f docker-compose.prod.yaml down --remove-orphans` (derruba e
remove o container em execução, se houver), `git reset --hard
origin/main` e `docker compose -f docker-compose.prod.yaml up -d
--build` (recria o container com o código novo). No final, o workflow faz
um health check em `GET /health` para confirmar que o deploy funcionou.

---

## 딜 Entregáveis da Fase 1

Você deve entregar os seguintes itens:

1.  **Vídeo de Demonstração (até 15 minutos):**
    - Apresentação rápida da aplicação rodando localmente com Docker.
    - Explicação do seu diagrama de arquitetura para a AWS.
    - Demonstração da aplicação rodando na EC2, provando que está conectada ao RDS.
    - Mostre as configurações de Security Group que garantem a segurança do ambiente.

2.  **Documentação:**
    - Link para o seu diagrama de arquitetura ([Miro](https://miro.com/), [Diagrams.net](https://app.diagrams.net/), etc.).

3.  **Relatório de Entrega (`ENTREGA.md` ou `.pdf`):**
    - Nomes dos participantes.
    - Link para o vídeo e para a documentação.
    - Resumo dos desafios encontrados e das decisões tomadas.

## 💡 Dicas e Pontos de Atenção

- **⚠️ SEGURANÇA:** Nunca, jamais, suba suas chaves de acesso da AWS para o seu repositório Git.
- **💸 CUSTOS:** Fique atento aos recursos que você cria na AWS. Utilize o *AWS Academy* ou *Free Tier* sempre que possível e **lembre-se de desligar ou remover os recursos** após a avaliação do desafio.
- **📝 DOCUMENTAÇÃO:** Uma boa documentação é parte crucial da cultura DevOps. Descreva suas escolhas e justifique-as.

Boa sorte!