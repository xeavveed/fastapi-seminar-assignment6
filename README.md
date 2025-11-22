# 포트폴리오용 프로젝트 안내
이 저장소는 2025년 11월 와플스튜디오 동아리에서 진행한 FastAPI 최종 세미나 과제의 소스 코드와 결과물입니다.

원본 저장소는 동아리 정책상 Private으로 관리되고 있어, 포트폴리오용으로 재구성하여 Public으로 게시합니다.

## CI/CD Pipeline and Infrastructure
이 문서는 GitHub Actions, Docker Hub, AWS EC2를 활용하여 구축한 자동화된 배포 파이프라인(CI/CD)에 대한 기술 상세입니다.

### Architecture Overview
서비스의 지속적인 통합과 배포를 위해 Docker 기반의 컨테이너 환경을 구축하고, GitHub Actions를 통해 배포 프로세스를 자동화했습니다.

- Version Control: GitHub (Main Branch)

- CI/CD: GitHub Actions

- Container Registry: Docker Hub

- Infrastructure: AWS EC2 (Ubuntu), Docker Compose

- Package Manager: uv (Python)

### CI/CD Pipeline Workflow
main 브랜치에 코드가 푸시되면 다음의 자동화된 워크플로우가 순차적으로 실행됩니다.

1. Continuous Integration (CI)
- Build: Dockerfile을 기반으로 최신 소스 코드를 도커 이미지로 빌드합니다.

- Python의 최신 패키지 매니저인 uv를 활용하여 의존성 설치 속도를 최적화했습니다.

- Push: 빌드된 이미지를 Docker Hub 레포지토리(xeavveed/wapang:latest)에 업로드합니다.

2. Continuous Deployment (CD)
- File Transfer: appleboy/scp-action을 사용하여 최신 docker-compose.yaml 설정 파일을 EC2 서버로 전송합니다. 이를 통해 인프라 변경 사항을 자동으로 동기화합니다.

- Remote Execution: appleboy/ssh-action을 사용하여 AWS EC2 인스턴스에 접속 후 배포 스크립트를 실행합니다.

- Deployment Steps:

  1. Pull: Docker Hub에서 최신 이미지를 다운로드합니다.

  2. Update: 기존 컨테이너를 중단 및 삭제하고, 새 이미지로 컨테이너를 재실행합니다.

  3. Clean Up: 디스크 공간 확보를 위해 사용하지 않는 구버전 이미지(dangling images)를 삭제합니다.

### Configuration Details
- Dockerfile Strategy
  - Base Image: python:3.12-slim 이미지를 사용하여 불필요한 패키지를 최소화했습니다.

  - Layer Caching: pyproject.toml과 uv.lock 파일을 소스 코드보다 먼저 복사(COPY)하여, 의존성 변경이 없을 경우 도커의 레이어 캐시를 재사용하도록 최적화했습니다.

- Docker Compose Strategy
  - Image Source: 로컬 빌드 방식(build: .) 대신 Docker Hub의 이미지를 사용하도록 설정하여 빌드와 실행 환경을 분리했습니다.

  - Environment Management: 보안을 위해 .env.prod 파일은 서버에서 직접 관리하며, 코드베이스에 포함하지 않았습니다.

  - Restart Policy: restart: always 옵션을 적용하여 서버 재부팅 시에도 서비스가 자동으로 복구되도록 설정했습니다.

### Troubleshooting and Resolutions
1. SSH 접속 후 설정 파일 부재 문제
- Problem: GitHub Actions에서 배포 스크립트 실행 시 Can't find a suitable configuration file 에러가 발생했습니다. git pull 없이 이미지만 다운로드하는 방식이라 docker-compose.yaml 파일이 서버에 없어서 발생한 문제였습니다.

- Solution: 파이프라인에 scp-action 단계를 추가하여, 배포 직전 최신 docker-compose.yaml 파일을 EC2로 자동 전송하도록 개선하여 해결했습니다.

2. Docker Pull 권한 문제
- Problem: EC2에서 이미지를 다운로드할 때 pull access denied 에러가 발생했습니다. Private 레포지토리에 대한 인증 설정이 복잡하여 발생한 문제였습니다.

- Solution: Docker Hub 레포지토리의 가시성을 Public으로 전환하여 인증 의존성을 제거하고 배포 안정성을 확보했습니다.

### Deployment Information
- Server IP: 3.39.24.161

- API Documentation: http://3.39.24.161:8000/docs
