#!/usr/bin/env bash
# Q10 — busybox 부하 발생 스크립트
#
# 사용법:  bash load-test.sh
#
# 다른 터미널에서 watch:
#   kubectl get hpa -n realestate-kihoon -w
#   kubectl get pods -n realestate-kihoon -w
#
# 정리:  Ctrl+C 로 중단 (Pod 자동 삭제 — --rm 옵션)
set -euo pipefail

NS="realestate-kihoon"
SVC="realestate-svc.${NS}.svc.cluster.local"

echo "🔥 부하 발생 시작 — 대상: http://${SVC}"
echo "   (HPA scale-out 확인을 위해 다른 터미널에서 'kubectl get hpa -n ${NS} -w' 실행)"
echo ""

kubectl run load-gen \
  --image=busybox:1.36 \
  --restart=Never \
  --rm -i --tty \
  --namespace="${NS}" \
  --labels="student=kihoon,role=load-gen" \
  -- /bin/sh -c "
    echo '부하 시작 — Ctrl+C 로 중단';
    while sleep 0.005; do
      wget -q -O- http://${SVC} > /dev/null;
    done
  "
