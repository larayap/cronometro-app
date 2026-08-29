---
type: change-state
change_name: windows-autostart-single-instance
domain: feature
fast_path: spec-first
worktree: /home/larayap/cronometro-app/.sdd/worktrees/windows-autostart-single-instance
feature_branch: feature/windows-autostart-single-instance
integration_target: main
jira_key: "POM-4"
post_init_fields_done: true
subtask_proposal_key: "POM-5"
post_propose_subtask_done: true
subtask_results_key: "POM-15"
post_archive_fields_done: true
status: completed
phases_completed: [sdd-init, sdd-propose, sdd-spec, sdd-tasks, sdd-apply, sdd-verify, sdd-archive]
current_phase: ""
spec_refs: ["[[installer-opt-in-autostart]]", "[[startup-visibility-preference]]", "[[single-instance-focus]]"]
mr: "https://github.com/larayap/work-tracker/pull/6"
mr_status: created
updated: "2026-08-09"
---

# windows-autostart-single-instance

## Intent

Agregar autoarranque con Windows configurable desde el instalador NSIS (casilla que
escribe la entrada `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, sin argumentos),
single-instance lock con `app.requestSingleInstanceLock()` en `src/background.js` (hoy una
segunda instancia cuenta sobre el mismo log de uso), y visibilidad al arrancar gobernada por
una única preferencia persistida `startupVisibility` (`'window'` por default) que aplica tanto
al arranque manual como al automático. Origen: Jira POM-4.

## Path Inference
- Inferred: spec-first (rule 2)
- Signals: S1=Y, S2=Y, S3=N
- Override: none (usuario confirmó la inferencia)
