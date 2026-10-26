# Contenido del perfil. Fuente: portafolio (src/data/*.ts) y brain David-AI.
# Para cambiar algo del perfil se edita este archivo y se corre: python3 scripts/build.py

NOMBRE = "Jordan Aragon"
PROMPT = "jordan@aragon ~ %"
TITULO = "Desarrollador de software"
TITULO_2 = "IA, automatización e infraestructura"
TITULAR = "Construyo software, agentes de IA e infraestructura que funcionan en producción."
UBICACION = "Cali, Colombia · UTC−5"
ESTADO = "Disponible para proyectos"
SITIO = "jordanco.club"

TERMINAL = [
    ("cmd", "cat sobre-mi.txt"),
    ("out", "Empecé arreglando computadores y redes. Esa curiosidad por entender cómo funcionan las cosas me llevó a construirlas: hoy hago webs, agentes de IA y automatizaciones para clientes reales."),
    ("cmd", "cat ahora.txt"),
    ("item", "Líder técnico en Ocean Industries: webs, agentes de IA y automatización"),
    ("item", "Construyendo AiDEN, gestión para viveros con un agente de IA"),
    ("item", "Operando Aragon Server: diez servicios en mi propio servidor"),
    ("item", "Estudiando Ingeniería de Sistemas (UNAD) y ADSO (SENA)"),
    ("cmd", "open jordanco.club"),
]

SERVICIOS = [
    ("web", "Producto web", "Sitios y plataformas con SSR, rutas tipadas y diseño propio.", "React · Next.js · TanStack · Astro"),
    ("ia", "IA y agentes", "Agentes que atienden llamadas y chats, con salidas estructuradas y validadas.", "Claude · Gemini · LiveKit · ElevenLabs"),
    ("auto", "Automatización", "Flujos que conectan herramientas de negocio, pagos y medición.", "n8n · Webhooks · Wompi · GA4"),
    ("infra", "Infraestructura", "Servidores propios, contenedores, redes privadas y despliegue continuo.", "Linux · Docker · Caddy · Tailscale"),
]

# (grupo, [(nombre, slug de Simple Icons o None)])
STACK = [
    ("Producto web", [("TypeScript", "typescript"), ("JavaScript", "javascript"), ("React", "react"), ("Next.js", "nextdotjs"), ("TanStack Start", "tanstack"), ("Astro", "astro"), ("Preact", "preact"), ("Vite", "vite"), ("Tailwind CSS", "tailwindcss"), ("HTML", "html5"), ("CSS", "css")]),
    ("Backend y datos", [("Node.js", "nodedotjs"), ("Express", "express"), ("Python", "python"), ("Django", "django"), ("PostgreSQL", "postgresql"), ("Supabase", "supabase"), ("Redis", "redis"), ("Zod", "zod"), ("SQL", None)]),
    ("IA y voz", [("Claude", "claude"), ("Claude Code", "anthropic"), ("OpenAI", None), ("Gemini", "googlegemini"), ("ElevenLabs", "elevenlabs"), ("LiveKit", "livekit"), ("Deepgram", "deepgram"), ("Telnyx · SIP", None)]),
    ("Automatización", [("n8n", "n8n"), ("Webhooks", None), ("Wompi", None), ("GA4", "googleanalytics"), ("Meta CAPI", "meta"), ("Jobber", None)]),
    ("Infraestructura", [("Linux", "linux"), ("Ubuntu Server", "ubuntu"), ("Docker", "docker"), ("Docker Compose", "docker"), ("Caddy", "caddy"), ("Tailscale", "tailscale"), ("Vercel", "vercel"), ("Cloudflare", "cloudflare"), ("GitHub Actions", "githubactions"), ("Git", "git"), ("GitHub", "github")]),
    ("Calidad y 3D", [("Playwright", None), ("Lighthouse", "lighthouse"), ("WCAG AA", None), ("SEO técnico", None), ("WebGPU · vgpu", "webgpu"), ("Canvas 2D", None)]),
    ("Herramientas", [("Figma", "figma"), ("VS Code", None), ("Obsidian", "obsidian"), ("Arduino", "arduino"), ("WordPress", "wordpress"), ("WooCommerce", "woocommerce")]),
]

# (archivo, título, estado, tipo de estado, descripción, stack, url visible, enlace, letra de la matriz)
PROYECTOS = [
    ("aiden", "AiDEN", "En producción", "vivo",
     "Plataforma web que sigue cada lote de un vivero de la siembra al despacho: producción, trazabilidad, costos y reportes, con un agente de IA y un vivero en 3D.",
     "React 19 · Supabase · WebGPU · Playwright", "aidencol.vercel.app", "https://aidencol.vercel.app", "A"),
    ("aragon", "Aragon", "En producción", "vivo",
     "El sitio de mi agencia de software: servicios con demos que funcionan, cómo trabajamos y contacto, con un campo de partículas que ordena lo que toca el cursor.",
     "Next.js 16 · React 19 · WebGPU · Canvas 2D", "aragons.vercel.app", "https://aragons.vercel.app", "R"),
    ("aragon-server", "Aragon Server", "Activo", "vivo",
     "Mi propio servidor: diez servicios en contenedores con proxy inverso, acceso remoto privado por Tailscale y monitorización.",
     "Linux · Docker · Caddy · Tailscale · PostgreSQL", "jordanco.club/projects/aragon-server", "https://www.jordanco.club/projects/aragon-server", "S"),
    ("portafolio", "Portafolio", "En producción", "vivo",
     "Terminal funcional, paleta ⌘K, casos de estudio y un retrato segmentado con MediaPipe. Es la versión larga de este perfil.",
     "TanStack Start · React 19 · Tailwind 4", "jordanco.club", "https://www.jordanco.club", "J"),
    ("leidy", "Leidy Micolta", "Cliente", "cliente",
     "Portafolio editorial por capítulos para una psicóloga de Popayán y Cali, con una versión de lectura indexable y SEO local.",
     "React 19 · Vite · Tailwind 4 · JSON-LD", "leidymicolta.vercel.app", "https://leidymicolta.vercel.app", "L"),
    ("calendar", "Calendar", "En desarrollo", "dev",
     "Calendario personal con asistente en lenguaje natural: Gemini propone, el backend valida con Zod y solo entonces toca la base de datos.",
     "React · Express 5 · Zod · Supabase · Gemini", "jordanco.club/projects/calendar", "https://www.jordanco.club/projects/calendar", "C"),
]

EXPERIENCIA = [
    ("Ocean Industries", "Sep 2026 — hoy", "Desarrollador de software, IA y automatización", "Líder técnico de la agencia: webs, pagos, medición y agentes de IA para clientes en Colombia y Estados Unidos."),
    ("Federación Nacional de Cafeteros", "Jul 2024 — Ago 2025", "Aprendiz técnico · Comité del Cauca", "Mantenimiento de equipos de cómputo, redes y soporte en Popayán."),
]
FORMACION = [
    ("Ingeniería de Sistemas", "UNAD", "2024 — en curso"),
    ("Tecnólogo en Análisis y Desarrollo de Software", "SENA", "2025 — en curso"),
    ("Técnico en Mantenimiento de Equipos de Cómputo", "SENA", "2025 · titulado"),
]

CONTACTO = [
    ("portafolio", "Portafolio", "jordanco.club", "https://www.jordanco.club"),
    ("aragon", "Aragon", "agencia de software", "https://aragons.vercel.app"),
    ("linkedin", "LinkedIn", "in/jordanaragon", "https://www.linkedin.com/in/jordanaragon"),
    ("correo", "Correo", "jordandavidaragon@outlook.com", "mailto:jordandavidaragon@outlook.com"),
]

CIERRE = "Construyo, aprendo y mejoro un proyecto a la vez."
