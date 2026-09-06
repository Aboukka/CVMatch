import json
import os
import re
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DEMO_DIR = BASE_DIR.parent / "job-intelligence-demo"

app = FastAPI(title="Teamwork Job Intelligence Live Test", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class JobRequest(BaseModel):
    title: str
    company: str = "Entreprise Démo"
    department: str = "Ressources Humaines"
    reports_to: str = "DRH"
    context: str = ""

class ResearchRequest(BaseModel):
    query: str


def _clean_json_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.I)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _walk_urls(obj: Any, out: list[dict]):
    if isinstance(obj, dict):
        url = obj.get("url")
        if isinstance(url, str) and url.startswith("http"):
            out.append({"url": url, "title": obj.get("title") or obj.get("name") or url})
        for value in obj.values():
            _walk_urls(value, out)
    elif isinstance(obj, list):
        for value in obj:
            _walk_urls(value, out)


def openai_web_search(query: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return {"available": False, "summary": "", "sources": [], "error": "OPENAI_API_KEY absente"}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_WEB_SEARCH_MODEL") or os.getenv("OPENAI_MODEL") or "gpt-5.6-terra"
        response = client.responses.create(
            model=model,
            tools=[{"type": "web_search"}],
            tool_choice="auto",
            include=["web_search_call.action.sources"],
            input=(
                "Effectue une recherche professionnelle sur le poste suivant. Priorise les référentiels métier, "
                "associations professionnelles, institutions, pages carrière reconnues et sources RH crédibles. "
                "Identifie finalité, missions, responsabilités, compétences, outils, KPI, autonomie et évolutions récentes. "
                f"Requête : {query}"
            ),
        )
        dumped = response.model_dump() if hasattr(response, "model_dump") else {}
        raw_sources: list[dict] = []
        _walk_urls(dumped, raw_sources)
        seen = set()
        sources = []
        for item in raw_sources:
            if item["url"] not in seen:
                seen.add(item["url"])
                sources.append(item)
        return {"available": True, "summary": getattr(response, "output_text", "") or "", "sources": sources[:20], "error": None}
    except Exception as exc:
        return {"available": False, "summary": "", "sources": [], "error": str(exc)}


def esco_search(query: str) -> dict:
    base = os.getenv("ESCO_API_BASE_URL", "https://ec.europa.eu/esco/api").rstrip("/")
    version = os.getenv("ESCO_SELECTED_VERSION", "v1.2.0")
    try:
        r = requests.get(
            f"{base}/search",
            params={"text": query, "type": "occupation", "language": "fr", "selectedVersion": version},
            timeout=15,
            headers={"User-Agent": "Teamwork-Job-Intelligence/0.1"},
        )
        r.raise_for_status()
        data = r.json()
        items = []
        embedded = data.get("_embedded", {}) if isinstance(data, dict) else {}
        for key in ("results", "occupations"):
            value = embedded.get(key)
            if isinstance(value, list):
                items.extend(value)
        if not items and isinstance(data, dict):
            for key in ("results", "occupations"):
                value = data.get(key)
                if isinstance(value, list):
                    items.extend(value)
        parsed = []
        for item in items[:8]:
            if not isinstance(item, dict):
                continue
            label = item.get("title") or item.get("preferredLabel") or item.get("label") or item.get("name")
            uri = item.get("uri") or item.get("conceptUri") or item.get("href")
            parsed.append({"title": label or "Occupation ESCO", "url": uri or "https://esco.ec.europa.eu/", "type": "ESCO"})
        return {"available": True, "results": parsed, "error": None}
    except Exception as exc:
        return {"available": False, "results": [], "error": str(exc)}


def local_profile(req: JobRequest) -> dict:
    title = req.title.strip() or "Poste"
    return {
        "title": title,
        "finality": f"Piloter les principales responsabilités du poste de {title} afin de contribuer aux priorités de l’organisation avec un niveau clair d’autonomie, de coordination et de résultat.",
        "missions": [
            "Structurer et piloter le périmètre d’activité du poste.",
            "Coordonner les parties prenantes internes et externes utiles à la réalisation des objectifs.",
            "Suivre la qualité, les délais, les risques et les résultats associés au périmètre.",
            "Proposer des améliorations et accompagner l’évolution des pratiques, outils et compétences.",
        ],
        "responsibilities": [
            "Répondre de la qualité et de la fiabilité des livrables de son périmètre.",
            "Alerter et recommander des arbitrages en cas d’écart ou de risque significatif.",
        ],
        "skills": ["Pilotage", "Analyse", "Coordination", "Communication", "Maîtrise des outils du métier"],
        "kpis": ["Respect des délais", "Qualité des livrables", "Taux de réalisation des objectifs"],
        "quality_score": 78,
        "provider": "local-demo",
    }


def ai_generate(req: JobRequest, research: dict) -> dict:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            model = os.getenv("OPENAI_MODEL", "gpt-5.6-terra")
            prompt = f"""
Tu es le moteur Teamwork Job Intelligence. Produit une fiche de poste structurée, sobre et précise.
Règles : ne jamais inventer silencieusement, distinguer responsabilités et activités, 4 à 7 missions, compétences justifiées, KPI uniquement s'ils sont pertinents, pas de jargon générique.
Contexte entreprise : {req.company}; département : {req.department}; rattachement : {req.reports_to}; contexte libre : {req.context or 'non renseigné'}.
Poste : {req.title}.
Synthèse recherche : {research.get('web', {}).get('summary', '')[:8000]}
Sources ESCO : {json.dumps(research.get('esco', {}).get('results', []), ensure_ascii=False)[:4000]}
Retourne UNIQUEMENT un JSON valide avec les clés : title, finality, missions (liste), responsibilities (liste), activities (liste), skills (liste), kpis (liste), autonomy, stakeholders (liste), quality_score (entier 0-100), validation_points (liste).
"""
            response = client.responses.create(model=model, input=prompt)
            text = getattr(response, "output_text", "") or ""
            data = json.loads(_clean_json_text(text))
            data["provider"] = f"openai:{model}"
            return data
        except Exception as exc:
            fallback = local_profile(req)
            fallback["provider"] = "local-demo (fallback OpenAI)"
            fallback["generation_error"] = str(exc)
            return fallback

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=anthropic_key)
            model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
            prompt = f"""Tu es Teamwork Job Intelligence. Génère une fiche structurée pour {req.title} chez {req.company}. Retourne uniquement du JSON valide avec title, finality, missions, responsibilities, activities, skills, kpis, autonomy, stakeholders, quality_score, validation_points. Évite toute invention non signalée. Contexte recherche: {research.get('web', {}).get('summary','')[:6000]}"""
            message = client.messages.create(model=model, max_tokens=3500, messages=[{"role": "user", "content": prompt}])
            text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")
            data = json.loads(_clean_json_text(text))
            data["provider"] = f"anthropic:{model}"
            return data
        except Exception as exc:
            fallback = local_profile(req)
            fallback["provider"] = "local-demo (fallback Claude)"
            fallback["generation_error"] = str(exc)
            return fallback

    return local_profile(req)


@app.get("/health")
def health():
    return {"status": "ok", "app": "Teamwork Job Intelligence"}


@app.get("/api/status")
def status():
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "claude": bool(os.getenv("ANTHROPIC_API_KEY", "").strip()),
        "esco": True,
        "rome": bool(os.getenv("FRANCE_TRAVAIL_ROME_SEARCH_URL", "").strip()),
        "onet": bool(os.getenv("ONET_API_KEY", "").strip()),
        "mode": "live" if (os.getenv("OPENAI_API_KEY", "").strip() or os.getenv("ANTHROPIC_API_KEY", "").strip()) else "hybrid-demo",
    }


@app.post("/api/research")
def research(req: ResearchRequest):
    esco = esco_search(req.query)
    web = openai_web_search(req.query)
    sources = []
    for item in esco.get("results", []):
        sources.append({"title": item.get("title"), "url": item.get("url"), "type": "ESCO", "authority": 0.94})
    for item in web.get("sources", []):
        sources.append({"title": item.get("title"), "url": item.get("url"), "type": "Web", "authority": 0.72})
    dedup = []
    seen = set()
    for s in sources:
        key = s.get("url") or s.get("title")
        if key and key not in seen:
            seen.add(key)
            dedup.append(s)
    return {"query": req.query, "esco": esco, "web": web, "sources": dedup[:25], "source_count": len(dedup)}


@app.post("/api/generate")
def generate(req: JobRequest):
    query = f"{req.title} {req.department} missions responsabilités compétences KPI outils autonomie"
    research_payload = {"esco": esco_search(query), "web": openai_web_search(query)}
    profile = ai_generate(req, research_payload)
    return {"profile": profile, "research": research_payload}


@app.get("/livrable")
def livrable():
    path = DEMO_DIR / "livrable.html"
    if path.exists():
        return FileResponse(path)
    return JSONResponse({"error": "livrable.html introuvable"}, status_code=404)


@app.get("/")
def root():
    path = DEMO_DIR / "live.html"
    if path.exists():
        return FileResponse(path)
    return {"message": "Teamwork Job Intelligence API", "health": "/health"}
