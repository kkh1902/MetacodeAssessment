"""학생 ipynb를 셀 단위로 실행하고 Q별 성공/실패를 기록.
Q4는 건너뜀 (Kaggle/Colab에서 별도 채점)
"""
import os, sys, json, re, traceback, time, gc
os.environ['HF_TOKEN'] = 'YOUR_HF_TOKEN_HERE'
os.environ['HUGGING_FACE_HUB_TOKEN'] = os.environ['HF_TOKEN']
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

import warnings
warnings.filterwarnings('ignore')

import torch
print(f"[INFO] CUDA: {torch.cuda.is_available()}, device: {torch.cuda.get_device_name(0)}")

STUDENT = sys.argv[1]
NB_PATH = f"/home/pc/dev/metacode/MetacodeAssessment/AILLM/14week/수강생/14주차_{STUDENT}.ipynb"
LOG = f"/home/pc/dev/metacode/MetacodeAssessment/AILLM/14week/실행로그/{STUDENT}.log"

def log(msg):
    print(msg, flush=True)
    with open(LOG, 'a') as f:
        f.write(msg + '\n')

# Reset log
open(LOG, 'w').close()
log(f"=== 실행 채점: {STUDENT} ===")
log(f"시작: {time.strftime('%Y-%m-%d %H:%M:%S')}")

with open(NB_PATH) as f:
    nb = json.load(f)

# 셀 분류
cells_to_run = []
current_q = None
for i, cell in enumerate(nb['cells']):
    src = ''.join(cell.get('source', []))
    m = re.search(r'문제\s*(\d+(?:-\d+)?)', src)
    if m:
        current_q = m.group(1)
    if cell['cell_type'] != 'code':
        continue
    # skip pip install
    if src.strip().startswith(('!pip', '! pip', '%pip', '! %pip')):
        continue
    if 'pip install' in src and src.strip().startswith('!'):
        continue
    if 'pip uninstall' in src:
        src = '\n'.join(line for line in src.split('\n') if 'pip uninstall' not in line)
    # skip notebook_login (interactive)
    if 'notebook_login' in src:
        continue
    # skip Q4 cells
    if current_q and current_q.startswith('4'):
        log(f"  cell {i}: Q{current_q} SKIP (Kaggle 별도)")
        continue
    cells_to_run.append((i, current_q, src))

log(f"\n실행 셀 수: {len(cells_to_run)}")

# Add token-based login at the start
login_code = """
import os
os.environ['HF_TOKEN'] = 'YOUR_HF_TOKEN_HERE'
os.environ['HUGGING_FACE_HUB_TOKEN'] = os.environ['HF_TOKEN']
from huggingface_hub import login
login(token=os.environ['HF_TOKEN'])
"""

# 실행 namespace
ns = {'__name__': '__main__'}
exec(login_code, ns)

# Q별 결과 추적
q_results = {}  # current_q -> 'O' / 'X (사유)'
q_outputs = {}  # current_q -> last stdout

import io, contextlib

for i, current_q, src in cells_to_run:
    label = f"Q{current_q}" if current_q else f"setup"
    t0 = time.time()

    # Capture stdout
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

    log(f"\n--- cell {i} [{label}] ({elapsed:.1f}s) {'OK' if success else 'FAIL'} ---")
    if out_text.strip():
        log(f"OUT: {out_text.strip()[:500]}")
    if err:
        log(f"ERR: {err}")

    if current_q:
        # update result for Q (pessimistic - fail if any sub-cell fails)
        if current_q not in q_results:
            q_results[current_q] = 'O' if success else f"X: {err[:100]}"
        elif not success and q_results[current_q] == 'O':
            q_results[current_q] = f"X: {err[:100]}"
        # capture output
        if out_text.strip() and current_q not in q_outputs:
            q_outputs[current_q] = out_text.strip()[:800]
        elif out_text.strip():
            q_outputs[current_q] += '\n---\n' + out_text.strip()[:400]

log("\n" + "="*60)
log("Q별 결과 (Q4 제외):")
# group sub-Qs to main Qs
main_results = {}
for sub_q, res in q_results.items():
    main_q = sub_q.split('-')[0]
    if main_q not in main_results:
        main_results[main_q] = []
    main_results[main_q].append((sub_q, res))

for mq in ['1','2','3','5','6','7','8','9','10']:
    if mq in main_results:
        any_fail = any(not r.startswith('O') for _, r in main_results[mq])
        verdict = 'X' if any_fail else 'O'
        details = [f"{sq}={r.split(':')[0]}" for sq, r in main_results[mq]]
        log(f"  Q{mq}: {verdict} ({', '.join(details)})")
    else:
        log(f"  Q{mq}: ?? (not found)")

log(f"\n끝: {time.strftime('%Y-%m-%d %H:%M:%S')}")

# cleanup
del ns
gc.collect()
torch.cuda.empty_cache()
