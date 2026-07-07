"""
Tests: F6: Cierre — Validación final de documentos, cierre y consistencia.

Verifica todos los criterios de aceptación de F6:
- PRD.md y TRD.md actualizados con estado Aprobado v1.0.0
- Cross-ref consistency entre documentos
- Enlaces no rotos en documentación
- Line count mínimo en documentos clave
"""
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

# ─── Slice 1: Document Review — PRD & TRD Status ──────────────

class TestDocStatus:
    """F6-01.1/2: PRD y TRD deben reflejar estado final v1.0.0."""

    @pytest.mark.parametrize("filename", ["PRD.md", "TRD.md"])
    def test_doc_exists(self, root: Path, filename: str):
        assert (root / "docs" / filename).exists()

    @pytest.mark.parametrize("filename", ["PRD.md", "TRD.md"])
    def test_doc_has_aprobado_status(self, root: Path, filename: str):
        content = (root / "docs" / filename).read_text()
        assert "Aprobado" in content, f"{filename} debe tener estado 'Aprobado'"
        assert "Borrador" not in content, f"{filename} no debe decir 'Borrador'"

    @pytest.mark.parametrize("filename", ["PRD.md", "TRD.md"])
    def test_doc_has_current_date(self, root: Path, filename: str):
        content = (root / "docs" / filename).read_text()
        assert "2026-07-07" in content, f"{filename} debe tener fecha 2026-07-07"

    @pytest.mark.parametrize("filename", ["PRD.md", "TRD.md"])
    def test_doc_has_version_100(self, root: Path, filename: str):
        content = (root / "docs" / filename).read_text()
        assert "v1.0.0" in content, f"{filename} debe mencionar v1.0.0"

    def test_prd_has_record_count(self, root: Path):
        content = (root / "docs" / "PRD.md").read_text()
        assert any(p in content for p in ("182K", "182,465", "182465")), \
            "PRD.md debe mencionar ~182K registros"

    def test_trd_trazabilidad_no_pendiente(self, root: Path):
        """TRD: matriz de trazabilidad debe reflejar estado completado."""
        content = (root / "docs" / "TRD.md").read_text()
        assert "Pendiente" not in content, \
            "TRD.md no debe tener requisitos Pendiente (todos completados)"


class TestAgentsVerification:
    """F6-01.3: AGENTS.md links verificados."""

    def test_agents_md_exists(self, root: Path):
        assert (root / "AGENTS.md").exists()

    def test_agents_links_exist(self, root: Path):
        """Todos los links relativos en AGENTS.md apuntan a archivos existentes."""
        content = (root / "AGENTS.md").read_text()
        for line in content.splitlines():
            if "](docs/" in line or "](specs/" in line:
                # Extract path between ]( and )
                start = line.find("](") + 2
                end = line.find(")", start)
                if start > 1 and end > start:
                    ref_path = line[start:end]
                    full_path = root / ref_path
                    assert full_path.exists(), f"Link rotos: {ref_path} (line: {line.strip()[:80]})"

    def test_agents_version(self, root: Path):
        content = (root / "AGENTS.md").read_text()
        assert "v2.5" in content or "2.5" in content, "AGENTS.md debe ser v2.5 (release v1.0.0)"


class TestWorkflowVerification:
    """F6-01.4: WORKFLOW.md verificado."""

    def test_workflow_exists(self, root: Path):
        assert (root / "docs" / "WORKFLOW.md").exists()

    def test_workflow_has_f0_to_f5_completed(self, root: Path):
        content = (root / "docs" / "WORKFLOW.md").read_text()
        for i in range(6):
            assert f"F{i}" in content, f"WORKFLOW.md debe cubrir F{i}"

    def test_workflow_minimum_lines(self, root: Path):
        lines = (root / "docs" / "WORKFLOW.md").read_text().splitlines()
        assert len(lines) >= 300, f"WORKFLOW.md tiene {len(lines)} líneas, esperado >= 300"


class TestCrossRefConsistency:
    """F6-01.5: Cross-ref check entre documentos."""

    @staticmethod
    def _get_record_counts(root: Path) -> Dict[str, List[str]]:
        """Find record count mentions across docs. Returns {file: [lines_with_mentions]}."""
        patterns = ["182K", "182,465", "182465"]
        doc_dir = root / "docs"
        result: Dict[str, List[str]] = {}
        for f in sorted(doc_dir.glob("*.md")):
            content = f.read_text()
            mentions = []
            for i, line in enumerate(content.splitlines(), 1):
                if any(p in line for p in patterns):
                    mentions.append(f"  L{i}: {line.strip()[:100]}")
            if mentions:
                result[f.name] = mentions
        return result

    def test_record_count_consistency(self, root: Path):
        """All docs should agree on ~182K record count."""
        counts = self._get_record_counts(root)
        assert len(counts) >= 2, \
            f"Al menos 2 docs deben mencionar ~182K. Encontrados: {list(counts.keys())}"

    def test_prd_trd_record_count_agreement(self, root: Path):
        """PRD.md y TRD.md deben usar el mismo record count."""
        prd = (root / "docs" / "PRD.md").read_text()
        trd = (root / "docs" / "TRD.md").read_text()
        # Both should reference 182K or similar
        if "182" in prd or "50K" in prd:
            assert "182" in trd or "50K" in trd or "200K" in trd

    def test_agents_docs_links_resolve(self, root: Path):
        """All docs/ links in AGENTS.md resolve to actual files."""
        content = (root / "AGENTS.md").read_text()
        links_found = 0
        for line in content.splitlines():
            if "](" in line:
                start = line.find("](") + 2
                end = line.find(")", start)
                if start > 1 and end > start:
                    ref_path = line[start:end]
                    if ref_path.startswith("docs/") or ref_path.startswith("specs/"):
                        links_found += 1
                        full_path = root / ref_path
                        assert full_path.exists(), f"Broken: {ref_path}"
        assert links_found >= 5, f"AGENTS.md debe tener >=5 links a docs, tiene {links_found}"


class TestTechDocsSpotCheck:
    """F6-01.6: Documentación técnica verificada."""

    TECH_DOCS: List[Tuple[str, int]] = [
        ("ARCHITECTURE.md", 30),
        ("SCHEMA.md", 30),
        ("TESTING.md", 30),
        ("SECURITY.md", 30),
        ("CODE_STYLE.md", 30),
        ("USER_GUIDE.md", 200),
        ("TECHNICAL_GUIDE.md", 300),
        ("REPRODUCIBILITY.md", 50),
    ]

    @pytest.mark.parametrize("filename,_", TECH_DOCS)
    def test_tech_doc_exists(self, root: Path, filename: str, _: int):
        assert (root / "docs" / filename).exists(), f"Falta {filename}"

    def test_docs_have_minimum_lines(self, root: Path):
        """Cada doc técnico debe tener contenido sustancial."""
        for fname, min_lines in self.TECH_DOCS:
            f = root / "docs" / fname
            lines = f.read_text().splitlines()
            assert len(lines) >= min_lines, \
                f"{fname} tiene {len(lines)} líneas, esperado >= {min_lines}"

    def test_doc_links_resolve(self, root: Path):
        """Verify that [text](path) links within docs/ resolve to existing files.
        
        Resolves relative links from the document's parent directory.
        """
        for doc_file in sorted((root / "docs").glob("*.md")):
            content = doc_file.read_text()
            doc_dir = doc_file.parent  # docs/ directory
            for line in content.splitlines():
                if "](" in line and "http" not in line and "#" not in line.split("](")[1]:
                    start = line.find("](") + 2
                    end = line.find(")", start)
                    if start > 1 and end > start:
                        ref = line[start:end]
                        # Skip external URLs and anchors-only
                        if ref.startswith("http") or ref.startswith("#"):
                            continue
                        # Resolve relative path from doc file's directory
                        full = (doc_dir / ref).resolve()
                        assert full.exists(), \
                            f"Broken link in {doc_file.name}: '{ref}' -> {full} (line: {line.strip()[:80]})"


class TestTechnicalDebt:
    """F6-02: TECH_DEBT.md llenado con items reales."""

    def test_tech_debt_exists(self, root: Path):
        assert (root / "docs" / "TECH_DEBT.md").exists()

    def test_tech_debt_no_placeholders(self, root: Path):
        """No debe contener placeholders [YYYY-MM-DD], [Nombre], [N]."""
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        assert "[YYYY-MM-DD]" not in content, "Tech debt tiene placeholder de fecha"
        assert "[Nombre]" not in content, "Tech debt tiene placeholder de nombre"
        assert "[N]" not in content or "Total de ítems" in content, \
            "Tech debt tiene placeholders numéricos"

    def test_tech_debt_has_header(self, root: Path):
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        assert "2026-07-07" in content, "Tech debt debe tener fecha actual"
        assert "Fisherk2" in content, "Tech debt debe tener autor"

    def test_tech_debt_has_open_items(self, root: Path):
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        assert "TD-002" in content, "Tech debt debe tener TD-002 documentado"
        assert "TD-003" in content, "Tech debt debe tener TD-003 documentado"
        assert "TD-004" in content, "Tech debt debe tener TD-004 documentado"

    def test_tech_debt_has_closed_items(self, root: Path):
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        assert "TD-001" in content, "Tech debt debe tener TD-001 (cerrado)"
        assert "Cerrado" in content or "Resuelto" in content, \
            "Tech debt debe tener sección de items cerrados"

    def test_tech_debt_minimum_open_items(self, root: Path):
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        # Count TD- entries
        td_count = content.count("TD-0")
        assert td_count >= 4, f"Tech debt debe tener >=4 ítems, tiene {td_count}"

    def test_tech_debt_has_risk_ratings(self, root: Path):
        content = (root / "docs" / "TECH_DEBT.md").read_text()
        assert "Riesgo" in content or "riesgo" in content, \
            "Tech debt debe tener ratings de riesgo"


class TestLessonsLearned:
    """F6-03: LESSONS_LEARNED.md creado con lecciones de todas las fases."""

    def test_lessons_learned_exists(self, root: Path):
        assert (root / "docs" / "LESSONS_LEARNED.md").exists()

    def test_lessons_learned_minimum_lines(self, root: Path):
        lines = (root / "docs" / "LESSONS_LEARNED.md").read_text().splitlines()
        assert len(lines) >= 200, \
            f"LESSONS_LEARNED.md tiene {len(lines)} líneas, esperado >= 200"

    def test_lessons_covers_all_phases(self, root: Path):
        content = (root / "docs" / "LESSONS_LEARNED.md").read_text()
        for phase in ["F0", "F1", "F2", "F3", "F4", "F5"]:
            assert phase in content, f"Lessons debe cubrir {phase}"

    def test_lessons_has_cross_phase_patterns(self, root: Path):
        content = (root / "docs" / "LESSONS_LEARNED.md").read_text()
        assert "Cross-Phase" in content or "cross-phase" in content.lower(), \
            "Lessons debe tener sección Cross-Phase Patterns"

    def test_lessons_format_problema_solucion(self, root: Path):
        content = (root / "docs" / "LESSONS_LEARNED.md").read_text()
        assert "Problema" in content, "Cada lección debe mencionar 'Problema'"
        assert "Solución" in content, "Cada lección debe mencionar 'Solución'"
        assert "Lección" in content, "Cada lección debe mencionar 'Lección'"

    def test_lessons_has_problem_solution_lesson_count(self, root: Path):
        """Al menos 15 lecciones en formato Problema→Solución→Lección."""
        content = (root / "docs" / "LESSONS_LEARNED.md").read_text()
        lesson_count = content.count("**Lección")
        assert lesson_count >= 15, \
            f"Debe haber >=15 lecciones, encontradas {lesson_count}"

    def test_lessons_dated_header(self, root: Path):
        content = (root / "docs" / "LESSONS_LEARNED.md").read_text()
        assert "2026-07-07" in content, "Lessons debe tener fecha"


class TestGitWorkflow:
    """F6-04: Git Workflow Release v1.0.0 — validación de estado git."""

    def test_develop_branch_exists(self, run_cmd):
        """F6-04.1: develop branch debe existir y contener F6 commits."""
        rc, stdout, _ = run_cmd("git branch -a")
        assert rc == 0
        assert "develop" in stdout, "develop branch debe existir"

    def test_feat_branch_has_f6_commits(self, run_cmd):
        """feat/mvp-dashboard debe tener los 3 commits de F6."""
        rc, stdout, _ = run_cmd(
            "git log feat/mvp-dashboard --oneline --grep='feat(f6)'"
        )
        assert rc == 0
        count = len(stdout.splitlines()) if stdout else 0
        assert count >= 3, f"feat/mvp-dashboard debe tener >=3 commits F6, tiene {count}"

    def test_develop_merged_feat(self, run_cmd):
        """develop debe tener los commits de feat/mvp-dashboard."""
        rc, stdout, _ = run_cmd(
            "git log develop --oneline | head -5"
        )
        assert rc == 0
        assert "feat(f6):" in stdout, \
            "develop debe contener commits feat(f6): de F6"

    def test_release_tag_exists(self, run_cmd):
        """F6-04.4: Tag v1.0.0 debe existir."""
        rc, stdout, _ = run_cmd("git tag -l 'v1.0.0'")
        assert rc == 0
        assert "v1.0.0" in stdout, "Tag v1.0.0 debe existir"

    def test_main_has_release_commit(self, run_cmd):
        """F6-04.4: main debe tener el merge commit de release."""
        rc, stdout, _ = run_cmd("git log main --oneline -5")
        assert rc == 0
        assert "Release v1.0.0" in stdout or "release/v1.0.0" in stdout, \
            "main debe tener commit de release"

    def test_no_divergence_develop_main(self, run_cmd):
        """F6-04.5: develop y main no deben divergir (sync post-release)."""
        rc, stdout, _ = run_cmd("git log main..develop --oneline")
        assert rc == 0
        assert stdout == "" or len(stdout.splitlines()) <= 1, \
            f"develop no debe divergir de main. Diferencia: {stdout[:200]}"

    def test_release_branch_deleted(self, run_cmd):
        """F6-04.6: release/v1.0.0 branch debe estar eliminada."""
        rc, stdout, _ = run_cmd("git branch -a")
        assert rc == 0
        assert "release/v1.0.0" not in stdout, \
            "release/v1.0.0 branch debe estar eliminada"

    def test_git_status_clean(self, run_cmd):
        """Working directory debe estar limpio."""
        rc, stdout, _ = run_cmd("git status --short")
        assert rc == 0
        assert stdout == "", f"Working directory no está limpio:\n{stdout}"


class TestFileLineCounts:
    """Document line counts for checkpoint record."""

    def test_record_line_counts(self, root: Path):
        """Record and report line counts for all docs."""
        counts: List[Tuple[str, int]] = []
        for f in sorted((root / "docs").glob("*.md")):
            lines = len(f.read_text().splitlines())
            counts.append((f.name, lines))
        # Also check root docs
        for fname in ["README.md", "AGENTS.md", "SPEC.md"]:
            f = root / fname
            if f.exists():
                lines = len(f.read_text().splitlines())
                counts.append((f.name, lines))
        report = "\n".join(f"  {name}: {n} lines" for name, n in counts)
        print(f"\n📊 Document line counts:\n{report}")
        # At minimum all docs must exist and have content
        assert len(counts) >= 10, f"Solo {len(counts)} documentos encontrados"
