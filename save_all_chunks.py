import json
from pathlib import Path

# Chunk 1 data
chunk1_data = {
  "nodes": [
    {"id": "app_main", "label": "Flask Application Entry", "file_type": "code", "source_file": "app.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_init", "label": "create_app()", "file_type": "code", "source_file": "tracker/__init__.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_storage", "label": "Storage Layer", "file_type": "code", "source_file": "tracker/storage.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_domain", "label": "Domain Models & Constants", "file_type": "code", "source_file": "tracker/domain.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_services", "label": "Project & Task Services", "file_type": "code", "source_file": "tracker/services.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_catalog", "label": "Catalog Management", "file_type": "code", "source_file": "tracker/catalog.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_drive", "label": "Drive Configuration & Scanning", "file_type": "code", "source_file": "tracker/drive.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_validators", "label": "Form Validators", "file_type": "code", "source_file": "tracker/validators.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_csv_import", "label": "CSV Import Parser", "file_type": "code", "source_file": "tracker/csv_import.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_pdfs", "label": "PDF Generation", "file_type": "code", "source_file": "tracker/pdfs.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_project_view", "label": "Project Detail Context Builder", "file_type": "code", "source_file": "tracker/project_view.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_catalog_search", "label": "Catalog Search & Filtering", "file_type": "code", "source_file": "tracker/catalog_search.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_consistency", "label": "COT vs LDM Consistency", "file_type": "code", "source_file": "tracker/consistency.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_bundles", "label": "Product Bundles", "file_type": "code", "source_file": "tracker/bundles.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_comparison_rules", "label": "COT-LDM Conversion Rules", "file_type": "code", "source_file": "tracker/comparison_rules.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_comparison_ignored", "label": "Ignored Items in Comparison", "file_type": "code", "source_file": "tracker/comparison_ignored.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_deletions", "label": "Cascading Deletions", "file_type": "code", "source_file": "tracker/deletions.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_form_models", "label": "Form Data Models", "file_type": "code", "source_file": "tracker/form_models.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_routes_admin", "label": "Admin Routes", "file_type": "code", "source_file": "tracker/routes/admin.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "tracker_routes_materials", "label": "Material/LDM Routes", "file_type": "code", "source_file": "tracker/routes/materials.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None},
    {"id": "graphify_detect", "label": "Code Detection Tool", "file_type": "code", "source_file": "graphify_detect.py", "source_location": None, "source_url": None, "captured_at": None, "author": None, "contributor": None}
  ],
  "edges": [],
  "hyperedges": [],
  "input_tokens": 0,
  "output_tokens": 0
}

# Save chunk 1
Path('graphify-out/graphify_chunk_01.json').write_text(json.dumps(chunk1_data, indent=2))
print("Saved chunk 1")
