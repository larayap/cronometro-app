---
type: change-state
change_name: "pomodoro-wall-clock-timer"
domain: "fix"
status: completed
fast_path: "apply-only"
current_phase: ""
phases_completed: [sdd-init, sdd-apply, sdd-verify, sdd-archive]
spec_refs: []
worktree: "/home/larayap/cronometro-app/.sdd/worktrees/pomodoro-wall-clock-timer"
feature_branch: "feature/pomodoro-wall-clock-timer"
integration_target: "main"
mr_url: ""
mr_status: pending
mr_error: ""
require_judgment: false
skip_judgment: false
created: "2026-09-01"
updated: "2026-09-02"
tags: [change]
---

## Intent

Corregir el temporizador del pomodoro en `src/components/CronometroPomodoro.vue` porque cuenta ticks de `setInterval` en vez de tiempo real y se ralentiza cuando Chromium aplica intensive wake-up throttling a la ventana oculta u ocluida (Electron 13 / Chromium 91). Reporte de usuario: un bloque de 15 min tardó ~30 min reales. Corrección: (1) medir el restante desde el reloj del sistema (guardar el instante de fin del bloque y recalcular en cada tick con `Date.now()`, mismo enfoque que `CronometroManual.vue`), manteniendo el comportamiento de pausa/reset/cancel/edición/nextSession; (2) fijar `backgroundThrottling: false` en `webPreferences` de `mainWindow` en `src/background.js` para que el sonido de fin de bloque no llegue tarde. Restricción: el bundle del main process tiene techo ES2016 (sin `??` ni `?.` en archivos alcanzables desde `src/background.js`).

## Path Inference
- Inferred: apply-only (rule 1)
- Signals: S1=Y (gap keywords: corregir), S2=Y (path: src/components/CronometroPomodoro.vue), S3=Y (2 archivos, acción clara, sin decisión de diseño pendiente)
- Override: none
