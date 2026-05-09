#!/bin/bash
# Q10 — busybox Pod 에서 wget 무한 루프로 부하 발생
# 사용법:
#   bash Q10/load-test.sh
# 추가 부하가 필요하면 여러 개 동시에 실행:
#   bash Q10/load-test.sh & bash Q10/load-test.sh

NAMESPACE="realestate-홍길동"
SERVICE_HOST="realestate-svc.${NAMESPACE}.svc.cluster.local"
LOAD_POD="load-gen-$(date +%s)"

kubectl run "$LOAD_POD" \
  --image=busybox \
  --rm -it --restart=Never \
  --namespace="$NAMESPACE" \
  -- /bin/sh -c "while sleep 0.01; do wget -qO- http://${SERVICE_HOST}; done"
