import json
import re

# Read chunk 1
chunk1_text = """```json
{
  "nodes": [
    {"id": "app_main", "label": "Flask Application Entry", "file_type": "code", "source_file": "app.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_init", "label": "create_app()", "file_type": "code", "source_file": "tracker/__init__.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_storage", "label": "Storage Layer", "file_type": "code", "source_file": "tracker/storage.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_domain", "label": "Domain Models & Constants", "file_type": "code", "source_file": "tracker/domain.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_services", "label": "Project & Task Services", "file_type": "code", "source_file": "tracker/services.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_catalog", "label": "Catalog Management", "file_type": "code", "source_file": "tracker/catalog.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_drive", "label": "Drive Configuration & Scanning", "file_type": "code", "source_file": "tracker/drive.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_validators", "label": "Form Validators", "file_type": "code", "source_file": "tracker/validators.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_csv_import", "label": "CSV Import Parser", "file_type": "code", "source_file": "tracker/csv_import.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_pdfs", "label": "PDF Generation", "file_type": "code", "source_file": "tracker/pdfs.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_project_view", "label": "Project Detail Context Builder", "file_type": "code", "source_file": "tracker/project_view.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_catalog_search", "label": "Catalog Search & Filtering", "file_type": "code", "source_file": "tracker/catalog_search.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_consistency", "label": "COT vs LDM Consistency", "file_type": "code", "source_file": "tracker/consistency.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_bundles", "label": "Product Bundles", "file_type": "code", "source_file": "tracker/bundles.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_comparison_rules", "label": "COT-LDM Conversion Rules", "file_type": "code", "source_file": "tracker/comparison_rules.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_comparison_ignored", "label": "Ignored Items in Comparison", "file_type": "code", "source_file": "tracker/comparison_ignored.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_deletions", "label": "Cascading Deletions", "file_type": "code", "source_file": "tracker/deletions.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_form_models", "label": "Form Data Models", "file_type": "code", "source_file": "tracker/form_models.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_routes_admin", "label": "Admin Routes", "file_type": "code", "source_file": "tracker/routes/admin.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "tracker_routes_materials", "label": "Material/LDM Routes", "file_type": "code", "source_file": "tracker/routes/materials.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null},
    {"id": "graphify_detect", "label": "Code Detection Tool", "file_type": "code", "source_file": "graphify_detect.py", "source_location": null, "source_url": null, "captured_at": null, "author": null, "contributor": null}
  ],
  "edges": [
    {"source": "app_main", "target": "tracker_init", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "app.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_init", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/__init__.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_init", "target": "tracker_domain", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/__init__.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_init", "target": "tracker_drive", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/__init__.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_init", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/__init__.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_domain", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/domain.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_services", "target": "tracker_domain", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/services.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_services", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/services.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_catalog", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/catalog.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_drive", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/drive.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_validators", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/validators.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_csv_import", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/csv_import.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_pdfs", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/pdfs.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_pdfs", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/pdfs.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_consistency", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_domain", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_drive", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_consistency", "target": "tracker_bundles", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/consistency.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_consistency", "target": "tracker_comparison_rules", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/consistency.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_consistency", "target": "tracker_comparison_ignored", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/consistency.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_deletions", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/deletions.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_form_models", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/form_models.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_form_models", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/form_models.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_bundles", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_catalog_search", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_comparison_ignored", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_comparison_rules", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_deletions", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_domain", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_catalog", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_csv_import", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_deletions", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_drive", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_form_models", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_pdfs", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_storage", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_materials", "target": "tracker_validators", "relation": "calls", "confidence": "EXTRACTED", "confidence_score": 1.0, "source_file": "tracker/routes/materials.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_storage", "target": "tracker_consistency", "relation": "shares_data_with", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "tracker/storage.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_catalog_search", "target": "tracker_consistency", "relation": "semantically_similar_to", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tracker/catalog_search.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_form_models", "target": "tracker_services", "relation": "shares_data_with", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "tracker/form_models.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_validators", "target": "tracker_services", "relation": "shares_data_with", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "tracker/validators.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_csv_import", "target": "tracker_form_models", "relation": "semantically_similar_to", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tracker/csv_import.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_project_view", "target": "tracker_form_models", "relation": "calls", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tracker/project_view.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_consistency", "target": "tracker_catalog", "relation": "shares_data_with", "confidence": "INFERRED", "confidence_score": 0.95, "source_file": "tracker/consistency.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_comparison_ignored", "target": "tracker_comparison_rules", "relation": "conceptually_related_to", "confidence": "INFERRED", "confidence_score": 0.75, "source_file": "tracker/comparison_ignored.py", "source_location": null, "weight": 1.0},
    {"source": "tracker_routes_admin", "target": "tracker_project_view", "relation": "calls", "confidence": "INFERRED", "confidence_score": 0.85, "source_file": "tracker/routes/admin.py", "source_location": null, "weight": 1.0}
  ],
  "hyperedges": [],
  "input_tokens": 0,
  "output_tokens": 0
}
```"""

# Extract JSON from chunk 1
chunk1_match = re.search(r'```json\n(.*?)\n```', chunk1_text, re.DOTALL)
if chunk1_match:
    chunk1_data = json.loads(chunk1_match.group(1))
    with open('graphify-out/graphify_chunk_01.json', 'w') as f:
        json.dump(chunk1_data, f, indent=2)
    print("Saved chunk 1")
else:
    print("Could not extract chunk 1 JSON")
