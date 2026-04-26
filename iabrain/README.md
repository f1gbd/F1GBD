# IAbrain RAG Pack — ADRASEC

**Version** : 2026.04.26
**Date** : 2026-04-26T11:17:49Z
**Chunks** : 2092 (182 fichiers sources)
**Modèle d'embedding** : nomic-embed-text (768 dim)

## Description

Base RAG Adrasec pour IAbrain

## Installation depuis IAbrain

1. Lancez IAbrain v1.32 ou supérieur
2. Menu **Connaissances → 🔄 Mettre à jour la base depuis GitHub**
3. Cliquez **Vérifier** puis **Mettre à jour**

L'application télécharge `manifest.json`, vérifie les SHA-256, télécharge
les fichiers, vérifie l'intégrité, et installe la base atomiquement.

## Vérification manuelle (optionnelle)

Si vous voulez vérifier l'intégrité d'un fichier sans IAbrain :

```bash
sha256sum rag/vectors.npy   # doit correspondre au manifest.json
sha256sum rag/records.json
sha256sum rag/rag_meta.json
```

## Changelog

Pack initial.

## Compatibilité

Cette base est compatible avec IAbrain v1.32+
configuré pour utiliser le modèle d'embedding **nomic-embed-text**.

Si votre IAbrain utilise un autre modèle, la mise à jour sera bloquée
avec un message d'erreur explicite. Configurez le bon modèle dans
**Options → Paramètres → Modèle d'embedding** avant la mise à jour.

---

Publié par F1GBD / F4JHW — ADRASEC 77
