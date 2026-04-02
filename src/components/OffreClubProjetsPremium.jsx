import React, { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Users,
  Target,
  Layers3,
  Sparkles,
  Brain,
  Briefcase,
  ChevronDown,
  ShieldCheck,
  Presentation,
  BarChart3,
  Lightbulb,
  Workflow,
  Wand2,
} from "lucide-react";

const levels = [
  {
    id: "n1",
    badge: "Niveau 1",
    title: "Tronc commun",
    subtitle: "Poser les bases, partager un langage commun, structurer les bons réflexes projet.",
    color: "from-slate-900 via-slate-800 to-slate-900",
    sessions: [
      {
        title: "Webinaire 1 — Les fondamentaux de la gestion de projet",
        points: [
          "Définition d’un projet et typologies de projets",
          "Cycle de vie, rôles et responsabilités",
          "Facteurs clés de réussite",
          "Lecture d’un mini-cas projet",
        ],
      },
      {
        title: "Webinaire 2 — Cadrer un projet efficacement",
        points: [
          "Formalisation du besoin",
          "Définition des objectifs et des livrables",
          "Périmètre et parties prenantes",
          "Exercice de cadrage simplifié",
        ],
      },
      {
        title: "Webinaire 3 — Planifier et organiser son projet",
        points: [
          "Découpage des tâches",
          "Jalons et échéancier",
          "Introduction au diagramme de Gantt",
          "Répartition des responsabilités",
        ],
      },
      {
        title: "Webinaire 4 — Suivre et piloter l’avancement",
        points: [
          "Suivi des délais, coûts et qualité",
          "Indicateurs de pilotage",
          "Gestion des écarts",
          "Bonnes pratiques de reporting projet",
        ],
      },
      {
        title: "Webinaire 5 — Atelier de consolidation (optionnel)",
        points: [
          "Étude de cas fil rouge",
          "Mise en pratique collective",
          "Débrief et recommandations opérationnelles",
        ],
      },
    ],
  },
  {
    id: "ia",
    badge: "Module bonus",
    title: "IA au service de la gestion de projet",
    subtitle: "Un bloc court, concret et immédiatement utile pour gagner en efficacité après l’acquisition des fondamentaux.",
    color: "from-amber-500 via-orange-500 to-yellow-500",
    sessions: [
      {
        title: "Webinaire bonus 1 — Découvrir les usages de l’IA en gestion de projet",
        points: [
          "Panorama des apports de l’IA dans l’environnement projet",
          "Cas d’usage concrets pour les chefs de projet",
          "Aide à la rédaction : cadrage, objectifs, comptes rendus, plans d’action",
          "Bonnes pratiques d’utilisation et points de vigilance",
        ],
      },
      {
        title: "Webinaire bonus 2 — Utiliser l’IA pour gagner en efficacité dans le pilotage projet",
        points: [
          "Aide à la planification et à la structuration des tâches",
          "Préparation des supports de communication projet",
          "Synthèse d’informations, suivi des actions et des décisions",
          "Prompts utiles et atelier pratique sur cas projet",
        ],
      },
    ],
  },
  {
    id: "n2",
    badge: "Niveau 2",
    title: "Management de projet avancé",
    subtitle: "Renforcer la maîtrise opérationnelle, coordonner efficacement et gérer la complexité terrain.",
    color: "from-sky-900 via-blue-900 to-slate-900",
    sessions: [
      {
        title: "Webinaire 1 — Planification avancée et coordination",
        points: [
          "Planification détaillée",
          "Dépendances, contraintes et arbitrages",
          "Réajustements et coordination des acteurs projet",
        ],
      },
      {
        title: "Webinaire 2 — Gestion des risques projet",
        points: [
          "Identification et analyse des risques",
          "Évaluation de l’impact et de la probabilité",
          "Plans de traitement et outils de suivi",
        ],
      },
      {
        title: "Webinaire 3 — Communication projet et gestion des parties prenantes",
        points: [
          "Cartographie des parties prenantes",
          "Communication adaptée selon les interlocuteurs",
          "Gestion des attentes, alignement et mobilisation",
        ],
      },
      {
        title: "Webinaire 4 — Management d’équipe projet",
        points: [
          "Animation d’équipe transverse",
          "Motivation et responsabilisation",
          "Gestion des tensions et posture du chef de projet",
        ],
      },
      {
        title: "Webinaire 5 — Retour d’expérience et résolution de cas (optionnel)",
        points: [
          "Analyse de situations réelles",
          "Décryptage de projets en difficulté",
          "Capitalisation sur les bonnes pratiques",
        ],
      },
    ],
  },
  {
    id: "n3",
    badge: "Niveau 3",
    title: "Pilotage stratégique et excellence projet",
    subtitle: "Développer une vision stratégique, arbitrer dans la complexité et piloter la valeur.",
    color: "from-emerald-900 via-teal-900 to-slate-900",
    sessions: [
      {
        title: "Webinaire 1 — Pilotage stratégique des projets",
        points: [
          "Alignement entre projet et stratégie",
          "Gouvernance et instances de pilotage",
          "Arbitrages stratégiques et lecture de la performance projet",
        ],
      },
      {
        title: "Webinaire 2 — Gestion multi-projets et priorisation",
        points: [
          "Logique portefeuille projets",
          "Priorisation selon la valeur, l’urgence et les ressources",
          "Allocation des moyens et vision transverse",
        ],
      },
      {
        title: "Webinaire 3 — Agilité, Scrum et Lean",
        points: [
          "Fondamentaux des approches agiles",
          "Principes Scrum",
          "Apports du Lean en gestion de projet",
          "Choix de la bonne approche selon le contexte",
        ],
      },
      {
        title: "Webinaire 4 — Anticipation des risques complexes et conduite du changement",
        points: [
          "Risques complexes et interdépendances",
          "Gestion de l’incertitude",
          "Accompagnement du changement",
          "Facteurs humains dans la réussite des projets",
        ],
      },
      {
        title: "Webinaire 5 — Masterclass expert / clinique projet (optionnel)",
        points: [
          "Analyse de cas complexes",
          "Échange expert-participants",
          "Recommandations personnalisées",
        ],
      },
    ],
  },
];

const strengths = [
  {
    icon: Target,
    title: "Progression claire",
    text: "Un parcours pensé pour faire évoluer les participants des fondamentaux vers le pilotage stratégique.",
  },
  {
    icon: Presentation,
    title: "Format compatible terrain",
    text: "Des webinaires interactifs de 3h maximum pour concilier montée en compétence et contraintes opérationnelles.",
  },
  {
    icon: Lightbulb,
    title: "Orientation pratique",
    text: "Cas concrets, mises en situation, outils réutilisables et exercices directement connectés au quotidien des participants.",
  },
  {
    icon: Brain,
    title: "Ouverture sur l’IA",
    text: "Un module bonus pour montrer comment l’IA peut accélérer la structuration, la communication et le suivi des projets.",
  },
];

const pedagogy = [
  "Apports méthodologiques clairs et structurés",
  "Études de cas et mises en situation guidées",
  "Sondages, quiz, questions-réponses et échanges d’expérience",
  "Boîte à outils directement mobilisable en situation de travail",
  "Synthèse opérationnelle à l’issue de chaque session",
];

const organization = [
  { label: "Format", value: "Webinaires interactifs à distance" },
  { label: "Durée", value: "3h maximum par session" },
  { label: "Rythme recommandé", value: "1 à 2 webinaires par mois" },
  { label: "Architecture", value: "3 niveaux + 1 module IA bonus" },
];

const pricing = [
  {
    title: "Option 1",
    subtitle: "Niveau à l’unité",
    details: [
      "1 niveau complet",
      "4 webinaires de 3h maximum",
      "12h d’animation",
      "Tarif HT : à compléter",
    ],
  },
  {
    title: "Option 2",
    subtitle: "Niveau renforcé",
    details: [
      "1 niveau complet",
      "5 webinaires de 3h maximum",
      "15h d’animation",
      "Atelier de consolidation inclus",
      "Tarif HT : à compléter",
    ],
    featured: true,
  },
  {
    title: "Option 3",
    subtitle: "Parcours global",
    details: [
      "3 niveaux complets",
      "12 à 15 webinaires selon l’option retenue",
      "36h à 45h d’animation",
      "Module IA bonus intégrable",
      "Tarif HT : à compléter",
    ],
  },
];

function SectionTitle({ eyebrow, title, text }) {
  return (
    <div className="max-w-3xl">
      <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-amber-300">
        <Sparkles className="h-3.5 w-3.5" />
        {eyebrow}
      </div>
      <h2 className="text-3xl font-semibold tracking-tight text-white md:text-4xl">{title}</h2>
      <p className="mt-4 text-base leading-7 text-slate-300 md:text-lg">{text}</p>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-sm">
      <div className="mb-3 inline-flex rounded-2xl bg-white/10 p-3 text-amber-300">
        <Icon className="h-5 w-5" />
      </div>
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-1 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function SessionAccordion({ items, accent = "from-amber-400 to-orange-500" }) {
  const [openIndex, setOpenIndex] = useState(0);

  return (
    <div className="space-y-4">
      {items.map((item, index) => {
        const open = openIndex === index;
        return (
          <div key={item.title} className="overflow-hidden rounded-3xl border border-white/10 bg-white/5 backdrop-blur-sm">
            <button
              onClick={() => setOpenIndex(open ? -1 : index)}
              className="flex w-full items-center justify-between gap-4 p-5 text-left transition hover:bg-white/5"
            >
              <div className="flex items-start gap-4">
                <div className={`mt-1 h-10 w-1 rounded-full bg-gradient-to-b ${accent}`} />
                <div>
                  <div className="text-base font-semibold text-white md:text-lg">{item.title}</div>
                </div>
              </div>
              <ChevronDown className={`h-5 w-5 shrink-0 text-slate-300 transition ${open ? "rotate-180" : ""}`} />
            </button>
            <AnimatePresence initial={false}>
              {open && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25 }}
                >
                  <div className="px-5 pb-5 pl-10 md:pl-14">
                    <ul className="space-y-3">
                      {item.points.map((point) => (
                        <li key={point} className="flex items-start gap-3 text-slate-300">
                          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
                          <span>{point}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}

function OfferCard({ title, subtitle, details, featured = false }) {
  return (
    <div
      className={`relative rounded-[28px] border p-6 ${
        featured
          ? "border-amber-400/50 bg-gradient-to-b from-amber-400/10 to-white/5 shadow-2xl shadow-amber-500/10"
          : "border-white/10 bg-white/5"
      }`}
    >
      {featured && (
        <div className="absolute right-4 top-4 rounded-full bg-amber-300 px-3 py-1 text-xs font-semibold text-slate-900">
          Recommandée
        </div>
      )}
      <div className="text-sm uppercase tracking-[0.2em] text-slate-400">{title}</div>
      <h3 className="mt-2 text-2xl font-semibold text-white">{subtitle}</h3>
      <ul className="mt-6 space-y-3">
        {details.map((detail) => (
          <li key={detail} className="flex items-start gap-3 text-slate-300">
            <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-amber-300" />
            <span>{detail}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function OffreClubProjetsPremium() {
  const metrics = useMemo(
    () => [
      { icon: Layers3, label: "Niveaux de progression", value: "3 niveaux structurés" },
      { icon: Clock3, label: "Format des sessions", value: "3h max par webinaire" },
      { icon: Users, label: "Dynamique d’apprentissage", value: "Interactive, pratique, continue" },
      { icon: Wand2, label: "Extension innovation", value: "2 webinaires bonus IA" },
    ],
    []
  );

  return (
    <div className="min-h-screen bg-[#07111f] text-slate-100">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute left-[-10%] top-[-10%] h-[420px] w-[420px] rounded-full bg-amber-500/10 blur-3xl" />
        <div className="absolute right-[-8%] top-[12%] h-[360px] w-[360px] rounded-full bg-cyan-500/10 blur-3xl" />
        <div className="absolute bottom-[-10%] left-[20%] h-[340px] w-[340px] rounded-full bg-emerald-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-7xl px-6 py-10 md:px-8 lg:px-10">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="overflow-hidden rounded-[36px] border border-white/10 bg-gradient-to-br from-slate-900/95 via-[#0d1b30]/95 to-slate-950/95 p-8 shadow-2xl shadow-black/30 md:p-12"
        >
          <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-amber-400/20 bg-amber-300/10 px-4 py-2 text-sm font-medium text-amber-200">
                <Sparkles className="h-4 w-4" />
                Proposition premium — Parcours de formation en gestion de projet
              </div>
              <h1 className="mt-6 max-w-4xl text-4xl font-semibold leading-tight tracking-tight text-white md:text-6xl">
                Une offre élégante, progressive et orientée terrain pour faire monter vos équipes en puissance sur la gestion de projet.
              </h1>
              <p className="mt-6 max-w-3xl text-lg leading-8 text-slate-300 md:text-xl">
                Un dispositif structuré en trois niveaux, animé sous forme de webinaires interactifs, enrichi par un module bonus dédié aux usages concrets de l’IA au service du pilotage projet.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">Approche progressive</div>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">Pédagogie active</div>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">Cas concrets</div>
                <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200">Module IA bonus</div>
              </div>
            </div>

            <div className="grid gap-4 sm:grid-cols-2">
              {metrics.map((metric) => (
                <MetricCard key={metric.label} {...metric} />
              ))}
            </div>
          </div>
        </motion.section>

        <section className="mt-10 grid gap-6 lg:grid-cols-2">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
            <SectionTitle
              eyebrow="Vision"
              title="Compréhension du besoin"
              text="Le dispositif vise à installer une dynamique d’apprentissage continue autour de la gestion de projet, à travers des sessions utiles, participatives et directement connectées à la réalité des participants."
            />
            <div className="mt-8 space-y-4 text-slate-300">
              <p>
                L’ambition n’est pas seulement de transmettre des concepts, mais de faire évoluer durablement les pratiques projet au sein des équipes, en créant un parcours progressif, lisible et compatible avec les contraintes opérationnelles.
              </p>
              <p>
                Ce positionnement permet de passer d’un simple enchaînement de webinaires à une véritable trajectoire de professionnalisation, avec une montée en compétence structurée du socle fondamental vers la maîtrise avancée et le pilotage stratégique.
              </p>
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-gradient-to-br from-white/10 to-white/5 p-8 backdrop-blur-sm">
            <SectionTitle
              eyebrow="Promesse"
              title="Les objectifs du parcours"
              text="Faire progresser les participants avec méthode, fluidité et impact opérationnel."
            />
            <div className="mt-8 grid gap-4">
              {[
                "Maîtriser les fondamentaux de la gestion de projet",
                "Structurer efficacement le cadrage, la planification et le suivi",
                "Renforcer la gestion des risques, des parties prenantes et des équipes projet",
                "Développer une vision stratégique et agile du pilotage des projets",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/30 p-4">
                  <ShieldCheck className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span className="text-slate-200">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-20">
          <SectionTitle
            eyebrow="Architecture pédagogique"
            title="Un parcours en 3 niveaux, enrichi par un module IA bonus"
            text="Chaque niveau peut être déployé en 4 à 5 webinaires de 3h maximum. Le module IA vient naturellement s’insérer après le tronc commun pour apporter un levier immédiat de productivité et de qualité dans la pratique projet."
          />
          <div className="mt-10 space-y-8">
            {levels.map((level, i) => (
              <motion.div
                key={level.id}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, amount: 0.2 }}
                transition={{ duration: 0.45, delay: i * 0.05 }}
                className="overflow-hidden rounded-[32px] border border-white/10 bg-white/5 backdrop-blur-sm"
              >
                <div className={`bg-gradient-to-r ${level.color} p-8`}>
                  <div className="mb-4 inline-flex rounded-full border border-white/15 bg-white/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/90">
                    {level.badge}
                  </div>
                  <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr] lg:items-end">
                    <div>
                      <h3 className="text-3xl font-semibold text-white">{level.title}</h3>
                      <p className="mt-3 max-w-3xl text-base leading-7 text-white/80">{level.subtitle}</p>
                    </div>
                    <div className="rounded-3xl border border-white/10 bg-black/15 p-5 text-sm leading-7 text-white/90">
                      {level.id === "ia"
                        ? "Positionné juste après le Niveau 1, ce module permet de transformer les bases acquises en gains de temps concrets grâce à l’IA : structuration, synthèse, communication, planification et suivi."
                        : "Chaque niveau s’inscrit dans une logique de progression claire, avec une pédagogie orientée terrain et des contenus immédiatement mobilisables dans les projets du quotidien."}
                    </div>
                  </div>
                </div>
                <div className="p-6 md:p-8">
                  <SessionAccordion
                    items={level.sessions}
                    accent={level.id === "ia" ? "from-amber-300 to-orange-500" : level.id === "n2" ? "from-cyan-300 to-blue-500" : level.id === "n3" ? "from-emerald-300 to-teal-500" : "from-amber-300 to-yellow-500"}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </section>

        <section className="mt-20 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
            <SectionTitle
              eyebrow="Approche pédagogique"
              title="Une logique de formation-action, vive et participative"
              text="Chaque session alterne apports méthodologiques, interactions, cas pratiques, temps de débrief et synthèse opérationnelle. L’objectif est de favoriser l’appropriation réelle, pas seulement la compréhension théorique."
            />
            <div className="mt-8 grid gap-4 md:grid-cols-2">
              {pedagogy.map((item) => (
                <div key={item} className="rounded-2xl border border-white/10 bg-slate-950/30 p-4 text-slate-200">
                  <div className="flex items-start gap-3">
                    <Workflow className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                    <span>{item}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-gradient-to-br from-slate-900/90 to-slate-800/60 p-8">
            <SectionTitle
              eyebrow="Format type"
              title="Le rythme d’un webinaire de 3h"
              text="Un format pensé pour maintenir l’attention, favoriser l’engagement et garantir une sortie utile à chaque session."
            />
            <div className="mt-8 space-y-4">
              {[
                ["1", "Ouverture & cadrage", "Objectifs, recueil des attentes, mise en dynamique"],
                ["2", "Apports structurés", "Méthodes, repères, outils et modèles"],
                ["3", "Mise en pratique", "Étude de cas, mini-atelier ou exercice guidé"],
                ["4", "Débrief & échanges", "Questions-réponses, partage d’expérience, points de vigilance"],
                ["5", "Synthèse opérationnelle", "Messages clés et recommandations de mise en œuvre"],
              ].map(([step, title, desc]) => (
                <div key={step} className="flex gap-4 rounded-2xl border border-white/10 bg-white/5 p-4">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl bg-amber-300 font-semibold text-slate-900">{step}</div>
                  <div>
                    <div className="font-semibold text-white">{title}</div>
                    <div className="mt-1 text-sm leading-6 text-slate-300">{desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="mt-20 grid gap-6 lg:grid-cols-2">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
            <SectionTitle
              eyebrow="Intervenants"
              title="Des profils crédibles, orientés terrain"
              text="L’animation du parcours est assurée par des intervenants expérimentés en gestion de projet, pilotage de la performance, méthodes agiles, conduite du changement et facilitation à distance."
            />
            <div className="mt-8 space-y-4">
              {[
                "Expertise confirmée en gestion et management de projet",
                "Expérience concrète dans l’accompagnement de projets et de transformations",
                "Maîtrise des approches classiques, agiles et collaboratives",
                "Capacité à relier les contenus aux réalités métier des participants",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3 rounded-2xl border border-white/10 bg-slate-950/30 p-4 text-slate-200">
                  <Briefcase className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[32px] border border-white/10 bg-white/5 p-8 backdrop-blur-sm">
            <SectionTitle
              eyebrow="Organisation"
              title="Modalités de déploiement"
              text="Le dispositif peut être déployé de manière souple selon le rythme et le niveau de personnalisation attendus."
            />
            <div className="mt-8 grid gap-4">
              {organization.map((item) => (
                <div key={item.label} className="flex items-start justify-between gap-4 rounded-2xl border border-white/10 bg-slate-950/30 p-4">
                  <div className="text-sm uppercase tracking-[0.18em] text-slate-400">{item.label}</div>
                  <div className="max-w-[55%] text-right font-medium text-white">{item.value}</div>
                </div>
              ))}
              <div className="rounded-2xl border border-dashed border-amber-400/40 bg-amber-300/5 p-4 text-sm leading-7 text-slate-300">
                Les supports, outils, cas pratiques, éventuelles fiches de synthèse et modalités d’évaluation peuvent être ajustés selon le périmètre retenu et le public cible.
              </div>
            </div>
          </div>
        </section>

        <section className="mt-20">
          <SectionTitle
            eyebrow="Différenciation"
            title="Les forces de la proposition"
            text="Une offre pensée pour être lisible, engageante et hautement actionnable."
          />
          <div className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
            {strengths.map((item, i) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.2 }}
                  transition={{ duration: 0.35, delay: i * 0.05 }}
                  className="rounded-[28px] border border-white/10 bg-white/5 p-6 backdrop-blur-sm"
                >
                  <div className="mb-4 inline-flex rounded-2xl bg-amber-300/10 p-3 text-amber-300">
                    <Icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-xl font-semibold text-white">{item.title}</h3>
                  <p className="mt-3 leading-7 text-slate-300">{item.text}</p>
                </motion.div>
              );
            })}
          </div>
        </section>

        <section className="mt-20 rounded-[36px] border border-white/10 bg-gradient-to-br from-slate-900 via-[#0e1f36] to-slate-950 p-8 md:p-10">
          <div className="grid gap-8 xl:grid-cols-[1fr_1.1fr]">
            <div>
              <SectionTitle
                eyebrow="Proposition financière"
                title="Une structure tarifaire claire et flexible"
                text="La tarification peut être affinée selon le nombre de niveaux retenus, le volume de sessions, le degré de personnalisation attendu et l’intégration du module IA bonus."
              />
              <div className="mt-6 rounded-3xl border border-dashed border-white/15 bg-white/5 p-5 text-sm leading-7 text-slate-300">
                La proposition financière pourra inclure la conception pédagogique, la préparation des supports, l’animation des webinaires, la coordination du dispositif ainsi que la remise des supports participants.
              </div>
            </div>
            <div className="grid gap-5 lg:grid-cols-3">
              {pricing.map((card) => (
                <OfferCard key={card.title} {...card} />
              ))}
            </div>
          </div>
        </section>

        <section className="mt-20 rounded-[36px] border border-white/10 bg-white/5 p-8 backdrop-blur-sm md:p-10">
          <div className="grid gap-8 lg:grid-cols-[1fr_0.95fr] lg:items-center">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-amber-300">
                <BarChart3 className="h-3.5 w-3.5" />
                Conclusion
              </div>
              <h2 className="mt-4 text-3xl font-semibold tracking-tight text-white md:text-4xl">
                Une trajectoire de professionnalisation complète, moderne et immédiatement utile.
              </h2>
              <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300 md:text-lg">
                Cette proposition constitue une base de travail premium, structurée pour répondre aux enjeux de montée en compétence en gestion de projet, tout en offrant une expérience d’apprentissage engageante, progressive et concrète.
              </p>
              <p className="mt-4 max-w-3xl text-base leading-8 text-slate-300 md:text-lg">
                Elle pourra être affinée selon le public cible, le rythme de déploiement, les thématiques prioritaires et le niveau de personnalisation souhaité.
              </p>
            </div>
            <div className="rounded-[32px] border border-amber-400/20 bg-gradient-to-br from-amber-300/10 to-white/5 p-6">
              <div className="text-sm uppercase tracking-[0.2em] text-amber-300">Signature de l’offre</div>
              <div className="mt-3 text-2xl font-semibold text-white">
                Apprendre, structurer, piloter — et demain, augmenter la performance projet avec intelligence.
              </div>
              <div className="mt-6 space-y-3 text-slate-300">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span>3 niveaux progressifs</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span>Webinaires interactifs et pratiques</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span>Module IA bonus après le tronc commun</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-amber-300" />
                  <span>Format premium prêt à être personnalisé</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
