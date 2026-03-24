"""
NEXTRIQ Discord v3.0 — Complete Server Setup
=============================================
Verbeterde structuur met:
- Ink Approved afdeling (eigen setters)
- NEXTRIQ Label / Platform afdeling (eigen setters)  
- Outreach afdeling (cold outreachers)
- Content & Marketing (creators + ambassadeurs samen, duidelijk gesplitst)
- Marketing Middelen prominente eigen plek
- Tech & Oplevering samengevoegd
- Franchise Boris kanaal
- Platform strategie kanaal
"""

import requests, os, time, sys

BOT_TOKEN = os.environ.get("BOT_TOKEN")
SERVER_ID  = os.environ.get("SERVER_ID")
BASE       = "https://discord.com/api/v10"
HEADERS    = {"Authorization": f"Bot {BOT_TOKEN}", "Content-Type": "application/json"}

# ─── API ──────────────────────────────────────────────────────────────────────

def api(method, endpoint, payload=None, retries=5):
    url = f"{BASE}{endpoint}"
    for attempt in range(retries):
        r = getattr(requests, method)(url, headers=HEADERS, json=payload)
        if r.status_code == 429:
            wait = r.json().get("retry_after", 2)
            print(f"  ⏳ Rate limit — wacht {wait}s...")
            time.sleep(float(wait) + 0.5)
            continue
        if r.status_code in (200, 201):
            return r.json()
        print(f"  ⚠️  {method.upper()} {endpoint} → {r.status_code}: {r.text[:200]}")
        return None
    return None

# ─── RECHTEN ──────────────────────────────────────────────────────────────────

VIEW      = 1024
SEND      = 2048
HIST      = 65536
REACT     = 64
ATTACH    = 32768
EMBED     = 16384
CONN      = 1048576
SPEAK     = 2097152
MGMSG     = 8192
ALL_TEXT  = VIEW | SEND | HIST | REACT | ATTACH | EMBED
READ_ONLY = VIEW | HIST | REACT

def allow(rid, p):    return {"id": rid, "type": 0, "allow": str(p), "deny": "0"}
def deny(rid, p=VIEW): return {"id": rid, "type": 0, "allow": "0", "deny": str(p)}
def ev_allow(ev):     return {"id": ev, "type": 0, "allow": str(ALL_TEXT), "deny": "0"}
def ev_deny(ev):      return {"id": ev, "type": 0, "allow": "0", "deny": str(VIEW)}

def create_role(name, color_hex, hoist=True, mentionable=True):
    res = api("post", f"/guilds/{SERVER_ID}/roles", {
        "name": name, "color": int(color_hex, 16),
        "hoist": hoist, "mentionable": mentionable
    })
    time.sleep(0.5)
    if res:
        print(f"  ✅ Rol: {name}")
        return res["id"]
    return None

def create_cat(name, pos, overwrites):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 4, "position": pos,
        "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"\n📁 {name}")
        return res["id"]
    return None

def ch(name, cat, topic, overwrites, ro=False):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 0, "parent_id": cat,
        "topic": topic, "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"  {'🔒' if ro else '  '} #{name}")
        return res["id"]
    return None

def vc(name, cat, overwrites):
    res = api("post", f"/guilds/{SERVER_ID}/channels", {
        "name": name, "type": 2, "parent_id": cat,
        "permission_overwrites": overwrites
    })
    time.sleep(0.5)
    if res:
        print(f"    🔊 {name}")

def pin(channel_id, content):
    msg = api("post", f"/channels/{channel_id}/messages", {"content": content})
    if msg:
        time.sleep(0.3)
        api("put", f"/channels/{channel_id}/pins/{msg['id']}")
        time.sleep(0.3)

def delete_all():
    channels = api("get", f"/guilds/{SERVER_ID}/channels")
    if channels:
        for c in channels:
            api("delete", f"/channels/{c['id']}")
            time.sleep(0.3)

# ═══════════════════════════════════════════════════════════════════════════════
def main():
    if not BOT_TOKEN or not SERVER_ID:
        print("❌ BOT_TOKEN of SERVER_ID ontbreekt")
        sys.exit(1)

    guild = api("get", f"/guilds/{SERVER_ID}")
    if not guild:
        print("❌ Server niet gevonden")
        sys.exit(1)

    ev = SERVER_ID
    print(f"\n🚀 NEXTRIQ Discord v3.0 — {guild['name']}\n")

    print("🧹 Opruimen...")
    delete_all()

    # ═══════════════════════════════════
    # ROLLEN
    # ═══════════════════════════════════
    print("\n🎭 ROLLEN AANMAKEN...")
    r = {}
    r["founder"]      = create_role("🚀 Founder",             "E67E22")
    r["headtech"]      = create_role("⚡ Head of Tech",           "27AE60")
    r["webdev"]       = create_role("💻 Head of Web Dev",      "1ABC9C")
    r["manager"]      = create_role("🛡️ Sales Manager",       "8E44AD")
    r["top_setter"]   = create_role("🏆 Top Setter",           "F1C40F")
    r["setter"]       = create_role("🎯 Setter",               "2980B9")
    r["new_setter"]   = create_role("🆕 Nieuwe Setter",        "95A5A6")
    r["ink_setter"]   = create_role("🖤 Ink Setter",           "2C2C2C")  # Ink Approved setters
    r["platform_set"] = create_role("🌐 Platform Setter",      "16A085")  # Vergelijkingssite setters
    r["outreacher"]   = create_role("📧 Outreacher",           "E74C3C")  # Cold outreachers
    r["closer"]       = create_role("🎯 Closer",               "C0392B")
    r["creator"]      = create_role("🎬 Creator",              "E91E8C")
    r["ambassador"]   = create_role("🌟 Ambassadeur",          "52BE80")
    r["bot"]          = create_role("🤖 NEXTRIQ Bot",          "5865F2", hoist=False)

    fo  = r["founder"]
    cf  = r["headtech"]
    mgr = r["manager"]
    wd  = cf  # Head of Tech = Head of Tech — zelfde niveau
    ts  = r["top_setter"]
    s   = r["setter"]
    ns  = r["new_setter"]
    ink = r["ink_setter"]
    ps  = r["platform_set"]
    out = r["outreacher"]
    cl  = r["closer"]
    cr  = r["creator"]
    amb = r["ambassador"]

    # Groepen
    mgmt        = [fo, cf, mgr, wd]
    leaders     = [fo, cf, mgr, wd]
    all_setters = [fo, mgr, ts, s, ns, out, ink, ps]
    all_sales   = [fo, cf, mgr, ts, s, ns, cl, out, ink, ps]
    intern_all  = [fo, cf, mgr, wd, ts, s, ns, cl, cr, out, ink, ps]
    tech_team   = [fo, cf, mgr, wd]
    content_cr  = [fo, mgr, cr]
    content_all = [fo, mgr, cr, amb]
    ink_team    = [fo, mgr, ink]
    plat_team   = [fo, mgr, ps]
    out_team    = [fo, mgr, out]

    print("\n📋 KANALEN AANMAKEN...")

    # ════════════════════════════════════════
    # 1. INFORMATIE
    # ════════════════════════════════════════
    cat = create_cat("📌 INFORMATIE", 0, [ev_allow(ev)])

    welkom_id = ch("welkom-en-regels", cat,
        "Welkomsttekst, serverregels, roluitleg en CRM-link. Altijd lezen bij onboarding.",
        [ev_allow(ev), deny(ev, SEND)], ro=True)

    aankondigingen_id = ch("aankondigingen", cat,
        "Officiële berichten van Founder en Manager. Zet notificaties aan voor dit kanaal.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    productupdates_id = ch("product-updates", cat,
        "Actuele producten en prijzen. Altijd checken voor een klantgesprek.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    systeemUpdates_id = ch("systeem-updates", cat,
        "Updates over CRM (crmoas.vercel.app), Discord, Zapier en tools.",
        [ev_allow(ev), deny(ev, SEND),
         allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    # ════════════════════════════════════════
    # 2. TEAM
    # ════════════════════════════════════════
    cat = create_cat("💬 TEAM", 1,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    teamchat_id = ch("team-chat", cat, "Algemeen teamkanaal voor iedereen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    beschikbaar_id = ch("beschikbaarheid", cat,
        "Dagelijks vóór 9:30 doorgeven. ✅ BESCHIKBAAR [uren] [focus] of ❌ NIET BESCHIKBAAR [reden].",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    vragen_id = ch("vragen-aan-manager", cat,
        "Alle vragen aan Kim komen HIER. Nooit in DM. Kim reageert binnen 4 uur op werkdagen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("wins-van-de-dag", cat,
        "Vier elke win — groot of klein. Deal, activatie, positieve reactie. Minimaal één per dag!",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    # ════════════════════════════════════════
    # 3. KENNIS & SCRIPTS
    # ════════════════════════════════════════
    cat = create_cat("🧠 KENNIS & SCRIPTS", 2,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ro_intern = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in intern_all] + \
                [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    scripts_id = ch("kennis-en-sales-scripts", cat,
        "Alle verkoopscripts per product + BANT+ protocol. Verplicht lezen voor elk gesprek.",
        ro_intern, ro=True)

    bezwaren_id = ch("bezwaren-behandeling", cat,
        "Hoe om te gaan met elk bezwaar per producttype. Te duur? Geen tijd? Hier staat het antwoord.",
        ro_intern, ro=True)

    ch("cta-bibliotheek", cat,
        "Alle goedgekeurde calls-to-action per product. Gebruik ALLEEN goedgekeurde CTAs.",
        ro_intern, ro=True)

    handboeken_id = ch("handboeken", cat,
        "Links naar alle handboeken: Setter, Closer, Creator, Ambassadeur, Manager + CRM handleiding.",
        ro_intern, ro=True)

    # ════════════════════════════════════════
    # 4. MARKETING MIDDELEN  ← EIGEN PROMINENTE CATEGORIE
    # ════════════════════════════════════════
    cat = create_cat("🎨 MARKETING MIDDELEN", 3,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ro_mkt = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in intern_all] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG), allow(cr, ALL_TEXT)]

    canva_id = ch("canva-templates", cat,
        "Alle goedgekeurde Canva-templates. Stories, Reels, carrousels, visitekaartjes. Gebruik alleen deze.",
        ro_mkt, ro=True)

    ch("goedgekeurde-links", cat,
        "Goedgekeurde Instagram/TikTok/LinkedIn links voor setters om te delen met prospects.",
        ro_mkt, ro=True)

    brand_id = ch("brand-assets", cat,
        "Logo's, kleuren (#1B2A4A navy, #6B3FA0 paars), fonts, huisstijlgids. Officiële NEXTRIQ branding.",
        ro_mkt, ro=True)

    ch("campagne-updates", cat,
        "Actieve campagnes en wekelijkse CTA-instructies. Welk product staat centraal? Check dit elke maandag.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr, s, ts]])

    ch("content-ideeen", cat,
        "Deel content-ideeën voor NEXTRIQ. Format: Platform | Idee | Doelgroep | Verwacht bereik.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    # ════════════════════════════════════════
    # 5. SALES — NEXTRIQ CORE
    # ════════════════════════════════════════
    cat = create_cat("📊 SALES & RESULTATEN", 4,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("crm-updates", cat,
        "⚡ ZAPIER — Automatisch: nieuwe lead in CRM. Niet handmatig posten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    dagrapport_id = ch("dagrapport", cat,
        "Verplicht vóór 18:00 elke werkdag. Format vastgepind. Geen rapport = niet geteld.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("leaderboard", cat,
        "⚡ ZAPIER — Elke vrijdag 16:00 automatisch: top 3 setters van de week.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in all_sales] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("booked-calls", cat,
        "⚡ ZAPIER — Automatisch: Calendly-afspraak ingepland. Closers: check dit elk uur.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("deals-gesloten", cat,
        "🔥 ⚡ ZAPIER — Deal gesloten. Reageer! Een team dat viert groeit.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    ch("betalingen-ontvangen", cat,
        "💰 ⚡ ZAPIER — Betaling ontvangen → commissie-teller loopt. Alleen management post handmatig.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in all_sales] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    noshows_id = ch("no-shows", cat,
        "Closer meldt no-show direct na gemiste afspraak. Format: Closer | Klant | Tijd | Reden | Actie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in all_sales])

    # ════════════════════════════════════════
    # 6. OUTREACH ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("📧 OUTREACH", 5,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team + [ts, s]])

    ro_out = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in out_team] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    outscripts_id = ch("outreach-scripts", cat,
        "Cold call scripts, email templates, LinkedIn-berichten. Alleen goedgekeurde scripts gebruiken.",
        ro_out, ro=True)

    ch("mijn-contacten", cat,
        "Outreacher logt elk nieuw contact. Format: Bedrijf | Contact | Methode | Status | Volgende actie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team])

    ch("leads-doorgestuurd", cat,
        "Als outreacher een contact omzet naar lead voor setter. Format: Bedrijf | Contact | Waarom doorgestuurd.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team + [s, ts]])

    dagout_id = ch("dagrapport-outreach", cat,
        "Dagrapport voor outreachers. Vóór 18:00. Format: Contacten benaderd | Reacties | Leads doorgezet | Pijnpunten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in out_team])

    ch("resultaten-outreach", cat,
        "⚡ ZAPIER — Wekelijks automatisch overzicht: contacten, conversie, top outreacher.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in out_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    # ════════════════════════════════════════
    # 7. INK APPROVED ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("🖤 INK APPROVED", 6,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ro_ink = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in ink_team] + \
             [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    inkinfo_id = ch("ink-info-en-scripts", cat,
        "Productinfo Ink Approved + scripts voor tatu-shops. Gratis (≤5) → €29/mnd upgrade.",
        ro_ink, ro=True)

    ch("ink-leads", cat,
        "Nieuwe tatu-shop leads loggen. Format: Shopnaam | Stad | Contact | Status | Setter.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-upgrades", cat,
        "⚡ ZAPIER — Automatisch: upgrade naar €29/mnd. Elke upgrade telt als recurring MRR.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in ink_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    inkdag_id = ch("ink-dagrapport", cat,
        "Dagrapport Ink Approved setters. Format: Shops benaderd | Reacties | Upgrades | Pijnpunten.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-klanten-actief", cat,
        "Overzicht alle actieve Ink Approved abonnementen. Kim bijwerkt bij elke upgrade/opzegging.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team])

    ch("ink-feedback", cat,
        "Klantfeedback en verbeterpunten voor Erik. 3+ dezelfde klacht = prioriteit voor product update.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in ink_team + [cf]])

    # ════════════════════════════════════════
    # 8. NEXTRIQ LABEL / PLATFORM ← NIEUW
    # ════════════════════════════════════════
    cat = create_cat("🌐 NEXTRIQ LABEL & PLATFORM", 7,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ro_plat = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in plat_team] + \
              [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT|MGMSG)]

    platinfo_id = ch("platform-info-en-doelen", cat,
        "Wat is het platform, wie benaderen we, targets en pitch. Verplicht lezen voor start.",
        ro_plat, ro=True)

    platpitch_id = ch("pitch-en-scripts", cat,
        "Scripts voor aanbieders benaderen. Pitch: gratis listing → betaald pakket → NEXTRIQ Label.",
        ro_plat, ro=True)

    ch("aanbieders-prospectie", cat,
        "Welke AI-bureaus/SaaS/consultants gaan we benaderen? Planning en taakverdeling per setter.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("aanbieders-pipeline", cat,
        "Status per aanbieder. Format: Aanbieder | Contact | Status (gratis/€99/€299/Label) | Setter | Datum.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("platform-deals", cat,
        "⚡ ZAPIER — Nieuwe betalende aanbieder op het platform. Elke betaling = recurring MRR.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in plat_team] +
        [allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("label-certificeringen", cat,
        "Aanbieders die NEXTRIQ Label hebben aangevraagd. Head of Tech + Saif keuren goed. Status bijhouden.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team + [cf]])

    platdag_id = ch("platform-dagrapport", cat,
        "Dagrapport platform setters. Format: Aanbieders benaderd | Reacties | Nieuwe listings | Upgrades.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team])

    ch("platform-bouwen", cat,
        "Head of Tech post updates over de platformbouw. Features live, bugs, roadmap wijzigingen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in plat_team + [cf]])

    # ════════════════════════════════════════
    # 9. CONTENT & CREATORS + AMBASSADEURS SAMEN
    # ════════════════════════════════════════
    cat = create_cat("🎬 CONTENT & CREATORS", 8,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr]])

    # --- Creators sectie ---
    ro_cr = [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] + \
            [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)]

    briefings_id = ch("content-briefings", cat,
        "Wekelijkse briefings van Founder — elke maandag. Alleen Founder post. Dit is jouw taak voor de week.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] +
        [allow(fo, ALL_TEXT|MGMSG)], ro=True)

    ch("content-planning", cat,
        "Weekplanning per creator. Wat maak je, wanneer gaat het live, welk product promoot je?",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_cr + [mgr]])

    ch("content-geplaatst", cat,
        "Screenshot + link zodra content live gaat. Format: Platform | Type | CTA | Link | Creator.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_all + [mgr]])

    ch("dm-opvolging", cat,
        "Creator meldt inkomende DMs voor setter. Format: Platform | Van wie | Inhoud | Urgentie.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in content_cr + [s, ts, mgr]])

    # --- Ambassadeurs sectie (in zelfde categorie maar eigen kanalen) ---
    ambregels_id = ch("amb-briefings-en-regels", cat,
        "Onboarding info + handboek link + campagne-instructies voor ambassadeurs. Lees dit eerst.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in content_all + [mgr]] +
        [allow(fo, ALL_TEXT|MGMSG), allow(mgr, ALL_TEXT)], ro=True)

    ch("amb-chat", cat,
        "Onderling overleg voor ambassadeurs. Vragen, samenwerking, content-ideeën delen.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb]])

    ch("amb-wins-en-resultaten", cat,
        "Vier je successen als ambassadeur! Leads via jouw kanaal, virale content, positieve reacties.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb, cr]])

    commissievr_id = ch("commissie-vragen", cat,
        "Vragen over commissieberekening of uitbetaling. Kim antwoordt binnen 2 werkdagen. Deadline rekening: 5e vd maand.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr, amb, cr]])

    ch("leaderboard-amb", cat,
        "⚡ ZAPIER — Maandelijks automatisch: top ambassadeurs op basis van omzet via hun kanaal.",
        [ev_deny(ev)] + [allow(x, READ_ONLY) for x in [fo, mgr, amb, cr]])

    # ════════════════════════════════════════
    # 10. TECH & OPLEVERING (samengevoegd)
    # ════════════════════════════════════════
    cat = create_cat("⚙️ TECH & OPLEVERING", 9,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    techvragen_id = ch("tech-vragen", cat,
        "Technische vragen voor Erik. Altijd hier, nooit in DM. Erik reageert binnen 1 werkdag.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in intern_all])

    ch("ai-agents", cat,
        "Updates over actieve AI agents in ontwikkeling. Versies, statuswijzigingen, livegang.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("automatiseringen", cat,
        "Documentatie alle Zapier/Make automatiseringen. Format: Naam | Trigger | Actie | Status.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("tech-demo-aanvragen", cat,
        "⚡ ZAPIER — AI Intelligence Scan aangevraagd. Erik en Founder handelen af.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team])

    ch("demo-aanvragen", cat,
        "⚡ ZAPIER — Website demo aangevraagd. Webdeveloper pakt dit op binnen 24 uur.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    onboarding_id = ch("klant-onboarding", cat,
        "Na deal: closer stuurt klantinfo + briefing naar webdeveloper. Format vastgepind.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("projecten-lopend", cat,
        "Overzicht actieve webprojecten. Webdeveloper bijwerkt wekelijks status.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    ch("opleveringen", cat,
        "Project afgerond. Na oplevering: upsell hosting €50/mnd aanbieden. Format: Klant | Project | Datum.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in tech_team + [cl]])

    # ════════════════════════════════════════
    # 11. ESCALATIE
    # ════════════════════════════════════════
    cat = create_cat("🚨 ESCALATIE", 10,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    for kanaal, topic in [
        ("maatwerk-goedkeuring",
         "Afwijkende prijs of scope. Closer vraagt aan — Founder keurt goed/af. NOOIT korting zonder goedkeuring hier."),
        ("betalingsproblemen",
         "Betalingsissues, chargebacks, openstaande facturen. Vertrouwelijk."),
        ("klachten-en-conflicten",
         "Klantklachten of interne conflicten. Strikt vertrouwelijk."),
        ("setter-problemen",
         "Kim rapporteert setterissues aan Saif. CRM-fouten, naleving, prestaties."),
    ]:
        ch(kanaal, cat, topic,
           [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    # Extra escalatie kanalen voor nieuwe afdelingen
    ch("ink-problemen", cat,
        "Issues met Ink Approved setters of klanten. Kim rapporteert aan Saif.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    ch("platform-problemen", cat,
        "Issues met platform setters of aanbieders. Kim rapporteert aan Saif en de Head of Tech.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    # ════════════════════════════════════════
    # 12. MANAGEMENT
    # ════════════════════════════════════════
    cat = create_cat("🗂️ MANAGEMENT", 11,
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    ch("manager-saif", cat,
        "Directe lijn Kim ↔ Saif. Strategische updates, beslissingen, vertrouwelijk.",
        [ev_deny(ev), allow(fo, ALL_TEXT), allow(mgr, ALL_TEXT)])

    ch("commissie-verwerking", cat,
        "Maandelijks commissieoverzicht. Vóór de 5e van elke maand. Kim indienen — Saif goedkeuren.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    ch("marktdata-analyse", cat,
        "Wekelijkse samenvatting pijnpunten van setters en outreachers. 3+ hetzelfde = potentieel nieuw product.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf, mgr, wd]])

    ch("franchise-boris", cat,
        "Boris (NEXTRIQ Oekraïne) maandrapport + 20% royalty + strategische afstemming. Alleen Saif ↔ Boris.",
        [ev_deny(ev), allow(fo, ALL_TEXT)])

    ch("platform-strategie", cat,
        "NEXTRIQ Label / vergelijkingssite strategie en beslissingen. Saif × Head of Tech.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, cf]])

    ch("team-beschikbaarheid", cat,
        "Overzicht team planning, verlof en afwezigheid. Kim beheert voor rapportage aan Saif.",
        [ev_deny(ev)] + [allow(x, ALL_TEXT) for x in [fo, mgr]])

    # ════════════════════════════════════════
    # 13. VOICE KANALEN
    # ════════════════════════════════════════
    cat = create_cat("🔊 VOICE", 12,
        [ev_deny(ev)] + [allow(x, ALL_TEXT|CONN|SPEAK) for x in intern_all])

    voice_channels = [
        ("🔊 Algemeen",                intern_all),
        ("📅 Wekelijkse Teammeeting",  intern_all),
        ("🎯 Setter Room",             [fo, mgr, ts, s, ns]),
        ("📧 Outreach Room",           [fo, mgr, out]),
        ("🖤 Ink Approved Room",       [fo, mgr, ink]),
        ("🌐 Platform Room",           [fo, cf, mgr, ps]),
        ("🎯 Closer Room",             [fo, mgr, cl]),
        ("🎬 Creator Room",            [fo, mgr, cr, amb]),
        ("⚙️ Tech Room",           [fo, cf, mgr, wd]),
        ("📍 1-op-1 met Kim",         [fo, mgr]),
    ]

    for vname, allowed in voice_channels:
        api("post", f"/guilds/{SERVER_ID}/channels", {
            "name": vname, "type": 2, "parent_id": cat,
            "permission_overwrites":
                [ev_deny(ev)] + [allow(x, CONN|SPEAK|VIEW) for x in allowed]
        })
        time.sleep(0.5)
        print(f"    🔊 {vname}")

    # ════════════════════════════════════════
    # WELKOMSTBERICHT VASTPINNEN
    # ════════════════════════════════════════
    if welkom_id:
        print("\n📌 Welkomstbericht vastpinnen...")
        welkom = """# 🚀 Welkom bij NEXTRIQ!

**NEXTRIQ | Business Intelligence voor het Nederlandse bedrijfsleven**

---

## 🗺️ Serverstructuur

**📌 INFORMATIE** — Lees dit eerst. Altijd actueel houden.
**💬 TEAM** — Dagelijkse communicatie, beschikbaarheid, wins.
**🧠 KENNIS & SCRIPTS** — Sales scripts, bezwaren, handboeken. Lees vóór elk gesprek.
**🎨 MARKETING MIDDELEN** — Templates, links, brand assets, campagnes.
**📊 SALES & RESULTATEN** — CRM updates, dagrapport, leaderboard, deals.
**📧 OUTREACH** — Cold outreach afdeling. Eigen scripts en rapportage.
**🖤 INK APPROVED** — Tatu-shop product. Eigen setters, eigen pipeline.
**🌐 NEXTRIQ LABEL & PLATFORM** — Vergelijkingssite. Eigen setters, aanbieders werven.
**🎬 CONTENT & CREATORS** — Briefings, planning, creators + ambassadeurs.
**⚙️ TECH & OPLEVERING** — Webprojecten, AI-agents, tech-vragen.
**🚨 ESCALATIE** — Alleen Founder + Manager. Uitzonderingen en problemen.
**🗂️ MANAGEMENT** — Intern management. Alleen Founder + Manager.

---

## 📋 De 7 regels van NEXTRIQ

**Regel 1** — Elke lead in het CRM. Ook afwijzingen. Altijd.
**Regel 2** — Pijnpunt Marktdata invullen bij elke interactie. Zelfs bij nee.
**Regel 3** — Dagrapport vóór 18:00 elke werkdag.
**Regel 4** — Nooit korting zonder goedkeuring in #maatwerk-goedkeuring.
**Regel 5** — AI Agency altijd pas na AI Intelligence Scan.
**Regel 6** — DMs binnen 2 uur beantwoorden.
**Regel 7** — Vragen aan manager? #vragen-aan-manager. Nooit in DM.

---

## 💻 Systemen

**CRM:** crmoas.vercel.app
**Calendly:** [invullen]
**Google Drive (handboeken):** [invullen]

---

*NEXTRIQ v3.0 — Gebouwd voor groei. Aangedreven door data.*

> 💡 Head of Web Dev wordt tijdelijk gedragen door Saif (Founder) totdat er een nieuwe webdeveloper is aangesteld."""
        pin(welkom_id, welkom)
        print("  ✅ Welkomstbericht vastgepind!")

    if dagrapport_id:
        print("\n📌 Dagrapport format vastpinnen...")
        dagrapport_format = """📋 **DAGRAPPORT FORMAT — kopieer en vul in**

```
📋 DAGRAPPORT [datum] — [jouw naam]

Leads benaderd: [aantal]
Cold calls / DMs: [aantal]
Calls geboekt: [aantal]
Actieve gesprekken: [aantal]
Follow-ups: [aantal]

Pijnpunten gehoord vandaag:
[Wat zeiden klanten? Welke problemen noemden ze letterlijk?]

Blokkades / wat kon beter:
[Wat hield je tegen vandaag?]
```

⏰ Deadline: **18:00 elke werkdag**
❌ Geen rapport = niet geteld voor leaderboard"""
        pin(dagrapport_id, dagrapport_format)
        print("  ✅ Dagrapport format vastgepind!")


    # ════════════════════════════════════════════════
    # VASTGEPINDE BERICHTEN
    # ════════════════════════════════════════════════
    print("\n📌 Vastgepinde berichten toevoegen...")

    def p(cid, msg):
        if cid:
            pin(cid, msg)

    p(aankondigingen_id, "📢 **Officieel aankondigingskanaal NEXTRIQ.**\n\nHier vind je:\n— Teamupdates en nieuwe beslissingen\n— Nieuwe teamleden en rolwijzigingen\n— Productwijzigingen en prijzen\n— Deadlines\n\n🔔 Zet notificaties aan voor dit kanaal.\n❌ Alleen Founder en Manager mogen hier posten.")

    p(productupdates_id, """🆕 **Actuele productprijzen — altijd checken voor klantgesprek**

🔍 AI Intelligence Scan Professioneel: **€1.500**
🔍 AI Scan Digitaal: **€450** *(nooit actief aanbieden — alleen plan B)*
🌐 Website Standaard: **€1.000** | 2 revisieronden + SEO
💻 Website Maatwerk: op aanvraag
🖥️ Hosting & Beveiliging: **€50/mnd** *(altijd upsellen!)*
🤖 AI Agency: **vanaf €5.000** *(ALTIJD na scan — nooit eerder)*
🖤 Ink Approved: Gratis (≤5) → **€29/mnd**
👥 Community: 1e maand gratis · **€100/mnd** klanten · **€200/mnd** extern

⚠️ Nooit korting zonder goedkeuring in #maatwerk-goedkeuring""")

    p(systeemUpdates_id, """💻 **NEXTRIQ Systemen**

**CRM:** crmoas.vercel.app
→ Alle leads, deals, dagrapporten en commissies

**Calendly:** [link invullen]
→ Setters sturen dit naar gekwalificeerde leads

**Handboeken:** [Google Drive link invullen]

**Zapier actief:**
⚡ Nieuwe lead → #crm-updates
⚡ Calendly → #booked-calls
⚡ Deal gesloten → #deals-gesloten
⚡ Betaling → #betalingen-ontvangen
⚡ Vrijdag 16:00 → #leaderboard
⚡ 17:30 werkdag → dagrapport herinnering""")

    p(beschikbaar_id, """📅 **Beschikbaarheid — dagelijks vóór 9:30**

✅ Beschikbaar:
`✅ [Naam] — BESCHIKBAAR | [tijden] | Focus: [wat doe je vandaag]`

❌ Niet beschikbaar:
`❌ [Naam] — NIET BESCHIKBAAR | Reden: [reden] | Terug: [datum]`

⚠️ Geen melding = Kim gaat ervan uit dat je niet werkt.""")

    p(vragen_id, """❓ **Vragen aan Kim — HIER, nooit in DM**

Kim reageert binnen 4 uur op werkdagen (09:00–18:00).
Spoed? Tag @Kim direct hier.

Niet hier voor:
→ Commissievragen → #commissie-vragen
→ Tech vragen → #tech-vragen
→ Klachten → escalatie kanalen""")

    p(scripts_id, """🧠 **Sales Scripts — lees vóór elk gesprek**

**Eerste DM:**
*"Hé [naam]! 👋 Zag je bedrijf — wat doe je precies?"*

**Na antwoord:**
*"Tof! Wij helpen bedrijven zoals jou slimmer werken met AI. Mag ik je een paar vragen stellen?"*

**BANT+ verplicht:**
— Budget: Ja / Onduidelijk / Nee
— Autoriteit: Beslisser / Directe lijn / Geen
— Need: schrijf letterlijk op wat ze zeggen
— Timing: <1mnd / <3mnd / 3–6mnd / Geen
— Pijnpunt Marktdata: welk proces kost meeste tijd? *(ook bij afwijzing!)*

**Doorsturen naar closer:**
*"Ik zet je even door naar onze specialist. Wanneer heb je 30 min?"* → [Calendly]""")

    p(bezwaren_id, """🛡️ **Bezwaren — de NEXTRIQ methode**

**"Te duur"** → *"Hoeveel uur per week kost [pijn] jou? Keer je uurtarief — dit verdient zichzelf terug."*
**"Geen tijd"** → *"Precies waarom wij er zijn. Jij hoeft alleen ja te zeggen."*
**"Moet nadenken"** → *"Wat twijfel je nog over? Dan lossen we het nu op."*
**"Werk al met iemand"** → *"Wat loopt er niet lekker bij hen? Wij werken naast ze."*
**"AI is niks voor mij"** → *"Hoeveel tijd kost [taak] je per week? Dat is precies wat AI oplost."*""")

    p(handboeken_id, """📚 **Handboeken — verplicht lezen bij onboarding**

📗 Handboek Setter → [link invullen]
📘 Handboek Closer → [link invullen]
📙 Handboek Creator → [link invullen]
📕 Handboek Ambassadeur → [link invullen]
📓 Handboek Sales Manager → [link invullen]
💻 CRM Handleiding → crmoas.vercel.app

💡 Staat je vraag in het handboek? Lees het eerst.""")

    p(canva_id, """🎨 **Canva Templates — alleen goedgekeurde designs gebruiken**

NEXTRIQ Canva workspace: [link invullen]

Beschikbaar: Stories · Reels · Carrousel · LinkedIn · TikTok cover

**Kleuren:** Navy #1B2A4A · Paars #6B3FA0 · Wit #FFFFFF
⚠️ Nooit kleuren of logo aanpassen zonder toestemming Saif.""")

    p(brand_id, """🏷️ **NEXTRIQ Brand Assets**

Navy: #1B2A4A · Paars: #6B3FA0 · Wit: #FFFFFF · Font: Arial/Inter

Logo downloads: [Google Drive link invullen]
— Horizontaal (PNG + SVG)
— Verticaal (PNG + SVG)
— Wit op donker (PNG + SVG)

⚠️ Altijd officieel logo. Niet vervormen of verkleuren.""")

    p(noshows_id, """❌ **No-Show registratie**

```
❌ NO-SHOW
Closer: [naam]
Klant: [bedrijfsnaam]
Tijd: [datum + tijd]
Reden: [indien bekend]
Actie: [herplannen / verloren]
```

Direct melden na gemiste afspraak. Bij herhaling → deal op Verloren.""")

    p(outscripts_id, """📧 **Outreach Scripts — alleen goedgekeurde scripts**

**Cold Call:**
*"Goedemiddag, u spreekt met [naam] van NEXTRIQ. Wij helpen [sector] bedrijven slimmer werken met AI. Heeft u 2 minuten?"*

**LinkedIn:**
*"Hi [naam], zag dat [bedrijf] actief is in [sector]. Wij bouwen AI-oplossingen voor MKB. Mag ik je een vraag stellen?"*

**Na interesse:**
→ Log in #leads-doorgestuurd, setter neemt binnen 2u contact op.""")

    p(dagout_id, """📋 **OUTREACH DAGRAPPORT — vóór 18:00**

```
OUTREACH DAGRAPPORT [datum] — [naam]
Benaderd: [aantal] | Reacties: [aantal]
Calls: [aantal] | Emails: [aantal] | LinkedIn: [aantal]
Leads doorgestuurd: [aantal]
Pijnpunten: [wat zeiden bedrijven]
```""")

    p(inkinfo_id, """🖤 **Ink Approved — Productinfo & Scripts**

AI-systeem voor tatu-shops: reserveringen, klanten, ontwerpen.
Gratis (≤5 aanvragen) → €29/mnd onbeperkt

**Opening DM:**
*"Hey [naam]! Gaaf werk 🔥 Beheer je reserveringen nog handmatig?"*

**Bij interesse:**
*"Wij hebben Ink Approved — gratis starten, geen creditcard."*

**Upgrade:**
*"Je 5 gratis aanvragen zijn op. Voor €29/mnd ga je onbeperkt — minder dan €1 per dag."*

Log elke shop in #ink-leads: Shopnaam | Stad | Contact | Status""")

    p(inkdag_id, """📋 **INK APPROVED DAGRAPPORT — vóór 18:00**

```
INK DAGRAPPORT [datum] — [naam]
Shops benaderd: [aantal] | Reacties: [aantal]
Demo's: [aantal] | Gratis starts: [aantal] | Upgrades: [aantal]
Feedback: [wat zeiden shops]
```""")

    p(platinfo_id, """🌐 **NEXTRIQ Label Platform — Info & Doelen**

De Independer voor AI in Nederland — vergelijkt bureaus, tools, educatie en consultants.

**Pakketten:**
— Gratis: basisvermelding (instap)
— Standaard €99/mnd: prominent, logo, contactknop
— Premium €299/mnd: top-3, video, case studies
— NEXTRIQ Label €499/mnd: keurmerk + leads direct

**Pitch:**
*"Wij brengen jou in contact met MKB'ers die actief zoeken naar jouw oplossing."*

**Doel:** 50 betalende aanbieders binnen 3 maanden.""")

    p(platpitch_id, """📞 **Platform Setter Scripts**

**Cold outreach:**
*"Hoi [naam], jullie [product] is perfect voor ons AI-vergelijkingsplatform — de Independer voor AI in NL. Gratis gelistet als early adopter?"*

**Van gratis naar betaald:**
*"Je staat gratis gelistet. We zien [X] views/week. Voor €99/mnd zet ik je prominent bovenaan."*

**NEXTRIQ Label:**
*"Het AI-keurmerk van Nederland. Aanbieders met Label zien 3x meer leads."*

Log aanbieders in #aanbieders-pipeline: Aanbieder | Status | Setter""")

    p(platdag_id, """📋 **PLATFORM DAGRAPPORT — vóór 18:00**

```
PLATFORM DAGRAPPORT [datum] — [naam]
Benaderd: [aantal] | Reacties: [aantal]
Gratis listings: [aantal] | Betaald: [aantal] | Label aanvr.: [aantal]
Feedback: [bezwaren, interesse]
```""")

    p(briefings_id, """🎬 **Content Briefings — elke maandag van Saif**

Hier staat jouw wekelijkse contenttaak.

Format briefing:
```
WEEK [X] — Content Briefing
Focusproduct: [product]
CTA: [wat moet kijker doen]
Thema: [onderwerp]
Minimaal: [X] Reels/TikToks · [X] Stories · [X] LinkedIn
Haak: [openingszin]
```

Content geplaatst? → #content-geplaatst
Ideeën? → #content-ideeen""")

    p(ambregels_id, """🌟 **Ambassadeur Onboarding — lees dit eerst**

Welkom! Je maakt content op jouw kanalen over NEXTRIQ.
Elke klant via jouw content → **10% commissie** voor jou.

Hoe werkt commissie:
1. Klant noemt jouw naam bij contact
2. Kim registreert in CRM
3. 30 dagen na betaling → jij krijgt 10%

Handboek: [link invullen]
Briefings: #content-briefings (elke maandag)
Templates: #canva-templates
Vragen: #commissie-vragen""")

    p(commissievr_id, """💰 **Commissies — hoe het werkt**

Creator/Ambassadeur: 10% omzet via jouw kanaal
Setter: 5–7% per gesloten deal
Closer: 10% per deal
Manager Kim: 5% totale teamomzet/maand

Uitbetaald: 30 dagen na betaling klant
Kim verwerkt vóór 5e van volgende maand
Rekening indienen vóór 1e van de maand""")

    p(techvragen_id, """⚙️ **Tech Vragen — altijd hier, nooit in DM**

Erik beantwoordt. Reactietijd: binnen 1 werkdag.

Format:
```
TECH VRAAG
Type: [CRM / AI / Website / Automatisering]
Probleem: [exact wat er misgaat]
Geprobeerd: [wat al gedaan]
Urgentie: normaal / hoog / urgent
```

CRM problemen → hard refresh: Cmd+Shift+R (Mac) / Ctrl+Shift+R (Windows)""")

    p(onboarding_id, """📦 **Klant Onboarding — format voor closers**

Na deal sluiten: stuur info hier zodat Saif/Erik kunnen starten.

```
KLANT ONBOARDING
Bedrijfsnaam: [naam]
Contact: [naam + email + tel]
Product: [website / AI Scan / AI Agency / Ink Approved]
Waarde: €[bedrag]
Betaling: [ja/nee]
Deadline: [indien relevant]
Wensen: [wat wil klant]
Closer: [naam] | Setter: [naam]
```

Saif/Erik bevestigt opstart binnen 24 uur.""")

    print("  ✅ Alle berichten vastgepind!")

    print("\n" + "="*55)
    print("✅ NEXTRIQ Discord v3.0 volledig aangemaakt!")
    print("="*55)
    print("""
Aangemaakt:
  ✅ 14 rollen (3 nieuw: Ink Setter, Platform Setter, Outreacher)
  ✅ 13 categorieën (4 nieuw: Marketing Middelen, Outreach, Ink Approved, Platform)
  ✅ 65+ kanalen met beschrijvingen en rechten
  ✅ Welkomstbericht vastgepind
  ✅ Dagrapport format vastgepind
  ✅ 10 voice kanalen

Volgende stappen:
  1. Geef jezelf de 🚀 Founder rol
  2. Geef Kim de 🛡️ Sales Manager rol
  3. Wijs Ink Setters de 🖤 Ink Setter rol toe
  4. Wijs Platform Setters de 🌐 Platform Setter rol toe
  5. Stel Zapier automatiseringen in
  6. Zet handboek-links in #handboeken
  7. Zet CRM-link (crmoas.vercel.app) in #systeem-updates
""")

if __name__ == "__main__":
    main()
