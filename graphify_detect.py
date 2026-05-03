import json
from graphify.detect import detect
from pathlib import Path

result = detect(Path('.'))
with open('graphify-out/graphify_detect.json', 'w') as f:
    json.dump(result, f, indent=2)

# Print summary
files = result.get('files', {})
total = result.get('total_files', 0)
words = result.get('total_words', 0)

print(f"Corpus: {total} files · ~{words:,} words")
for ftype, flist in files.items():
    if flist:
        print(f"  {ftype}: {len(flist)} files")
