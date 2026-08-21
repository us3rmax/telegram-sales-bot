# Telegram Sales Bot

Bot privado para monitorizar mensagens de vendas e novos fãs num canal/bot de origem e enviar notificações através de outro bot do Telegram.

## Configuração

Defina as variáveis `API_ID`, `API_HASH`, `MY_BOT_TOKEN`, `SOURCE_BOT` e `SESSION_STRING`. Consulte `.env.example` como modelo. A `SESSION_STRING` é uma representação segura da sessão Telethon e deve ser configurada como variável privada.

## Execução local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot.py
```

O processo inicia sem interação através da `SESSION_STRING`, permanece ligado, monitoriza o `SOURCE_BOT` e envia o relatório diário às 23:59.

## Railway

No Railway, configure `API_ID`, `API_HASH`, `MY_BOT_TOKEN`, `SOURCE_BOT` e `SESSION_STRING` como variáveis privadas do serviço. Para executar o bot, use o comando `python bot.py`. Não é necessário carregar o ficheiro `.session` no Railway, porque a sessão é fornecida pela `SESSION_STRING`.

## Segurança

As credenciais que estavam no ficheiro original foram removidas desta versão. Como foram expostas durante a preparação, recomenda-se revogar e recriar o token do bot e, se necessário, regenerar as credenciais da API do Telegram antes de colocar o serviço online.
