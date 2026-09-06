import os

def run_comprehensive_audit(project_path):
    """
    5대 렌즈 진단을 자동화하기 위한 스켈레톤 코드
    """
    print(f"Starting audit for: {project_path}")
    
    # 1. Static Analysis
    os.system(f"bandit -r {project_path} -f json -o security_results.json")
    
    # 2. Dependency Check
    os.system(f"safety check -r {project_path}/requirements.txt")
    
    # 3. Maintainability Check
    os.system(f"radon cc {project_path} -s")
    
    print("Audit complete. Check generated reports.")

if __name__ == "__main__":
    run_comprehensive_audit("./src")
