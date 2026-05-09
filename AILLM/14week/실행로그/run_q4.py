"""Q4만 채점: setup + Q1 + Q2 + Q4 실행"""
import os, sys, json, re, time, gc, io, contextlib
os.environ['HF_TOKEN'] = 'YOUR_HF_TOKEN_HERE'
os.environ['HUGGING_FACE_HUB_TOKEN'] = os.environ['HF_TOKEN']
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import warnings
warnings.filterwarnings('ignore')
import torch
print(f"[INFO] CUDA: {torch.cuda.is_available()}, VRAM free: {torch.cuda.mem_get_info()[0]//1024**2}MB")

STUDENT = sys.argv[1]
NB_PATH = f"/home/pc/dev/metacode/MetacodeAssessment/AILLM/14week/수강생/14주차_{STUDENT}.ipynb"
LOG = f"/home/pc/dev/metacode/MetacodeAssessment/AILLM/14week/실행로그/{STUDENT}_q4.log"

def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')

open(LOG, 'w').close()
log(f"=== Q4 채점: {STUDENT} ===")
log(f"시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")

with open(NB_PATH) as f:
    nb = json.load(f)

# 실행할 셀 분류: setup + Q1 + Q2 + Q4
cells_to_run = []
current_q = None
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    m = re.search(r'문제\s*(\d+(?:-\d+)?)', src)
    if m:
        current_q = m.group(1)
    if cell['cell_type'] != 'code':
        continue
    if src.strip().startswith(('!pip', '! pip', '%pip')):
        continue
    if 'pip install' in src and src.strip().startswith('!'):
        continue
    if 'pip uninstall' in src:
        continue
    if 'notebook_login' in src:
        continue
    # setup, Q1, Q2, Q4만 실행
    if current_q is None:
        cells_to_run.append((i, 'setup', src))
    elif current_q.startswith('1') or current_q.startswith('2') or current_q.startswith('4'):
        cells_to_run.append((i, current_q, src))

log(f"실행 셀 수: {len(cells_to_run)}")

login_code = """
import os
from huggingface_hub import login
login(token=os.environ['HF_TOKEN'])
"""
ns = {'__name__': '__main__'}
exec(login_code, ns)

q4_results = {}

for i, q, src in cells_to_run:
    label = f"Q{q}" if q != 'setup' else 'setup'
    t0 = time.time()
    out_buf = io.StringIO()
    err = None
    try:
        with contextlib.redirect_stdout(out_buf), contextlib.redirect_stderr(out_buf):
            exec(src, ns)
        success = True
    except Exception as e:
        err = f"{type(e).__name__}: {str(e)[:300]}"
        success = False

    out_text = out_buf.getvalue()
    elapsed = time.time() - t0
    vram_free = torch.cuda.mem_get_info()[0]//1024**2

    log(f"\n--- cell {i} [{label}] ({elapsed:.1f}s) {'OK' if success else 'FAIL'} | VRAM free: {vram_free}MB ---")
    if out_text.strip():
        log(f"OUT: {out_text.strip()[:800]}")
    if err:
        log(f"ERR: {err}")

    if q.startswith('4'):
        if q not in q4_results:
            q4_results[q] = 'O' if success else f"X: {err[:100] if err else ''}"
        elif not success and q4_results[q] == 'O':
            q4_results[q] = f"X: {err[:100] if err else ''}"

log("\n" + "="*50)
log("Q4 결과:")
any_fail = False
for sub_q in ['4', '4-2', '4-3']:
    if sub_q in q4_results:
        log(f"  Q{sub_q}: {q4_results[sub_q]}")
        if not q4_results[sub_q].startswith('O'):
            any_fail = True
log(f"\nQ4 최종: {'X' if any_fail else 'O'}")
log(f"끝: {time.strftime('%Y-%m-%d %H:%M:%S')}")

del ns
gc.collect()
torch.cuda.empty_cache()
