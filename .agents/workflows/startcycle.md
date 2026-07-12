---
description: Lance un pipeline multi-passes de spécification, génération, audit et lancement
---

Quand l’utilisateur tape `/startcycle <idee>`, exécute cette séquence :

1. Agis comme **Product Manager** et utilise le skill `write_specs.md`.
2. Arrête-toi et attends une validation explicite de l’utilisateur.
3. Une fois validé, agis comme **Full-Stack Engineer** et utilise `generate_code.md`.
4. Ensuite, agis comme **QA Engineer** et utilise `audit_code.md`.
5. Enfin, agis comme **DevOps Master** et utilise `deploy_app.md`.

Si l’utilisateur refuse ou demande des modifications à la spec, retourne à l’étape 1.