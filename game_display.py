"""Back up and change only this game's per-user DPI compatibility flag."""
import argparse
import json
import winreg
from pathlib import Path
from deploy_patch import require_closed

ROOT = Path(__file__).resolve().parent
GAME_EXE = str((ROOT/'Game/Game/Inquisitor.exe').resolve())
KEY = r'Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers'
BACKUP = ROOT/'Repack/dpi_settings.original'


def read():
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,KEY) as key:
            value,kind = winreg.QueryValueEx(key,GAME_EXE)
            assert kind == winreg.REG_SZ
            return value
    except FileNotFoundError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action',choices=['status','scale','restore','large-window','restore-window'])
    action = parser.parse_args().action
    if action in ['large-window','restore-window']:
        require_closed()
        config = ROOT/'Game/Game/d3dparams.ini'
        saved = ROOT/'Repack/d3dparams.ini.window-size.original'
        current_bytes = config.read_bytes()
        if not saved.exists():
            assert action == 'large-window'
            assert b'InitialScreenWidth=1024' in current_bytes and b'InitialScreenHeight=768' in current_bytes
            saved.write_bytes(current_bytes)
        before = saved.read_bytes()
        after = before.replace(b'InitialScreenWidth=1024',b'InitialScreenWidth=2048').replace(b'InitialScreenHeight=768',b'InitialScreenHeight=1536')
        assert current_bytes in [before,after], 'Resolution settings changed separately; refusing overwrite'
        config.write_bytes(after if action == 'large-window' else before)
        print('Applied 2048x1536 window' if action == 'large-window' else 'Restored previous window dimensions')
        return
    current = read()
    if action == 'status':
        print(json.dumps(dict(exe=GAME_EXE,current=current,backup_exists=BACKUP.exists()),ensure_ascii=False))
        return
    require_closed()
    if action == 'scale':
        if BACKUP.exists():
            state = json.loads(BACKUP.read_text(encoding='utf-8'))
            assert state['exe'] == GAME_EXE
            assert current in [state['before'],state['after']], 'Settings changed separately; refusing overwrite'
        else:
            tokens = (current or '').split()
            tokens = [t for t in tokens if t.upper() not in {'HIGHDPIAWARE','DPIUNAWARE'}]
            tokens.append('DPIUNAWARE')
            state = dict(exe=GAME_EXE,before=current,after=' '.join(tokens))
            BACKUP.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
        target = state['after']
    else:
        state = json.loads(BACKUP.read_text(encoding='utf-8'))
        assert state['exe'] == GAME_EXE and current in [state['before'],state['after']]
        target = state['before']
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER,KEY) as key:
        if target is None:
            if current is not None: winreg.DeleteValue(key,GAME_EXE)
        else:
            winreg.SetValueEx(key,GAME_EXE,0,winreg.REG_SZ,target)
    assert read() == target
    print(json.dumps(dict(exe=GAME_EXE,before=current,after=target,restart_required=True),ensure_ascii=False))

if __name__ == '__main__': main()
