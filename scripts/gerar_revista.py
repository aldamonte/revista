import anthropic
import requests
import os
from datetime import datetime
import pytz

# Fuso horário Brasil
tz = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(tz)
data_formatada = agora.strftime('%d/%m/%Y')
dia_semana = ['Segunda-feira','Terça-feira','Quarta-feira',
              'Quinta-feira','Sexta-feira','Sábado','Domingo'][agora.weekday()]

print(f"[{agora.strftime('%H:%M')}] Iniciando geração da Revista — {dia_semana}, {data_formatada}")

# ── 1. CHAMA O CLAUDE ──────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

PROMPT_SISTEMA = """Você é um curador executivo de notícias de tecnologia para uma 
profissional executiva sênior de engenharia de software baseada em São Paulo, Brasil. 
Gere uma revista diária HTML completa com 10 notícias em 5 seções: 
Inteligência Artificial, Mercado Financeiro, Agronegócio & TI, 
Gestão de Pessoas & RH, e Liderança Executiva.
Use web_search para buscar notícias reais e atuais do dia.
NUNCA invente notícias. Retorne APENAS o HTML completo, sem markdown."""

PROMPT_USUARIO = f"""Gere a Revista Executiva de Tecnologia para hoje, 
{dia_semana}, {data_formatada}.

INSTRUÇÕES:
1. Busque as 10 notícias mais relevantes e recentes de hoje
2. Priorize: MIT Tech Review, HBR, Anthropic, OpenAI, Bloomberg Tech, 
   Exame, MIT Sloan Brasil, Embrapa, Nord Investimentos, CNN Brasil
3. Cada notícia: manchete, resumo 3-4 linhas, impacto estratégico, link da fonte
4. Ticker financeiro com valores reais do dia (Ibovespa, USD/BRL, Selic, IPCA, Petróleo)
5. Use o design da Revista Executiva de Tecnologia com fundo #f5f0e8, 
   tipografia editorial, seções coloridas por tema
6. HTML auto-contido com <style> interno. Comece com <!DOCTYPE html>"""

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=8000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    system=PROMPT_SISTEMA,
    messages=[{"role": "user", "content": PROMPT_USUARIO}]
)

# Extrai o HTML da resposta
html_content = ""
for block in response.content:
    if block.type == "text":
        text = block.text.strip()
        text = text.replace("```html", "").replace("```", "").strip()
        if "<!DOCTYPE" in text or "<html" in text:
            html_content = text
            break
        html_content += text

if not html_content or "<html" not in html_content:
    raise ValueError(f"HTML inválido gerado. Resposta: {str(response.content)[:300]}")

print(f"✅ HTML gerado — {len(html_content)} caracteres")

# ── 2. SALVA O index.html ──────────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ index.html salvo")

# ── 3. ENVIA NO WHATSAPP via CallMeBot ────────────────────────────
phone    = os.environ.get("CALLMEBOT_PHONE", "")
apikey   = os.environ.get("CALLMEBOT_APIKEY", "")
url_site = "https://aldamonte.github.io/revista/"

if phone and apikey:
    mensagem = (
        f"📰 *Revista Executiva de Tecnologia*\n"
        f"{data_formatada} — Edição de hoje no ar!\n\n"
        f"🔗 {url_site}\n\n"
        f"_Leitura em ~15 minutos_"
    )
    resp = requests.get(
        "https://api.callmebot.com/whatsapp.php",
        params={"phone": phone, "text": mensagem, "apikey": apikey},
        timeout=15
    )
    if resp.status_code == 200:
        print(f"✅ WhatsApp enviado para {phone}")
    else:
        print(f"⚠️ Erro no WhatsApp: {resp.status_code} — {resp.text[:100]}")
else:
    print("⚠️ Variáveis CALLMEBOT não configuradas — pulando envio")

print(f"🎉 Concluído em {datetime.now(tz).strftime('%H:%M:%S')}")
