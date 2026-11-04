# Gera <app>-termos.html (Termos de Serviço pt/en/es) a partir de cada <app>.html (política de privacidade).
# Uso: python3 scripts/gerar_termos.py [app ...]   (sem argumentos: todos os apps)
import html, os, re, sys

DATA = '04/11/2026'
SAUDE = {'vittali', 'dens', 'clinus'}
# jogos de festa para maiores de 18 (bebida, desafios)
FESTA = {'bottlespinner', 'challengecards', 'challengedice', 'dareparty', 'nightquests', 'pointfingers', 'potatoonfire', 'spicelevels'}

def limpa(t):
    t = re.sub(r'<[^>]+>', '', t)
    return html.unescape(re.sub(r'\s+', ' ', t)).strip()

def info(slug):
    s = open(f'{slug}.html', encoding='utf-8').read()
    h1 = limpa(re.search(r'<h1>(.*?)</h1>', s, re.S).group(1))
    nome = h1.split('—')[0].strip()
    if nome.lower().startswith('política'):
        nome = h1.split('—')[1].strip()
    estilo = re.search(r'<style>.*?</style>', s, re.S).group(0)
    # primeira frase que apresenta o app, na parte em português
    desc = ''
    for p in re.findall(r'<p>(.*?)</p>', s, re.S):
        t = limpa(p)
        if t.startswith(('O ', 'A ')) and nome in t:
            frase = re.split(r'(?<=[.!?])\s', t)[0]
            frase = re.sub(r',?\s*desenvolvid[oa] pela Nespoli Digital', '', frase).rstrip('.,; ')
            desc = frase + '.'
            break
    adulto = slug in FESTA
    plano = 'Premium' if 'Premium' in s else ('Pro' if 'Assinatura Pro' in s else '')
    return dict(slug=slug, nome=nome, estilo=estilo, desc=desc,
                premium=bool(plano), plano=plano, anuncios='AdMob' in s, adulto=adulto, saude=slug in SAUDE)

def pagina(a):
    n = html.escape(a['nome']); slug = a['slug']
    pt, en, es = [], [], []
    pt.append(f"<div class=\"card\"><p>Estes Termos de Serviço regem o uso do app <strong>{n}</strong>, desenvolvido pela <strong>Nespoli Digital</strong>. Ao instalar ou usar o app, você concorda com eles. Se não concordar, não use o app.</p></div>")
    sec = [
        ('O app', (html.escape(a['desc']) + ' ' if a['desc'] else '') +
         'O app funciona sem cadastro: não há conta de usuário e os dados que você registra ficam guardados no seu próprio aparelho.'),
        ('Seus dados e backups',
         'Você é responsável pelos dados que registra, inclusive dados de outras pessoas (como nomes e contatos), e por tratá-los conforme a Lei Geral de Proteção de Dados (LGPD). Como os dados ficam só no aparelho, desinstalar o app, limpar os dados ou perder o aparelho pode apagá-los: faça backups regulares pelos recursos do app. Veja também a <a href="' + slug + '.html">Política de Privacidade</a>.'),
        ('Uso permitido',
         'Você pode usar o app para fins pessoais ou profissionais lícitos. Não é permitido usá-lo para atividades ilegais, copiar, modificar, fazer engenharia reversa, revender ou distribuir o app, nem tentar burlar os limites do plano grátis ou a verificação da assinatura.'),
    ]
    if a['premium']:
        sec.append(('Assinatura ' + a['plano'],
         'Alguns recursos exigem a assinatura ' + a['plano'] + ', vendida pela Google Play, mensal ou anual, com renovação automática até ser cancelada. O preço é o mostrado na Google Play no momento da compra. Cancele quando quiser em Play Store &gt; Pagamentos e assinaturas; o acesso continua até o fim do período já pago. Pedidos de reembolso seguem as regras da Google Play, sem prejuízo dos seus direitos pelo Código de Defesa do Consumidor. Se a assinatura acabar, nenhum dado é apagado; apenas os recursos ' + a['plano'] + ' deixam de estar disponíveis.'))
    if a['anuncios']:
        sec.append(('Anúncios',
         'No plano grátis o app exibe anúncios não personalizados do Google AdMob. Não nos responsabilizamos pelo conteúdo, produtos ou serviços anunciados por terceiros.'))
    if a['adulto']:
        sec.append(('Maiores de 18 anos',
         'O app é destinado exclusivamente a maiores de 18 anos. A participação em qualquer desafio ou pergunta é sempre voluntária: respeite os limites de cada pessoa. Se houver álcool, beba com moderação e nunca dirija depois de beber.'))
    if a['saude']:
        sec.append(('Saúde e responsabilidade profissional',
         'O app é uma ferramenta de organização. Não é dispositivo médico, não faz diagnóstico, não substitui o julgamento clínico nem a orientação de um profissional de saúde, e não é prontuário com certificação digital ICP-Brasil. Quando usado por profissionais, cabe a eles a guarda dos registros pelo prazo legal e a validade dos documentos emitidos.'))
    sec += [
        ('Limitação de responsabilidade',
         'O app é fornecido "no estado em que se encontra". Cálculos, estimativas, documentos, modelos e sugestões são apenas apoio: confira sempre os resultados antes de usá-los em decisões, cobranças, compras, cortes ou documentos oficiais. Na máxima extensão permitida pela lei, a Nespoli Digital não responde por perdas de dados, lucros cessantes ou danos indiretos decorrentes do uso do app.'),
        ('Propriedade intelectual',
         'O app, sua marca, layout, código e conteúdos próprios pertencem à Nespoli Digital. Os dados que você registra continuam sendo seus.'),
        ('Alterações',
         'Podemos atualizar o app e estes Termos. A versão vigente fica sempre nesta página, com a data da última atualização. O uso do app após uma mudança significa que você concorda com a nova versão.'),
        ('Lei aplicável',
         'Estes Termos seguem as leis do Brasil. Fica assegurado ao consumidor o foro do seu domicílio.'),
        ('Contato', 'Nespoli Digital — <a href="mailto:nespolidigital@gmail.com">nespolidigital@gmail.com</a>'),
    ]
    for i, (t, c) in enumerate(sec, 1):
        pt.append(f'<h2>{i}. {t}</h2>\n  <p>{c}</p>')
    extra_en = []
    if a['premium']: extra_en.append(f'<li><strong>{a["plano"]}:</strong> an auto-renewing monthly or yearly Google Play subscription; cancel anytime in Play Store &gt; Payments &amp; subscriptions; access lasts until the end of the paid period; refunds follow Google Play rules and applicable consumer law. No data is deleted if the subscription ends.</li>')
    if a['anuncios']: extra_en.append('<li><strong>Ads:</strong> the free plan shows non-personalized Google AdMob ads; we are not responsible for third-party advertised content.</li>')
    if a['adulto']: extra_en.append('<li><strong>Adults only:</strong> the app is for people 18+. Participation is always voluntary. Drink responsibly and never drink and drive.</li>')
    if a['saude']: extra_en.append('<li><strong>Health:</strong> the app is an organization tool, not a medical device; it does not diagnose or replace clinical judgment, and is not a digitally certified health record.</li>')
    extra_es = []
    if a['premium']: extra_es.append(f'<li><strong>{a["plano"]}:</strong> suscripción mensual o anual de Google Play con renovación automática; cancela cuando quieras en Play Store &gt; Pagos y suscripciones; el acceso dura hasta el fin del período pagado; los reembolsos siguen las reglas de Google Play y la ley del consumidor aplicable. No se borra ningún dato si la suscripción termina.</li>')
    if a['anuncios']: extra_es.append('<li><strong>Anuncios:</strong> el plan gratuito muestra anuncios no personalizados de Google AdMob; no respondemos por el contenido anunciado por terceros.</li>')
    if a['adulto']: extra_es.append('<li><strong>Solo adultos:</strong> la app es para mayores de 18 años. La participación es siempre voluntaria. Bebe con moderación y nunca conduzcas después de beber.</li>')
    if a['saude']: extra_es.append('<li><strong>Salud:</strong> la app es una herramienta de organización, no un dispositivo médico; no diagnostica ni reemplaza el juicio clínico, y no es una historia clínica con certificación digital.</li>')
    nl = '\n    '
    return f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{n} — Termos de Serviço / Terms of Service</title>
{a['estilo']}
</head>
<body>
<main>
  <h1>{n} — Termos de Serviço / Terms of Service / Términos de Servicio</h1>
  <p>Última atualização / Last updated / Última actualización: {DATA}</p>
  <p><a href="#pt">Português</a> · <a href="#en">English</a> · <a href="#es">Español</a></p>

  <section id="pt">
  {(nl[:-2]).join(pt)}
  </section>

  <section id="en">
  <h2>English</h2>
  <p>These Terms of Service govern the use of <strong>{n}</strong>, by <strong>Nespoli Digital</strong>. By installing or using the app you agree to them.</p>
  <ul>
    <li><strong>No account:</strong> your data is stored only on your device. You are responsible for the data you enter (including third-party data) and for regular backups; uninstalling or clearing app data may delete it. See the <a href="{slug}.html#en">Privacy Policy</a>.</li>
    <li><strong>Permitted use:</strong> lawful personal or professional use only; no copying, reverse engineering, resale, or bypassing free-plan limits or subscription checks.</li>
    {nl.join(extra_en)}
    <li><strong>No warranty:</strong> the app is provided "as is". Calculations, estimates, documents and suggestions are aids only; always check them. To the extent permitted by law, Nespoli Digital is not liable for data loss or indirect damages.</li>
    <li><strong>Changes and law:</strong> we may update the app and these Terms; the current version is always on this page. Governed by the laws of Brazil, without prejudice to mandatory consumer rights in your country.</li>
    <li><strong>Contact:</strong> <a href="mailto:nespolidigital@gmail.com">nespolidigital@gmail.com</a></li>
  </ul>
  </section>

  <section id="es">
  <h2>Español</h2>
  <p>Estos Términos de Servicio rigen el uso de <strong>{n}</strong>, de <strong>Nespoli Digital</strong>. Al instalar o usar la app, aceptas estos términos.</p>
  <ul>
    <li><strong>Sin cuenta:</strong> tus datos se guardan solo en tu dispositivo. Eres responsable de los datos que registras (incluidos datos de terceros) y de hacer copias de seguridad; desinstalar o borrar los datos puede eliminarlos. Consulta la <a href="{slug}.html#es">Política de Privacidad</a>.</li>
    <li><strong>Uso permitido:</strong> solo uso personal o profesional lícito; no se permite copiar, hacer ingeniería inversa, revender ni eludir los límites del plan gratuito o la verificación de la suscripción.</li>
    {nl.join(extra_es)}
    <li><strong>Sin garantía:</strong> la app se ofrece "tal cual". Cálculos, estimaciones, documentos y sugerencias son solo apoyo; verifícalos siempre. En la medida permitida por la ley, Nespoli Digital no responde por pérdida de datos ni daños indirectos.</li>
    <li><strong>Cambios y ley:</strong> podemos actualizar la app y estos términos; la versión vigente está siempre en esta página. Se rigen por las leyes de Brasil, sin perjuicio de los derechos del consumidor de tu país.</li>
    <li><strong>Contacto:</strong> <a href="mailto:nespolidigital@gmail.com">nespolidigital@gmail.com</a></li>
  </ul>
  </section>

  <footer>© 2026 Nespoli Digital</footer>
</main>
</body>
</html>
'''

if __name__ == '__main__':
    apps = sys.argv[1:] or sorted(f[:-5] for f in os.listdir('.') if f.endswith('.html')
                                  and not f.endswith(('-exclusao.html', '-termos.html')) and f != 'index.html')
    for slug in apps:
        a = info(slug)
        open(f'{slug}-termos.html', 'w', encoding='utf-8').write(pagina(a))
        print(f"{slug}: {a['nome']} | premium={a['premium']} anuncios={a['anuncios']} 18+={a['adulto']} | {a['desc'][:70]}")
