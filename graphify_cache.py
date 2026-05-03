import json
from pathlib import Path

try:
    from graphify.cache import check_semantic_cache
    
    detect = json.loads(Path('graphify-out/graphify_detect.json').read_text())
    all_files = [f for files in detect['files'].values() for f in files]
    
    cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)
    
    if cached_nodes or cached_edges or cached_hyperedges:
        Path('graphify-out/graphify_cached.json').write_text(json.dumps({'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}))
    Path('graphify-out/graphify_uncached.txt').write_text('\n'.join(uncached))
    print(f'Cache: {len(all_files)-len(uncached)} files hit, {len(uncached)} files need extraction')
except Exception as e:
    print(f"Cache check failed (first run?): {e}")
    print("Proceeding with all files as uncached...")
    detect = json.loads(Path('graphify-out/graphify_detect.json').read_text())
    docs = detect.get('files', {}).get('document', [])
    Path('graphify-out/graphify_uncached.txt').write_text('\n'.join(docs))
    Path('graphify-out/graphify_cached.json').write_text(json.dumps({'nodes': [], 'edges': [], 'hyperedges': []}))
    print(f'{len(docs)} document files need extraction')
