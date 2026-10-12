"""Read-only IDA RPC capture and PE string lookup for this localization project."""
import argparse
import http.client
import json
from pathlib import Path
import pefile

ROOT = Path(__file__).resolve().parent
EXE = ROOT / 'Game/Game/Inquisitor.exe'

def rpc(method, *params):
    connection = http.client.HTTPConnection('127.0.0.1', 13337, timeout=15)
    try:
        connection.request('POST', '/mcp', json.dumps(dict(jsonrpc='2.0', id=1, method=method, params=list(params))), {'Content-Type': 'application/json'})
        response = json.loads(connection.getresponse().read())
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response['result']
    finally:
        connection.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['asm', 'strings'])
    parser.add_argument('values', nargs='+')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    if args.mode == 'asm':
        output = ROOT / 'Repack/analysis'
        output.mkdir(parents=True, exist_ok=True)
        for address in args.values:
            result = rpc('disassemble_function', address)
            path = output / f'{address}.json'
            path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
            print(result['name'], len(result['lines']), path)
            if not args.quiet:
                for line in result['lines']:
                    print(line['address'], line['instruction'])
    else:
        pe = pefile.PE(str(EXE))
        data = EXE.read_bytes()
        for value in args.values:
            for encoding in ['ascii', 'utf-16-le']:
                needle = value.encode(encoding)
                start = 0
                while (start := data.find(needle, start)) >= 0:
                    address = pe.OPTIONAL_HEADER.ImageBase + pe.get_rva_from_offset(start)
                    print(value, encoding, hex(address))
                    start += len(needle)

if __name__ == '__main__':
    main()
