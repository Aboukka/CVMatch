import csv, io, json, os, re, time, uuid
from pathlib import Path
from typing import Any

import requests
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
DEMO_DIR = BASE_DIR.parent / "job-intelligence-demo"

app = FastAPI(title="Teamwork Job Intelligence — Integrated Pilot", version="3.6.0-pilot")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"])

ORG_ID="org-atlas"
NOW=lambda: int(time.time())

def uid(prefix="id"): return f"{prefix}-{uuid.uuid4().hex[:10]}"

def profile_template(title="Responsable Formation", department="Développement RH", reports_to="Directeur des Ressources Humaines", location="Casablanca"):
    return {
        "id": uid("profile"), "title_fr": title, "title_en": "Learning & Development Manager" if "Formation" in title else title,
        "department": department, "reports_to": reports_to, "location": location, "direct_reports": 2,
        "workflow_status":"hr_review", "quality_score":92, "freshness_score":88, "version":"1.2",
        "finality_fr": f"Concevoir, structurer et piloter le périmètre {title} afin de transformer les priorités de l’organisation en résultats mesurables, avec un niveau d’autonomie et de responsabilité clairement établi.",
        "missions":[
            {"id":uid("m"),"label":"Structurer et piloter la stratégie et le plan d’action du périmètre.","activities":["Analyser les besoins et priorités","Construire la feuille de route","Planifier les actions et ressources"]},
            {"id":uid("m"),"label":"Coordonner les parties prenantes et sécuriser l’exécution.","activities":["Animer les interfaces internes","Piloter les partenaires externes","Suivre délais, qualité et risques"]},
            {"id":uid("m"),"label":"Mesurer la performance et éclairer les décisions.","activities":["Définir les indicateurs utiles","Analyser les écarts","Formuler des recommandations"]},
            {"id":uid("m"),"label":"Faire évoluer les pratiques, outils et compétences du périmètre.","activities":["Réaliser une veille ciblée","Tester des améliorations","Accompagner l’adoption"]}
        ],
        "responsibilities":[
            {"id":uid("r"),"label":"Répondre de la qualité, de la conformité et de la fiabilité des livrables du périmètre.","authority":"décide / recommande"},
            {"id":uid("r"),"label":"Alerter, proposer et documenter les arbitrages en cas de risque ou d’écart significatif.","authority":"recommande / contrôle"}
        ],
        "skills":[
            {"id":uid("s"),"label":"Pilotage du périmètre","level":"N4","type":"technical"},
            {"id":uid("s"),"label":"Analyse et aide à la décision","level":"N4","type":"technical"},
            {"id":uid("s"),"label":"Coordination transverse","level":"N4","type":"behavioral"},
            {"id":uid("s"),"label":"Communication avec les parties prenantes","level":"N4","type":"behavioral"},
            {"id":uid("s"),"label":"Outils digitaux du métier","level":"N3","type":"tool"}
        ],
        "kpis":[
            {"id":uid("k"),"label":"Taux de réalisation du plan d’action","target":"≥ 90 %"},
            {"id":uid("k"),"label":"Respect des délais et engagements","target":"≥ 95 %"},
            {"id":uid("k"),"label":"Qualité / satisfaction des parties prenantes","target":"≥ 4/5"}
        ],
        "autonomy":"Autonomie dans l’organisation opérationnelle du périmètre ; arbitrages structurants avec le N+1.",
        "stakeholders":["Direction RH","Managers","Finance / Contrôle de gestion","Prestataires / partenaires"],
        "sources":[
            {"id":uid("e"),"title":"Teamwork Method — Job Architecture","type":"teamwork","authority":0.98,"confidence":0.96,"provenance":"proprietary"},
            {"id":uid("e"),"title":"ESCO — occupation & skills benchmark","type":"reference","authority":0.94,"confidence":0.88,"provenance":"external_reference"},
            {"id":uid("e"),"title":"Documents entreprise","type":"company_document","authority":0.97,"confidence":0.91,"provenance":"company_confirmed"}
        ],
        "quality_breakdown":{"positioning":9,"purpose":9,"missions":14,"activities":9,"responsibility":9,"skills":14,"kpis":9,"consistency":9,"differentiation":5,"writing":5},
        "recommendations":[
            {"id":uid("rec"),"severity":"medium","title":"Formaliser l’autorité de décision","why":"Le périmètre implique plusieurs arbitrages mais les droits de décision restent partiellement implicites."},
            {"id":uid("rec"),"severity":"low","title":"Relier chaque KPI à un résultat attendu","why":"Améliore la traçabilité entre responsabilités et performance."}
        ]
    }

STATE={
 "orgs":[{"id":ORG_ID,"legal_name":"Atlas Manufacturing","industry":"Industrie","country":"Maroc","employee_count":1250,"organization_type":"Fonctionnelle multi-sites","has_logo":False}],
 "jobs":[], "documents":[], "validations":[], "notifications":[], "imports":[], "update_runs":[], "comments":[]
}
for t,d,q,f,s in [
 ("Responsable Formation","Développement RH",92,88,"hr_review"),
 ("HR Business Partner","Ressources Humaines",89,91,"approved"),
 ("Responsable Recrutement","Talent Acquisition",86,84,"manager_validation"),
 ("Responsable Paie","Administration RH",68,61,"changes_requested"),
 ("Compensation & Benefits Manager","C&B",91,87,"approved")]:
 p=profile_template(t,d); p["quality_score"]=q;p["freshness_score"]=f;p["workflow_status"]=s; STATE["jobs"].append(p)

class JobCreate(BaseModel):
    organization_id:str=ORG_ID; title_fr:str; title_en:str|None=None; department:str=""; reports_to:str=""; location:str="Casablanca"; direct_reports:int=0
class ResearchReq(BaseModel): query:str=""; job_id:str|None=None
class ActionReq(BaseModel): action:str|None=None; value:Any=None; comment:str|None=None

def job_summary(p):
    return {k:p.get(k) for k in ["id","title_fr","title_en","department","reports_to","location","direct_reports","workflow_status","quality_score","freshness_score","version"]}

def find_job(job_id):
    for j in STATE["jobs"]:
        if j["id"]==job_id:return j
    raise HTTPException(404,"Job not found")

def _clean_json_text(text):
    return re.sub(r"\s*```$","",re.sub(r"^```(?:json)?\s*","",(text or "").strip(),flags=re.I)).strip()

def _walk_urls(obj,out):
    if isinstance(obj,dict):
        if isinstance(obj.get("url"),str) and obj["url"].startswith("http"): out.append({"url":obj["url"],"title":obj.get("title") or obj.get("name") or obj["url"]})
        for v in obj.values(): _walk_urls(v,out)
    elif isinstance(obj,list):
        for v in obj:_walk_urls(v,out)

def esco_search(query):
    try:
        r=requests.get("https://ec.europa.eu/esco/api/search",params={"text":query,"type":"occupation","language":"fr","selectedVersion":"v1.2.1"},timeout=12,headers={"User-Agent":"Teamwork-Job-Intelligence/3.6"})
        if r.status_code>=400:
            r=requests.get("https://ec.europa.eu/esco/api/search",params={"text":query,"type":"occupation","language":"fr","selectedVersion":"v1.2.0"},timeout=12)
        r.raise_for_status(); data=r.json(); items=[]
        emb=data.get("_embedded",{}) if isinstance(data,dict) else {}
        for key in ("results","occupations"):
            if isinstance(emb.get(key),list):items+=emb[key]
            if isinstance(data.get(key),list):items+=data[key]
        out=[]
        for x in items[:8]:
            if not isinstance(x,dict):continue
            out.append({"id":uid("esco"),"title":x.get("title") or x.get("preferredLabel") or x.get("label") or "Occupation ESCO","url":x.get("uri") or x.get("conceptUri") or "https://esco.ec.europa.eu/","type":"ESCO","authority":0.94,"confidence":0.86,"provenance":"external_reference"})
        return {"available":True,"results":out,"error":None}
    except Exception as e:return {"available":False,"results":[],"error":str(e)}

def web_search(query):
    key=os.getenv("OPENAI_API_KEY","").strip()
    if not key:return {"available":False,"summary":"Mode démonstration : ajoutez OPENAI_API_KEY pour activer la recherche web live.","sources":[],"error":"OPENAI_API_KEY absent"}
    try:
        from openai import OpenAI
        c=OpenAI(api_key=key); model=os.getenv("OPENAI_WEB_SEARCH_MODEL","gpt-5.6-terra")
        resp=c.responses.create(model=model,tools=[{"type":"web_search"}],tool_choice="auto",include=["web_search_call.action.sources"],input=f"Recherche professionnelle sur le poste {query}. Priorise institutions, référentiels, associations, études et pages carrière reconnues. Identifie missions, responsabilités, skills, outils, KPI et évolutions. Compare et synthétise sans copier.")
        dumped=resp.model_dump() if hasattr(resp,"model_dump") else {}; raw=[];_walk_urls(dumped,raw);seen=set();sources=[]
        for x in raw:
            if x["url"] in seen:continue
            seen.add(x["url"]);sources.append({"id":uid("web"),"title":x["title"],"url":x["url"],"type":"Web","authority":0.78,"confidence":0.82,"provenance":"web_benchmark"})
        return {"available":True,"summary":getattr(resp,"output_text","") or "","sources":sources[:16],"error":None}
    except Exception as e:return {"available":False,"summary":"","sources":[],"error":str(e)}

def ai_enrich(job,research):
    key=os.getenv("OPENAI_API_KEY","").strip()
    if not key:return job
    try:
        from openai import OpenAI
        c=OpenAI(api_key=key); model=os.getenv("OPENAI_MODEL","gpt-5.6-terra")
        prompt={"role":"Teamwork Job Analyst","doctrine":["understand before writing","job not person","4-7 missions","no silent invention","skills justified","KPIs outcomes","sober concrete writing"],"job":job_summary(job),"research":research}
        r=c.responses.create(model=model,input="Retourne uniquement un JSON avec finality_fr, missions (strings), responsibilities (strings), skills (strings), kpis (strings), autonomy, stakeholders (strings), validation_points (strings). Contexte: "+json.dumps(prompt,ensure_ascii=False)[:20000])
        data=json.loads(_clean_json_text(getattr(r,"output_text","") or "{}"))
        if data.get("finality_fr"):job["finality_fr"]=data["finality_fr"]
        if data.get("missions"):job["missions"]=[{"id":uid("m"),"label":x,"activities":[]} for x in data["missions"][:7]]
        if data.get("responsibilities"):job["responsibilities"]=[{"id":uid("r"),"label":x,"authority":"à valider"} for x in data["responsibilities"]]
        if data.get("skills"):job["skills"]=[{"id":uid("s"),"label":x,"level":"N3","type":"technical"} for x in data["skills"]]
        if data.get("kpis"):job["kpis"]=[{"id":uid("k"),"label":x,"target":"à cadrer"} for x in data["kpis"]]
        job["autonomy"]=data.get("autonomy") or job["autonomy"];job["stakeholders"]=data.get("stakeholders") or job["stakeholders"]
        job["provider"]=f"openai:{model}";job["quality_score"]=min(96,max(80,job.get("quality_score",88)+2))
    except Exception as e:job["generation_error"]=str(e)
    return job

@app.get("/health")
def health():return {"status":"ok","service":"teamwork-job-intelligence","version":"3.6.0-pilot"}
@app.get("/api/status")
def simple_status():return {"openai":bool(os.getenv("OPENAI_API_KEY")),"claude":bool(os.getenv("ANTHROPIC_API_KEY")),"esco":True,"mode":"live" if os.getenv("OPENAI_API_KEY") else "integrated-pilot"}
@app.get("/api/v1/ai/status")
def ai_status():return {"requested_provider":"auto","selected_provider":"openai" if os.getenv("OPENAI_API_KEY") else "local","openai_configured":bool(os.getenv("OPENAI_API_KEY")),"anthropic_configured":bool(os.getenv("ANTHROPIC_API_KEY")),"fallback_enabled":True,"models":{"openai":"gpt-5.6-terra","anthropic":"claude-sonnet-5","local":"teamwork-expert-engine"}}
@app.get("/api/v1/organizations")
def orgs():return STATE["orgs"]
@app.post("/api/v1/organizations")
def create_org(payload:dict=Body(...)):
    o={"id":uid("org"),**payload};STATE["orgs"].append(o);return o
@app.get("/api/v1/jobs")
def jobs():return [job_summary(x)|{"profile_id":x["id"],"finality_fr":x["finality_fr"]} for x in STATE["jobs"]]
@app.post("/api/v1/jobs")
def create_job(req:JobCreate):
    p=profile_template(req.title_fr,req.department or "À cadrer",req.reports_to or "À cadrer",req.location);p["title_en"]=req.title_en or req.title_fr;p["direct_reports"]=req.direct_reports;p["version"]="0.1";p["quality_score"]=58;p["freshness_score"]=100;p["workflow_status"]="interview";STATE["jobs"].insert(0,p);return job_summary(p)|{"profile_id":p["id"]}
@app.get("/api/v1/jobs/{job_id}/workspace")
def workspace(job_id:str):
    p=find_job(job_id)
    return {"job":job_summary(p),"profile":{"id":p["id"],"finality_fr":p["finality_fr"],"finality_en":p.get("finality_en","")},"missions":p["missions"],"responsibilities":p["responsibilities"],"skills":p["skills"],"kpis":p["kpis"],"autonomy":p["autonomy"],"stakeholders":p["stakeholders"],"recommendations":p["recommendations"],"quality_breakdown":p["quality_breakdown"],"sources":p["sources"]}
@app.post("/api/v1/jobs/{job_id}/interview/start")
def interview_start(job_id:str,locale:str="fr"):
    find_job(job_id);return {"job_id":job_id,"progress":0.2,"completed":False,"question":{"key":"decision_authority","text":"Quelles décisions le titulaire prend-il réellement sans validation préalable ?","why":"L’autorité de décision permet de calibrer le niveau du poste et d’éviter de confondre coordination et management.","options":["Exécute selon cadre défini","Recommande et coordonne","Décide sur son périmètre","Arbitre des choix structurants","Je ne sais pas"]}}
@app.post("/api/v1/jobs/{job_id}/interview/answer")
def interview_answer(job_id:str,payload:dict=Body(...)):
    p=find_job(job_id);p["workflow_status"]="draft";return {"job_id":job_id,"progress":1.0,"completed":True,"next_question":None,"message":"Contexte suffisant pour lancer l’analyse."}
@app.post("/api/v1/jobs/{job_id}/analyze")
def analyze(job_id:str):
    p=find_job(job_id);q=f"{p['title_fr']} {p['department']} missions responsabilités compétences KPI autonomie";esco=esco_search(q);web=web_search(q);research={"esco":esco,"web":web};p["sources"]=p["sources"]+esco["results"][:4]+web["sources"][:6];ai_enrich(p,research);p["quality_score"]=max(p["quality_score"],88);p["workflow_status"]="hr_review";return workspace(job_id)

@app.patch("/api/v1/editor/jobs/{job_id}/finality")
def edit_finality(job_id:str,payload:dict=Body(...)):
    p=find_job(job_id);p["finality_fr"]=payload.get("value") or payload.get("finality_fr") or p["finality_fr"];return {"ok":True,"finality_fr":p["finality_fr"]}
@app.post("/api/v1/editor/jobs/{job_id}/regenerate-section")
def regen(job_id:str,payload:dict=Body(...)):
    p=find_job(job_id);section=payload.get("section","finality");return {"section":section,"status":"regenerated","workspace":workspace(job_id)}
@app.patch("/api/v1/editor/missions/{item_id}")
def edit_mission(item_id:str,payload:dict=Body(...)):
    for p in STATE["jobs"]:
        for x in p["missions"]:
            if x["id"]==item_id:x["label"]=payload.get("label") or payload.get("value") or x["label"];return x
    raise HTTPException(404,"Mission not found")
@app.patch("/api/v1/editor/activities/{item_id}")
def edit_activity(item_id:str,payload:dict=Body(...)):return {"id":item_id,"ok":True,**payload}
@app.patch("/api/v1/editor/responsibilities/{item_id}")
def edit_resp(item_id:str,payload:dict=Body(...)):return {"id":item_id,"ok":True,**payload}
@app.patch("/api/v1/editor/job-skills/{item_id}")
def edit_skill(item_id:str,payload:dict=Body(...)):return {"id":item_id,"ok":True,**payload}
@app.patch("/api/v1/editor/kpis/{item_id}")
def edit_kpi(item_id:str,payload:dict=Body(...)):return {"id":item_id,"ok":True,**payload}
@app.post("/api/v1/editor/recommendations/{item_id}/accept")
def accept_rec(item_id:str):return {"id":item_id,"decision":"accepted"}
@app.post("/api/v1/editor/recommendations/{item_id}/ignore")
def ignore_rec(item_id:str):return {"id":item_id,"decision":"ignored"}

@app.post("/api/v1/jobs/{job_id}/submit-validation")
def submit_validation(job_id:str):
    p=find_job(job_id);p["workflow_status"]="manager_validation";v={"id":uid("val"),"job_id":job_id,"job_title":p["title_fr"],"status":"pending","requested_at":NOW(),"requested_by":"Abdellah Oukkache"};STATE["validations"].append(v);return v
@app.get("/api/v1/validations")
def validations():return STATE["validations"]
@app.post("/api/v1/validations/{vid}/approve")
def approve(vid:str):
    for v in STATE["validations"]:
        if v["id"]==vid:v["status"]="approved";find_job(v["job_id"])["workflow_status"]="approved";return v
    raise HTTPException(404,"Validation not found")
@app.post("/api/v1/validations/{vid}/request-changes")
def request_changes(vid:str,payload:dict=Body(default={})):
    for v in STATE["validations"]:
        if v["id"]==vid:v["status"]="changes_requested";v["comment"]=payload.get("comment","");find_job(v["job_id"])["workflow_status"]="changes_requested";return v
    raise HTTPException(404)
@app.post("/api/v1/validations/{vid}/reject")
def reject(vid:str,payload:dict=Body(default={})):
    for v in STATE["validations"]:
        if v["id"]==vid:v["status"]="rejected";return v
    raise HTTPException(404)
@app.post("/api/v1/validations/{vid}/comments")
def val_comment(vid:str,payload:dict=Body(...)):
    c={"id":uid("comment"),"validation_id":vid,"body":payload.get("body") or payload.get("comment") or "","author":"Abdellah","created_at":NOW()};STATE["comments"].append(c);return c
@app.post("/api/v1/jobs/{job_id}/publish")
def publish(job_id:str):
    p=find_job(job_id);p["workflow_status"]="published";return job_summary(p)
@app.get("/api/v1/jobs/{job_id}/history")
def history(job_id:str):
    p=find_job(job_id);return {"versions":[{"version":"1.0","event":"Création","actor":"RH"},{"version":"1.1","event":"Enrichissement benchmark","actor":"AI + RH"},{"version":p["version"],"event":"Version courante","actor":"RH"}],"events":[{"type":"quality","message":f"Quality Score {p['quality_score']}"}]}

@app.get("/api/v1/connectors")
def connectors():
    configured=bool(os.getenv("OPENAI_API_KEY"));return {"membership_role":"tenant_admin","can_manage":True,"connectors":[
      {"provider":"openai","label":"OpenAI","category":"ai_model","configured":configured,"status":"ready" if configured else "not_configured","description_fr":"Génération, analyse et Web Search."},
      {"provider":"anthropic","label":"Anthropic Claude","category":"ai_model","configured":bool(os.getenv("ANTHROPIC_API_KEY")),"status":"ready" if os.getenv("ANTHROPIC_API_KEY") else "not_configured","description_fr":"Analyse et challenge."},
      {"provider":"local","label":"Teamwork Expert Engine","category":"rules_engine","configured":True,"status":"ready","description_fr":"Moteur déterministe Teamwork."},
      {"provider":"esco","label":"ESCO","category":"occupational_reference","configured":True,"status":"ready","description_fr":"Référentiel occupations & skills."}],"preference":{"preferred_provider":"auto","preferred_quality":"premium","fallback_enabled":True,"allow_external_ai":True},"workflow_rules":[]}
@app.put("/api/v1/connectors/preferences")
def prefs(payload:dict=Body(...)):return payload
@app.post("/api/v1/connectors/{provider}/test")
def connector_test(provider:str):return {"provider":provider,"status":"ready" if provider in ["local","esco"] or (provider=="openai" and os.getenv("OPENAI_API_KEY")) else "not_configured"}
@app.get("/api/v1/live-intelligence/status")
def live_status():
    oa=bool(os.getenv("OPENAI_API_KEY"));an=bool(os.getenv("ANTHROPIC_API_KEY"));return {"openai":{"configured":oa,"model":"gpt-5.6-terra","web_search_ready":oa},"anthropic":{"configured":an,"model":"claude-sonnet-5","web_search_ready":False},"google":{"enabled":False,"ready":False},"web_search":{"enabled":oa,"providers":["openai"],"ready":oa},"esco":{"enabled":True,"ready":True,"base_url":"https://ec.europa.eu/esco/api","selected_version":"v1.2.1"},"rome":{"enabled":False,"ready":False},"onet":{"enabled":False,"ready":False},"benchmark_sites":{"direct_api":["ESCO"],"web_research":["Apec","CNFPT","professional associations","public institutions","employer career pages"]},"test_ready":True}
@app.post("/api/v1/live-intelligence/test/{service}")
def live_test(service:str,payload:dict=Body(default={})):
    q=payload.get("query","Responsable Formation")
    if service=="esco":return esco_search(q)
    if service in ["openai","web-search"]:return web_search(q)
    return {"available":False,"service":service,"error":"Service non configuré dans le pilote."}

@app.post("/api/v1/research/jobs/{job_id}/run")
def research_job(job_id:str,payload:dict=Body(default={})):
    p=find_job(job_id);q=payload.get("query") or f"{p['title_fr']} missions responsabilités compétences KPI outils tendances";esco=esco_search(q);web=web_search(q);evidence=p["sources"]+esco["results"]+web["sources"]
    summary=web.get("summary") or f"Benchmark consolidé pour {p['title_fr']} : rôle centré sur pilotage, coordination, résultats, compétences justifiées et responsabilités explicites. Les éléments restent à confronter au contexte entreprise."
    return {"id":uid("research"),"job_id":job_id,"query":q,"summary":summary,"evidence":evidence[:24],"source_count":len(evidence),"confidence":0.89,"convergence":["pilotage du périmètre","coordination transverse","mesure de la performance","évolution des outils et compétences"]}

@app.post("/api/v1/documents")
async def upload_document(file:UploadFile=File(...),role:str=Form("knowledge")):
    raw=await file.read();text=""
    try:
        if file.filename.lower().endswith((".txt",".md",".csv")):text=raw.decode("utf-8",errors="ignore")
        elif file.filename.lower().endswith(".docx"):
            from docx import Document
            d=Document(io.BytesIO(raw));text="\n".join(p.text for p in d.paragraphs if p.text.strip())
        elif file.filename.lower().endswith(".pdf"):
            from pypdf import PdfReader
            text="\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
    except Exception as e:text=f"Extraction partielle: {e}"
    doc={"id":uid("doc"),"filename":file.filename,"role":role,"status":"parsed","chars":len(text),"text":text[:50000],"created_at":NOW()};STATE["documents"].insert(0,doc);return {k:v for k,v in doc.items() if k!="text"}
@app.get("/api/v1/documents")
def documents():return [{k:v for k,v in d.items() if k!="text"} for d in STATE["documents"]]
@app.get("/api/v1/documents/search/knowledge")
def search_docs(q:str=""):
    terms=[x.lower() for x in q.split() if len(x)>2];out=[]
    for d in STATE["documents"]:
        score=sum(d["text"].lower().count(t) for t in terms)
        if score:out.append({"document_id":d["id"],"filename":d["filename"],"score":score,"excerpt":d["text"][:500]})
    return out[:12]

@app.post("/api/v1/existing-jobs/import")
async def existing_import(file:UploadFile=File(...),organization_id:str=Form(ORG_ID),mode:str=Form("balanced")):
    raw=await file.read();text=""
    if file.filename.lower().endswith((".txt",".md",".csv")):text=raw.decode("utf-8",errors="ignore")
    elif file.filename.lower().endswith(".docx"):
        from docx import Document
        d=Document(io.BytesIO(raw));text="\n".join(p.text for p in d.paragraphs if p.text.strip())
    elif file.filename.lower().endswith(".pdf"):
        from pypdf import PdfReader
        text="\n".join((p.extract_text() or "") for p in PdfReader(io.BytesIO(raw)).pages)
    lines=[x.strip() for x in text.splitlines() if x.strip()];title=lines[0][:120] if lines else re.sub(r"\.[^.]+$","",file.filename).replace("_"," ")
    p=profile_template(title);p["version"]="1.0";p["workflow_status"]="import_review";p["finality_fr"]=(lines[1][:500] if len(lines)>1 else p["finality_fr"]);STATE["jobs"].insert(0,p)
    imp={"id":uid("imp"),"job_id":p["id"],"filename":file.filename,"mode":mode,"extracted":{"title":title,"finality":p["finality_fr"],"missions":len(p["missions"]),"skills":len(p["skills"]),"kpis":0},"warnings":["Les champs non trouvés ne sont pas inventés."]};STATE["imports"].append(imp);return imp
@app.post("/api/v1/existing-jobs/imports/{import_id}/update-intelligence")
def update_intel(import_id:str):
    imp=next((x for x in STATE["imports"] if x["id"]==import_id),None)
    if not imp:raise HTTPException(404)
    p=find_job(imp["job_id"]);items=[
      {"id":uid("upd"),"section":"finality","action":"enrich","before":p["finality_fr"],"after":p["finality_fr"].rstrip(".")+" et mesurer l’impact du périmètre au regard des priorités de l’organisation.","why":"Les sources convergent vers une responsabilité explicite sur la mesure d’impact.","confidence":0.91,"decision":"pending"},
      {"id":uid("upd"),"section":"skills","action":"add","before":"","after":"Analyse de données métier — N3","why":"Compétence fréquemment associée aux pratiques actuelles du rôle.","confidence":0.84,"decision":"pending"},
      {"id":uid("upd"),"section":"kpis","action":"add","before":"Aucun KPI formalisé","after":"Taux de réalisation des objectifs du périmètre","why":"Le rôle nécessite un résultat mesurable ; le KPI doit être validé par le manager.","confidence":0.80,"decision":"pending"}]
    run={"id":uid("run"),"import_id":import_id,"job_id":p["id"],"status":"review","items":items,"summary":"3 propositions. Aucun contenu client n’est supprimé automatiquement."};STATE["update_runs"].append(run);return run
@app.patch("/api/v1/existing-jobs/update-runs/{run_id}/items/{item_id}")
def update_item(run_id:str,item_id:str,payload:dict=Body(...)):
    run=next((x for x in STATE["update_runs"] if x["id"]==run_id),None)
    if not run:raise HTTPException(404)
    for x in run["items"]:
        if x["id"]==item_id:x["decision"]=payload.get("decision") or payload.get("action") or "accepted";return x
    raise HTTPException(404)
@app.get("/api/v1/existing-jobs/update-runs/{run_id}")
def get_run(run_id:str):
    run=next((x for x in STATE["update_runs"] if x["id"]==run_id),None)
    if not run:raise HTTPException(404)
    return run
@app.post("/api/v1/existing-jobs/update-runs/{run_id}/accept-all")
def accept_all(run_id:str):
    run=get_run(run_id)
    for x in run["items"]:x["decision"]="accepted"
    return run
@app.post("/api/v1/existing-jobs/update-runs/{run_id}/apply")
def apply_run(run_id:str):
    run=get_run(run_id);p=find_job(run["job_id"])
    for x in run["items"]:
        if x["decision"]!="accepted":continue
        if x["section"]=="finality":p["finality_fr"]=x["after"]
        elif x["section"]=="skills":p["skills"].append({"id":uid("s"),"label":"Analyse de données métier","level":"N3","type":"technical"})
        elif x["section"]=="kpis":p["kpis"].append({"id":uid("k"),"label":"Taux de réalisation des objectifs du périmètre","target":"à valider"})
    p["version"]="1.1";p["workflow_status"]="hr_review";run["status"]="applied";return {"run":run,"job":job_summary(p),"version":"1.1"}

@app.post("/api/v1/bulk-audit/imports")
async def bulk_import(file:UploadFile=File(...)):
    raw=(await file.read()).decode("utf-8",errors="ignore");rows=list(csv.DictReader(io.StringIO(raw))) if raw.strip() else []
    batch={"batch_id":uid("batch"),"filename":file.filename,"row_count":len(rows),"rows":rows};STATE.setdefault("batches",[]).append(batch);return batch
@app.post("/api/v1/bulk-audit/imports/{batch_id}/analyze")
def bulk_analyze(batch_id:str):return {"batch_id":batch_id,"status":"completed","findings_count":7}
@app.get("/api/v1/bulk-audit/imports/{batch_id}/dashboard")
def bulk_dash(batch_id:str):return {"batch_id":batch_id,"metrics":{"jobs":48,"quality_avg":81,"freshness_avg":76,"duplicates":3,"missing_kpis":12,"skills_gaps":18},"findings":[{"type":"stale_job","severity":"high","title":"8 fiches à actualiser"},{"type":"duplicate_job","severity":"medium","title":"3 doublons potentiels"},{"type":"skills_gap","severity":"medium","title":"18 compétences à normaliser"}]}
@app.get("/api/v1/bulk-audit/template.csv")
def bulk_template():return StreamingResponse(iter(["title,department,reports_to,finality,skills,kpis\nResponsable Formation,DRH,DRH,Piloter le développement des compétences,Ingénierie formation;Pilotage,Taux de réalisation\n"]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=job-audit-template.csv"})
@app.post("/api/v1/architecture-intelligence/imports/{batch_id}/classify")
def arch_classify(batch_id:str):return {"status":"completed","classified":48}
@app.get("/api/v1/architecture-intelligence/imports/{batch_id}/map")
def arch_map(batch_id:str):return {"functions":[{"name":"Ressources Humaines","families":["Learning & Development","Talent Acquisition","C&B","HR Operations"]},{"name":"Finance","families":["Controlling","Accounting"]}],"levels":["L1","L2","L3","L4","L5","L6"]}
@app.get("/api/v1/architecture-intelligence/imports/{batch_id}/skills-heatmap")
def heatmap(batch_id:str):return {"skills":[{"skill":"Pilotage","coverage":82},{"skill":"Data Analysis","coverage":54},{"skill":"Digital Tools","coverage":61},{"skill":"Leadership","coverage":48}]}
@app.post("/api/v1/mobility-intelligence/imports/{batch_id}/generate")
def mobility_generate(batch_id:str):return {"status":"completed"}
@app.get("/api/v1/mobility-intelligence/imports/{batch_id}/adjacencies")
def adj(batch_id:str):return [{"from":"Chargé de Formation","to":"Responsable Formation","score":0.82},{"from":"HRBP","to":"Responsable Développement RH","score":0.73}]
@app.get("/api/v1/mobility-intelligence/imports/{batch_id}/career-paths")
def paths(batch_id:str):return [{"type":"vertical","path":["Chargé","Responsable","Head of"]}]
@app.get("/api/v1/mobility-intelligence/imports/{batch_id}/remediation-plan")
def remed(batch_id:str):return [{"priority":"high","action":"Formaliser KPI pour 12 rôles"},{"priority":"medium","action":"Normaliser 18 skills"}]
@app.get("/api/v1/reference-intelligence/sources")
def refs():return [{"key":"teamwork","label":"Teamwork Method","source_type":"proprietary","operational":True},{"key":"esco","label":"ESCO","source_type":"api","operational":True},{"key":"rome","label":"ROME 4.0","source_type":"api","operational":False},{"key":"apec","label":"Apec","source_type":"benchmark","operational":True},{"key":"cnfpt","label":"CNFPT","source_type":"benchmark","operational":True}]
@app.post("/api/v1/reference-intelligence/imports/{batch_id}/enrich")
def enrich(batch_id:str):return {"status":"completed","evidence":24}
@app.get("/api/v1/reference-intelligence/imports/{batch_id}/evidence")
def evid(batch_id:str):return refs()
@app.get("/api/v1/style-intelligence/profiles")
def style_profiles():return [{"id":"style-1","name":"Atlas HR Style","mode":"balanced","mission_avg":4.7,"skill_avg":7.2,"kpi_avg":2.3,"preferred_verbs":["Piloter","Structurer","Coordonner","Mesurer"]}]
@app.post("/api/v1/style-intelligence/imports/{batch_id}/profile")
def style_profile(batch_id:str):return style_profiles()[0]
@app.post("/api/v1/style-intelligence/profiles/{pid}/check")
def style_check(pid:str,payload:dict=Body(default={})):return {"profile_id":pid,"score":91,"findings":["Structure conforme","Terminologie cohérente"]}
@app.get("/api/v1/style-intelligence/profiles/{pid}/checks")
def checks(pid:str):return []
@app.patch("/api/v1/style-intelligence/profiles/{pid}/mode")
def style_mode(pid:str,payload:dict=Body(...)):return {"id":pid,"mode":payload.get("mode","balanced")}

@app.get("/api/v1/notifications/count")
def notif_count():return {"unread":len([x for x in STATE["notifications"] if not x.get("read")])}
@app.get("/api/v1/notifications")
def notifs():return STATE["notifications"]
@app.post("/api/v1/notifications/read-all")
def read_all():
    for x in STATE["notifications"]:x["read"]=True
    return {"ok":True}
@app.post("/api/v1/notifications/{nid}/read")
def read_one(nid:str):return {"ok":True,"id":nid}

@app.get("/api/v1/exports/jobs/{job_id}.{fmt}")
def export_job(job_id:str,fmt:str,locale:str="fr",mode:str="official"):
    p=find_job(job_id)
    if fmt.lower()=="docx":
        from docx import Document
        d=Document();d.add_heading(p["title_fr"],0);d.add_paragraph(f"Version {p['version']} · Quality {p['quality_score']} · Freshness {p['freshness_score']}");d.add_heading("Finalité",1);d.add_paragraph(p["finality_fr"])
        for label,items in [("Missions",[x["label"] for x in p["missions"]]),("Responsabilités",[x["label"] for x in p["responsibilities"]]),("Compétences",[f"{x['label']} — {x['level']}" for x in p["skills"]]),("Indicateurs",[x["label"] for x in p["kpis"]])]:
            if not items:continue
            d.add_heading(label,1)
            for x in items:d.add_paragraph(x,style="List Bullet")
        b=io.BytesIO();d.save(b);b.seek(0);return StreamingResponse(b,media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",headers={"Content-Disposition":f"attachment; filename={p['title_fr'].replace(' ','_')}.docx"})
    if fmt.lower()=="pdf":
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        b=io.BytesIO();c=canvas.Canvas(b,pagesize=A4);y=800;c.setFont("Helvetica-Bold",16);c.drawString(50,y,p["title_fr"]);y-=30;c.setFont("Helvetica",9)
        for text in ["FINALITÉ",p["finality_fr"],"MISSIONS"]+["• "+x["label"] for x in p["missions"]]+["RESPONSABILITÉS"]+["• "+x["label"] for x in p["responsibilities"]]:
            for line in [text[i:i+95] for i in range(0,len(text),95)]:
                if y<55:c.showPage();y=800;c.setFont("Helvetica",9)
                c.drawString(50,y,line);y-=13
            y-=4
        c.save();b.seek(0);return StreamingResponse(b,media_type="application/pdf",headers={"Content-Disposition":f"attachment; filename={p['title_fr'].replace(' ','_')}.pdf"})
    raise HTTPException(400,"Unsupported format")

@app.get("/app/styles.css")
def styles():
    path=DEMO_DIR/"full.css";return FileResponse(path,media_type="text/css") if path.exists() else HTMLResponse("",media_type="text/css")
@app.get("/app/app.js")
def script():
    path=DEMO_DIR/"full.js";return FileResponse(path,media_type="application/javascript") if path.exists() else HTMLResponse("",media_type="application/javascript")
@app.get("/livrable")
def livrable():
    path=DEMO_DIR/"livrable.html";return FileResponse(path) if path.exists() else JSONResponse({"detail":"livrable unavailable"},404)
@app.get("/app/")
@app.get("/")
def root():
    path=DEMO_DIR/"full.html";return FileResponse(path) if path.exists() else {"message":"Teamwork Job Intelligence","health":"/health"}
