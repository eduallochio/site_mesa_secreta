# 📺 Configuração da API do YouTube

## Como obter a API Key e Channel ID

### 1. Obter YouTube API Key

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. No menu lateral, vá em **APIs e Serviços** > **Biblioteca**
4. Procure por **YouTube Data API v3**
5. Clique em **Ativar**
6. Vá em **APIs e Serviços** > **Credenciais**
7. Clique em **+ Criar Credenciais** > **Chave de API**
8. Copie a chave gerada
9. **(Recomendado)** Clique em **Restringir chave** e limite para **YouTube Data API v3**

### 2. Obter YouTube Channel ID

#### Método 1: Pelo Studio
1. Acesse [YouTube Studio](https://studio.youtube.com/)
2. Vá em **Configurações** > **Canal** > **Configurações avançadas**
3. Copie o **ID do canal**

#### Método 2: Pela URL do Canal
Se sua URL é: `https://www.youtube.com/channel/UC_x5XG1OV2P6uZZ5FSM9Ttw`

O Channel ID é: `UC_x5XG1OV2P6uZZ5FSM9Ttw`

#### Método 3: Pelo Handle (@)
Se você usa handle (ex: `@mesasecreta`):
1. Acesse: `https://www.youtube.com/@mesasecreta`
2. Clique com botão direito > **Ver código-fonte da página**
3. Procure por `"channelId":"` ou `"externalId":"`
4. O ID está logo após essas strings

### 3. Configurar no Admin

1. Acesse o painel admin: `/admin/`
2. Clique em **⚙️ Configurações do Site**
3. Expanda a seção **📺 Integração YouTube**
4. Cole a **API Key** e o **Channel ID**
5. Marque **"Usar Inscritos Automático do YouTube"**
6. Salve

## Funcionamento

### Modo Manual (Padrão)
- Você define manualmente o número de inscritos
- Atualização manual quando necessário

### Modo Automático
- Busca os inscritos diretamente da API do YouTube
- Atualização em tempo real a cada carregamento da página
- Se houver erro na API, usa o valor manual como fallback

## Verificação no Admin

Ao salvar as configurações, você verá:

✅ **Inscritos automáticos: X inscritos** - Tudo funcionando
❌ **Erro ao buscar inscritos** - Verifique API Key e Channel ID
⚠️ **Configuração incompleta** - Preencha API Key e Channel ID
📝 **Modo manual ativo** - Usando valor manual

## Limitações da API

- **Quota diária**: 10.000 unidades/dia (suficiente para milhares de requisições)
- **Custo por requisição**: 1 unidade para buscar estatísticas
- **Gratuito**: Sem cobrança dentro do limite

## Segurança

🔒 **IMPORTANTE**: Nunca exponha sua API Key publicamente!
- Não commite em repositórios públicos
- Use variáveis de ambiente em produção
- Restrinja a chave apenas para YouTube Data API

## Exemplo de Uso em Produção

```python
# settings.py
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Depois configure no admin ou via variável de ambiente
```

## Troubleshooting

### Erro 403: API Key inválida
- Verifique se a API Key está correta
- Confirme que a YouTube Data API v3 está ativada

### Erro 404: Channel ID não encontrado
- Confirme o Channel ID
- Use o método correto para obter o ID (não use o handle/@)

### Erro de Quota
- Você excedeu o limite diário de 10.000 unidades
- Aguarde até o reset (meia-noite Pacific Time)
- Considere usar cache para reduzir chamadas

## Suporte

Para mais informações:
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [Google Cloud Console](https://console.cloud.google.com/)
