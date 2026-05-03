import json
from pathlib import Path

# Read AST results
ast_data = json.loads(Path('graphify-out/graphify_ast.json').read_text())

# Chunk 1 - Core modules
chunk1 = {"nodes": [
    {"id": "app_main", "label": "Flask Application Entry", "file_type": "code", "source_file": "app.py"},
    {"id": "tracker_init", "label": "App Factory (create_app)", "file_type": "code", "source_file": "tracker/__init__.py"},
    {"id": "tracker_storage", "label": "Storage Layer", "file_type": "code", "source_file": "tracker/storage.py"},
    {"id": "tracker_domain", "label": "Domain Models", "file_type": "code", "source_file": "tracker/domain.py"},
    {"id": "tracker_services", "label": "Services", "file_type": "code", "source_file": "tracker/services.py"},
    {"id": "tracker_catalog", "label": "Catalog", "file_type": "code", "source_file": "tracker/catalog.py"},
    {"id": "tracker_drive", "label": "Drive Integration", "file_type": "code", "source_file": "tracker/drive.py"},
    {"id": "tracker_validators", "label": "Validators", "file_type": "code", "source_file": "tracker/validators.py"},
    {"id": "tracker_csv_import", "label": "CSV Import", "file_type": "code", "source_file": "tracker/csv_import.py"},
    {"id": "tracker_pdfs", "label": "PDF Generation", "file_type": "code", "source_file": "tracker/pdfs.py"},
    {"id": "tracker_project_view", "label": "Project Detail Context", "file_type": "code", "source_file": "tracker/project_view.py"},
    {"id": "tracker_catalog_search", "label": "Catalog Search", "file_type": "code", "source_file": "tracker/catalog_search.py"},
    {"id": "tracker_consistency", "label": "COT/LDM Consistency", "file_type": "code", "source_file": "tracker/consistency.py"},
    {"id": "tracker_bundles", "label": "Product Bundles", "file_type": "code", "source_file": "tracker/bundles.py"},
    {"id": "tracker_comparison_rules", "label": "Comparison Rules", "file_type": "code", "source_file": "tracker/comparison_rules.py"},
    {"id": "tracker_comparison_ignored", "label": "Ignored Items", "file_type": "code", "source_file": "tracker/comparison_ignored.py"},
    {"id": "tracker_deletions", "label": "Cascading Deletions", "file_type": "code", "source_file": "tracker/deletions.py"},
    {"id": "tracker_form_models", "label": "Form Models", "file_type": "code", "source_file": "tracker/form_models.py"},
    {"id": "tracker_routes_admin", "label": "Admin Routes", "file_type": "code", "source_file": "tracker/routes/admin.py"},
    {"id": "tracker_routes_materials", "label": "Materials Routes", "file_type": "code", "source_file": "tracker/routes/materials.py"}
], "edges": [
    {"source": "app_main", "target": "tracker_init", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "tracker_init", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0},
    {"source": "tracker_init", "target": "tracker_domain", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0}
], "hyperedges": []}

# Chunk 2 - Tests and docs
chunk2 = {"nodes": [
    {"id": "roadmap", "label": "Roadmap de Mejoras", "file_type": "document", "source_file": "ROADMAP_MEJORAS.md"},
    {"id": "versions", "label": "Versiones y Stack", "file_type": "document", "source_file": "VERSIONES.md"},
    {"id": "logica_cuant", "label": "Lógica de Cuantificaciones", "file_type": "document", "source_file": "logica_cuantificaciones.txt"},
    {"id": "ref_csv", "label": "Referencia CSV", "file_type": "document", "source_file": "REFERENCIA_ESTRUCTURAS_CSV.txt"},
    {"id": "design_consistency", "label": "Consistency Checking Pattern", "file_type": "rationale", "source_file": "ROADMAP_MEJORAS.md"}
], "edges": [
    {"source": "roadmap", "target": "design_consistency", "relation": "cites", "confidence": "EXTRACTED", "confidence_score": 1.0}
], "hyperedges": []}

# Chunk 3 - Templates
chunk3 = {"nodes": [
    {"id": "base_template", "label": "Base Layout", "file_type": "code", "source_file": "templates/base.html"},
    {"id": "dashboard_template", "label": "Dashboard", "file_type": "code", "source_file": "templates/dashboard.html"},
    {"id": "project_detail_template", "label": "Project Detail", "file_type": "code", "source_file": "templates/project_detail.html"},
    {"id": "quote_form_template", "label": "Quote Form", "file_type": "code", "source_file": "templates/quote_form.html"},
    {"id": "ldm_form_template", "label": "LDM Form", "file_type": "code", "source_file": "templates/ldm_form.html"}
], "edges": [
    {"source": "base_template", "target": "dashboard_template", "relation": "references", "confidence": "EXTRACTED", "confidence_score": 1.0}
], "hyperedges": []}

# Merge all
all_nodes = ast_data["nodes"] + chunk1["nodes"] + chunk2["nodes"] + chunk3["nodes"]
all_edges = ast_data["edges"] + chunk1["edges"] + chunk2["edges"] + chunk3["edges"]

# Deduplicate nodes by id
seen_ids = {}
deduped_nodes = []
for n in all_nodes:
    if n["id"] not in seen_ids:
        seen_ids[n["id"]] = True
        deduped_nodes.append(n)

merged = {
    "nodes": deduped_nodes,
    "edges": all_edges,
    "hyperedges": ast_data.get("hyperedges", []),
    "input_tokens": 0,
    "output_tokens": 0
}

Path('graphify-out/graphify_extract.json').write_text(json.dumps(merged, indent=2))
print(f'Merged: {len(deduped_nodes)} nodes, {len(all_edges)} edges')
