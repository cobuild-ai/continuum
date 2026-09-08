# 🤝 Contributing to Continuum

Thank you for your interest in contributing to **Continuum**! We welcome contributors to build the future of mobile-first Vibe Coding and host sandbox orchestration.

---

## ✍️ Contributor License Agreement (CLA)
By submitting a Pull Request to Continuum, you agree to our [Contributor License Agreement (CLA)](CLA.md). All contributions are licensed under the **Apache License 2.0** pursuant to Section 5 of the License.

---

## 🚀 Development Workflow
1. **Clone Repository**:
   ```bash
   git clone https://github.com/cobuild-ai/continuum.git
   cd continuum
   ```
2. **FastAPI Vibe Server**:
   ```bash
   uv sync
   uv run vibe_server/main.py
   ```
3. **Run Unit Tests**:
   ```bash
   pytest tests/
   ```
4. **Android Client**:
   Open `mobile/` in Android Studio Ladybug or build via CLI:
   ```bash
   cd mobile && ./gradlew assembleDebug
   ```

---

## 📋 PR Submission Checklist
- [ ] Ensure all pytest unit tests pass (`pytest tests/`).
- [ ] Ensure the 5-Lens Quality Guardrail threshold passes (`check_quality_threshold >= 70.0`).
- [ ] Check the CLA affirmation box in your Pull Request description.
- [ ] Follow Conventional Commits format (`feat:`, `fix:`, `docs:`, `test:`).
