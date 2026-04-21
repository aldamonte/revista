import anthropic
import requests
import os
from datetime import datetime
import pytz

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────
tz = pytz.timezone('America/Sao_Paulo')
agora = datetime.now(tz)
data_formatada = agora.strftime('%d/%m/%Y')
dia_semana = [
    'Segunda-feira', 'Terça-feira', 'Quarta-feira',
    'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo'
][agora.weekday()]

print(f"[{agora.strftime('%H:%M')}] Iniciando geração — {dia_semana}, {data_formatada}")

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
1. Busque as 10 notícias mais relevantes e recentes de hoje nas categorias:
   IA/Tecnologia, Mercado Financeiro Brasil, Agronegócio Digital,
   Gestão de Pessoas/RH, Liderança Executiva
2. Priorize fontes: MIT Technology Review, Harvard Business Review, Anthropic,
   OpenAI, Bloomberg Tech, Exame, MIT Sloan Brasil, Embrapa,
   Nord Investimentos, CNN Brasil
3. Cada notícia deve ter: manchete impactante, resumo 3-4 linhas preservando
   a essência, análise de impacto estratégico para líderes de engenharia,
   e link para a fonte original
4. No ticker financeiro use os valores reais do dia
   (Ibovespa, USD/BRL, Selic Focus, IPCA, Petróleo)
5. Use o design da Revista Executiva de Tecnologia:
   - Fundo: #f5f0e8 (creme)
   - Tipografia editorial com Georgia
   - Seções com cores distintas por tema
   - Cards com bordas sutis
   - Destaque principal (lead story) em fundo escuro #2e3f52
   - Ticker bar em fundo preto
   - Rodapé em fundo preto
6. HTML auto-contido com todos os estilos em tag <style> no <head>
7. Comece com <!DOCTYPE html> e termine com </html>"""

print("Chamando Claude Opus 4.6 com web_search...")

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=8000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    system=PROMPT_SISTEMA,
    messages=[{"role": "user", "content": PROMPT_USUARIO}]
)

# ── 2. EXTRAI O HTML ───────────────────────────────────────────────
html_content = ""
for block in response.content:
    if block.type == "text":
        text = block.text.strip()
        # Remove possíveis blocos markdown que o modelo possa incluir
        text = text.replace("```html", "").replace("```", "").strip()
        if "<!DOCTYPE" in text or "<html" in text:
            html_content = text
            break
        html_content += text

if not html_content or "<html" not in html_content:
    raise ValueError(
        f"HTML inválido gerado pelo Claude.\n"
        f"Primeiros 500 chars da resposta: {str(response.content)[:500]}"
    )

print(f"✅ HTML gerado com sucesso — {len(html_content):,} caracteres")

# ── 3. SALVA O index.html ──────────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ index.html salvo no repositório")
print(f"🎉 Script concluído em {datetime.now(tz).strftime('%H:%M:%S')}")

# Nota: a notificação no Telegram é feita diretamente pelo step do GitHub Actions
# após o commit/push, garantindo que só notifica quando tudo funcionou.
