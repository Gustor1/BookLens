# MediaLens Frontend V2

Interface moderne, immersive et réactive en Next.js pour MediaLens, séparée de l'interface Lab Streamlit actuelle.

## Architecture

- **Next.js 16 (App Router)**
- **TypeScript strict**
- **Tailwind CSS v4** (Palette sombre ardoise, accentuations pétrole/teal, polices éditoriales)
- **Framer Motion** (Transitions fluides respectant `prefers-reduced-motion`)
- **i18n natif** léger (Support FR/EN/ZH, FR par défaut)

## Démarrage rapide

1. **Installer les dépendances** :
   ```bash
   npm install
   ```

2. **Configurer l'environnement** :
   Créez un fichier `.env` ou `.env.local` :
   ```env
   # Laissez vide pour activer le mode démo local avec mocks complets
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

3. **Lancer le serveur de développement** :
   ```bash
   npm run dev
   ```
   L'application sera accessible sur [http://localhost:3000](http://localhost:3000).

4. **Vérifier le code et compiler** :
   ```bash
   npm run lint
   npm run build
   ```

## Mode Démo / Mock

Si la variable `NEXT_PUBLIC_API_BASE_URL` n'est pas définie (ou si le backend est hors ligne), l'application bascule automatiquement en **Mode Démo** :
- Indicateur discret "Mode Démo" dans le ruban supérieur.
- Base de données mockée de 12 livres, 8 films et 8 jeux dans `src/lib/mock/media.ts`.
- Moteur de recommandation local calculant la proximité thématique sur les genres.
- Chatbot simulant des réponses textuelles sur le catalogue.
- Favoris persistés localement dans le `localStorage` du navigateur.

## Internationalization (i18n)

Les dictionnaires de langues sont définis dans `src/lib/i18n/` :
- `fr.json` (Français, par défaut)
- `en.json` (Anglais)
- `zh.json` (Chinois Simplifié)

Les URL sont structurées sous la forme `/[locale]/explore` pour respecter le SEO. Le composant `LanguageSelector` permet de basculer la langue de façon fluide en conservant la route actuelle.
