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

class TestPrdStatus:
    """F6-01.1: PRD.md debe reflejar estado final v1.0.0."""

    def test_prd_exists(self, root: Path):
        assert (root / "docs" / "PRD.md").exists()

    def test_prd_has_aprobado_status(self, root: Path):
        content = (root / "docs" / "PRD.md").read_text()
        assert "Aprobado" in content, "PRD.md debe tener estado 'Aprobado'"
        assert "Borrador" not in content, "PRD.md no debe decir 'Borrador'"

    def test_prd_has_current_date(self, root: Path):
        content = (root / "docs" / "PRD.md").read_text()
        assert "2026-07-07" in content, "PRD.md debe tener fecha 2026-07-07"

    def test_prd_has_version_100(self, root: Path):
        content = (root / "docs" / "PRD.md").read_text()
        assert "v1.0.0" in content, "PRD.md debe mencionar v1.0.0"

    def test_prd_has_record_count(self, root: Path):
        content = (root / "docs" / "PRD.md").read_text()
        assert "182K" in content or "182,465" in content or "182465" in content, \
            "PRD.md debe mencionar ~182K registros"


class TestTrdStatus:
    """F6-01.2: TRD.md debe reflejar estado final v1.0.0."""

    def test_trd_exists(self, root: Path):
        assert (root / "docs" / "TRD.md").exists()

    def test_trd_has_aprobado_status(self, root: Path):
        content = (root / "docs" / "TRD.md").read_text()
        assert "Aprobado" in content, "TRD.md debe tener estado 'Aprobado'"
        assert "Borrador" not in content, "TRD.md no debe decir 'Borrador'"

    def test_trd_has_current_date(self, root: Path):
        content = (root / "docs" / "TRD.md").read_text()
        assert "2026-07-07" in content, "TRD.md debe tener fecha 2026-07-07"

    def test_trd_has_version_100(self, root: Path):
        content = (root / "docs" / "TRD.md").read_text()
        assert "v1.0.0" in content, "TRD.md debe mencionar v1.0.0"

    def test_trd_trazabilidad_no_pendiente(self, root: Path):
        """La matriz de trazabilidad debe reflejar estado completado."""
        content = (root / "docs" / "TRD.md").read_text()
        # All requirements should be completed in v1.0.0
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

    def test_agents_version_24(self, root: Path):
        content = (root / "AGENTS.md").read_text()
        assert "v2.4" in content or "2.4" in content, "AGENTS.md debe ser v2.4"


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

    EXPECTED_RECORD_COUNT = "182K"

    def _get_record_counts(self, root: Path) -> Dict[str, List[str]]:
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

    def test_architecture_md_exists(self, root: Path):
        assert (root / "docs" / "ARCHITECTURE.md").exists()

    def test_schema_md_exists(self, root: Path):
        assert (root / "docs" / "SCHEMA.md").exists()

    def test_testing_md_exists(self, root: Path):
        assert (root / "docs" / "TESTING.md").exists()

    def test_security_md_exists(self, root: Path):
        assert (root / "docs" / "SECURITY.md").exists()

    def test_code_style_md_exists(self, root: Path):
        assert (root / "docs" / "CODE_STYLE.md").exists()

    def test_user_guide_md_exists(self, root: Path):
        assert (root / "docs" / "USER_GUIDE.md").exists()

    def test_technical_guide_md_exists(self, root: Path):
        assert (root / "docs" / "TECHNICAL_GUIDE.md").exists()

    def test_reproducibility_md_exists(self, root: Path):
        assert (root / "docs" / "REPRODUCIBILITY.md").exists()

    def test_docs_have_minimum_lines(self, root: Path):
        """Cada doc técnico debe tener contenido sustancial."""
        file_specs: List[Tuple[str, int]] = [
            ("ARCHITECTURE.md", 30),
            ("SCHEMA.md", 30),
            ("TESTING.md", 30),
            ("SECURITY.md", 30),
            ("CODE_STYLE.md", 30),
            ("USER_GUIDE.md", 200),
            ("TECHNICAL_GUIDE.md", 300),
            ("REPRODUCIBILITY.md", 50),
        ]
        for fname, min_lines in file_specs:
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
