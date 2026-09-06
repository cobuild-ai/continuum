# 5대 렌즈 종합 코드 품질 및 보안 진단 프레임워크

본 프레임워크는 코드의 안정성, 보안성, 유지보수성, 성능, 그리고 비즈니스 로직의 무결성을 평가하기 위한 5대 핵심 렌즈를 정의합니다.

## 1. 보안성 렌즈 (Security)
- OWASP Top 10 취약점 점검 (SQLi, XSS, CSRF 등)
- 민감 정보 하드코딩 여부 확인
- 의존성 라이브러리 CVE 취약점 스캔

## 2. 코드 품질 렌즈 (Code Quality)
- 정적 분석(Static Analysis)을 통한 코드 스멜(Code Smell) 탐지
- 순환 복잡도(Cyclomatic Complexity) 측정
- 코딩 컨벤션 준수 여부 (PEP8, ESLint 등)

## 3. 성능 렌즈 (Performance)
- 시간 복잡도 및 공간 복잡도 분석
- 비효율적인 루프 및 리소스 누수(Memory Leak) 탐지
- DB 쿼리 최적화 및 N+1 문제 진단

## 4. 유지보수성 렌즈 (Maintainability)
- 모듈 간 결합도(Coupling) 및 응집도(Cohesion) 평가
- 단위 테스트 커버리지(Unit Test Coverage) 측정
- 문서화(Docstring) 및 주석의 적절성

## 5. 비즈니스 로직 렌즈 (Business Logic)
- 예외 처리(Exception Handling)의 견고성
- 비즈니스 규칙의 일관성 및 경계값 테스트
- 로깅 및 모니터링 가시성 확보