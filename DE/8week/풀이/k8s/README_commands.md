# 과제 09 - EKS 클러스터 생성 및 앱 배포

## 1. EKS 클러스터 생성
```bash
eksctl create cluster \
  --name my-cluster \
  --region ap-northeast-2 \
  --node-type t3.micro \
  --nodes 2 \
  --managed
```

## 2. Nginx 배포
```bash
kubectl apply -f k8s/nginx-deployment.yaml
kubectl get pods
kubectl get svc
```

## 3. 브라우저 접속
- `<노드 공인 IP>:30080`

---

# 과제 10 - HPA 오토스케일링

## 1. Metrics Server 설치
```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

## 2. HPA Deployment + HPA 배포
```bash
kubectl apply -f k8s/nginx-hpa.yaml
```

## 3. 부하 발생 (busybox)
```bash
kubectl apply -f k8s/load-test.yaml
```

## 4. HPA 확인
```bash
kubectl get hpa -w
kubectl get pods -w
```

## 5. 정리
```bash
kubectl delete pod busybox-load-test
eksctl delete cluster --name my-cluster --region ap-northeast-2
```
