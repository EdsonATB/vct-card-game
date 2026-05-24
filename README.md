# VCT Discord Bot

Bot de Discord de coleção de cartas de jogadores profissionais de Valorant.

O projeto usa comandos de barra do Discord para sortear jogadores, dar claim em cartas, visualizar inventário e consultar o valor global dos jogadores. Os valores das cartas são dinâmicos e aumentam conforme mais usuários fazem claim.

## Funcionalidades

- `/ping` testa a latencia do bot.
- `/roll` sorteia uma carta de jogador de Valorant.
- `/claim` adiciona uma carta ao inventário do usuário.
- `/inventario` mostra as cartas do usuário com paginação.
- `/players` lista jogadores cadastrados ordenados por valor.

## Economia

As cartas não possuem raridade fixa.

Todos os jogadores podem ser sorteados, e o valor de cada carta e calculado com base na quantidade de claims globais.

```text
valor = 100 + (total_claims * 3)
```

## Stack

- Python
- discord.py
- PostgreSQL
- Supabase
- asyncpg

## Estrutura

```text
vct-discord-bot/
  main.py
  bot/
    client.py
    config.py
    cogs/
      general.py
      rolls.py
      claims.py
      inventory.py
      players.py
    database/
      connection.py
      schema.sql
      seeds/
        valorant_players.csv
```

## Configuracao

Crie um arquivo `.env` na raiz do projeto:

```env
DISCORD_TOKEN=seu_token_do_discord
DATABASE_URL=sua_url_do_postgresql
COMMAND_PREFIX=!
SYNC_COMMANDS=true
```

## Banco de Dados

O projeto usa PostgreSQL.

Para criar as tabelas, rode o SQL em:

```text
bot/database/schema.sql
```

Para popular os jogadores, importe o CSV:

```text
bot/database/seeds/valorant_players.csv
```

A tabela principal de jogadores espera colunas como:

```text
nome
jogo
time_atual
imagem_url
total_claims
regiao
```

## Rodando Localmente

Instale as dependencias:

```bash
pip install -r requirements.txt
```

Rode o bot:

```bash
python main.py
```

O bot precisa estar rodando em algum ambiente para ficar online no Discord.

## Observacoes

Este projeto ainda esta em desenvolvimento.

Possíveis próximos passos:

- botões para claim direto no roll;
- filtros por região/time;
- perfil de usuário;
- ranking de colecionadores;
- melhorias visuais nos embeds;
- hospedagem 24/7.
