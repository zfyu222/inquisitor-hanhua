"""Inquisitor compatibility entry point; shared safety logic lives in Tools/localization."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'Tools' / 'localization'))
from glossary_tool import apply_analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    snapshot = ROOT / 'glossary_original.json'
    original = json.loads(snapshot.read_text(encoding='utf-8'))
    reviewed = json.loads((ROOT / 'glossary_reviewed.json').read_text(encoding='utf-8'))
    if hashlib.sha256(snapshot.read_bytes()).hexdigest() != reviewed['review_metadata']['original_sha256']:
        parser.exit(1, 'Original glossary snapshot does not match this review.\n')
    try:
        result = apply_analysis(ROOT / 'AiNieeCache' / 'AinieeCacheData.json', original, reviewed, args.apply)
        print(result)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
