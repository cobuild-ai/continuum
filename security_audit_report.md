# 코드 품질 및 보안 5대 렌즈 종합 진단 프레임워크

본 진단은 소프트웨어의 견고성과 보안성을 보장하기 위해 다음 5가지 핵심 렌즈를 통해 수행됩니다.

## 1. 정적 분석 (Static Analysis)
- **목표:** 소스 코드 내 잠재적 취약점 및 코드 스멜 탐지
- **도구:** SonarQube, ESLint, Bandit, Checkstyle
- **체크리스트:** 하드코딩된 자격 증명, SQL 인젝션 패턴, 미사용 변수, 복잡도(Cyclomatic Complexity)

## 2. 의존성 보안 (Dependency Security)
- **목표:** 외부 라이브러리의 알려진 취약점(CVE) 관리
- **도구:** Snyk, OWASP Dependency-Check
- **체크리스트:** 취약한 버전의 패키지 사용 여부, 라이선스 컴플라이언스

## 3. 비즈니스 로직 및 아키텍처 (Logic & Architecture)
- **목표:** 설계 결함 및 비즈니스 로직 우회 방지
- **방법:** Threat Modeling (STRIDE), 코드 리뷰
- **체크리스트:** 권한 부여(Authorization) 누락, 입력값 검증 로직, 데이터 무결성

## 4. 런타임 및 인프라 보안 (Runtime & Infrastructure)
- **목표:** 실행 환경에서의 보안 설정 및 리소스 보호
- **도구:** Docker Bench, Cloud Custodian
- **체크리스트:** 최소 권한 원칙(Least Privilege), 민감 정보 환경 변수 관리, 네트워크 격리

## 5. 코드 가독성 및 유지보수성 (Maintainability)
- **목표:** 기술 부채 최소화 및 협업 효율성 증대
- **방법:** Clean Code 원칙, 자동화된 테스트 커버리지
- **체크리스트:** 함수 단위의 단일 책임 원칙(SRP), 테스트 코드 커버리지 80% 이상 유지
