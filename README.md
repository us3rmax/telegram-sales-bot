# Telegram Sales Bot

Bot privado para monitorizar mensagens de vendas e novos fãs num canal/bot de origem e enviar notificações através de outro bot do Telegram.

## Configuração

Defina as variáveis `API_ID`, `API_HASH`, `MY_BOT_TOKEN`, `SOURCE_BOT` e `SESSION_NAME`. Consulte `.env.example` como modelo. O ficheiro de sessão `*.session` é deliberadamente ignorado pelo Git e não deve ser publicado.

## Execução local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

A primeira execução pode exigir autenticação da sessão Telethon. Depois, o processo permanece ligado, monitoriza o `SOURCE_BOT` e envia o relatório diário às 23:59.

## Railway

No Railway, configure as mesmas variáveis como variáveis privadas do serviço. Para executar o bot, use o comando `python bot.py`. Como o ficheiro de sessão contém autenticação, não o coloque no GitHub; utilize um volume persistente ou injete a sessão de forma segura no ambiente de execução.

## Segurança

As credenciais que estavam no ficheiro original foram removidas desta versão. Como foram expostas durante a preparação, recomenda-se revogar e recriar o token do bot e, se necessário, regenerar as credenciais da API do Telegram antes de colocar o serviço online.
