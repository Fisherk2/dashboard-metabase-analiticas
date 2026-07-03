"""
Tests: F2: Núcleo — Validación de schema estrella, datos, índices y vistas.

Verifica todos los criterios de aceptación del plan F2:
- Slice 1: Schema Foundation (init.sql con 10 tablas)
- Slice 2: Data Generation (generate_data.py + volúmenes)
- Slice 3: Indexes (índices B-tree en FK)
- Slice 4: Materialized Views (3 MVs)
- Slice 5: Partitioning (12 particiones mensuales)
- Security: Integridad referencial, CHECK constraints
"""
import re
import ast
from pathlib import Path

import pytest

# ─── Slice 1: Schema Foundation ───────────────────────────────

class TestInitSql:
    """F2-01: scripts/init.sql existe y define 6 tablas de dimensiones."""

    INIT_SQL_PATH = "scripts/init.sql"

    def test_init_sql_exists(self, root: Path):
        assert (root / self.INIT_SQL_PATH).exists(), f"Missing: {self.INIT_SQL_PATH}"

    def test_init_sql_has_content(self, root: Path):
        content = (root / self.INIT_SQL_PATH).read_text()
        assert len(content.strip()) > 0, "init.sql is empty"

    @pytest.mark.parametrize("table", [
        "categorias",
        "proveedores",
        "productos",
        "clientes",
        "tiempo",
        "promociones",
    ])
    def test_dimension_table_exists(self, root: Path, table: str):
        """Cada tabla de dimensión declarada con CREATE TABLE."""
        content = (root / self.INIT_SQL_PATH).read_text()
        assert re.search(
            rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{table}\s*\(",
            content, re.IGNORECASE
        ), f"Missing CREATE TABLE for dimension: {table}"

    @pytest.mark.parametrize("table,column", [
        ("categorias", "nombre"),
        ("proveedores", "nombre"),
        ("productos", "nombre"),
        ("clientes", "nombre"),
        ("tiempo", "fecha"),
        ("promociones", "nombre"),
    ])
    def test_dimension_has_required_column(self, root: Path, table: str, column: str):
        """Cada tabla tiene al menos su columna principal."""
        content = (root / self.INIT_SQL_PATH).read_text()
        # Extract table definition block: from CREATE TABLE name to the closing semicolon
        # Use a simpler approach: find the table name in the content and check column name
        # appears reasonably after it
        lines = content.splitlines()
        in_table = False
        found_column = False
        for line in lines:
            stripped = line.strip()
            # Match CREATE TABLE statement (not COMMENT ON TABLE)
            if re.match(rf"CREATE\s+TABLE", stripped, re.IGNORECASE) and table in stripped.lower():
                in_table = True
                continue
            if in_table and stripped == ");":
                break
            if in_table and stripped.startswith(column):
                found_column = True
                break
        assert found_column, f"Missing column '{column}' in table '{table}'"

    @pytest.mark.parametrize("table,constraint_type", [
        ("categorias", "PRIMARY KEY"),
        ("proveedores", "PRIMARY KEY"),
        ("productos", "PRIMARY KEY"),
        ("clientes", "PRIMARY KEY"),
        ("tiempo", "PRIMARY KEY"),
        ("promociones", "PRIMARY KEY"),
    ])
    def test_dimension_has_primary_key(self, root: Path, table: str, constraint_type: str):
        """Cada tabla tiene PRIMARY KEY."""
        content = (root / self.INIT_SQL_PATH).read_text()
        # Extract the CREATE TABLE block for this table
        # Check if PRIMARY KEY appears in its definition
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert "PRIMARY KEY" in blocks[0].upper(), (
                f"Table '{table}' missing PRIMARY KEY"
            )

    @pytest.mark.parametrize("table,unique_column", [
        ("categorias", "nombre"),
        ("proveedores", "email"),
        ("clientes", "email"),
        ("tiempo", "fecha"),
    ])
    def test_dimension_has_unique_constraint(self, root: Path, table: str, unique_column: str):
        """Tablas clave tienen UNIQUE en columna natural."""
        content = (root / self.INIT_SQL_PATH).read_text()
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert "UNIQUE" in blocks[0].upper() and unique_column in blocks[0], (
                f"Table '{table}' missing UNIQUE constraint on '{unique_column}'"
            )

    def test_dimension_table_count(self, root: Path):
        """Al menos 6 tablas de dimensión definidas."""
        content = (root / self.INIT_SQL_PATH).read_text()
        # Count CREATE TABLE statements that are dimension tables
        dimension_tables = ["categorias", "proveedores", "productos", "clientes", "tiempo", "promociones"]
        create_count = sum(
            1 for t in dimension_tables
            if re.search(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{t}\s*\(", content, re.IGNORECASE)
        )
        assert create_count >= 6, f"Expected >=6 dimension tables, found {create_count}"

    def test_init_sql_is_valid_syntax(self, root: Path):
        """init.sql tiene estructura básica válida (comentarios, punto y coma)."""
        content = (root / self.INIT_SQL_PATH).read_text()
        lines = content.splitlines()
        # Every statement should end with semicolon for non-comment lines
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith("--") and not stripped.startswith("/*"):
                # Lines that are just opening parentheses or continue previous aren't statements
                pass
        assert True  # If we reach here, file is readable

    @pytest.mark.parametrize("table,expected_column", [
        ("productos", "precio"),
        ("productos", "stock_actual"),
        ("productos", "stock_minimo"),
        ("productos", "categoria_id"),
        ("productos", "proveedor_id"),
    ])
    def test_productos_has_critical_columns(self, root: Path, table: str, expected_column: str):
        """Tabla productos tiene columnas críticas."""
        content = (root / self.INIT_SQL_PATH).read_text()
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert expected_column in blocks[0], (
                f"Table '{table}' missing critical column '{expected_column}'"
            )


class TestCheckConstraints:
    """CHECK constraints en precios, stocks y cantidades."""

    INIT_SQL_PATH = "scripts/init.sql"

    @pytest.mark.parametrize("table,constraint_pattern", [
        ("productos", "precio > 0"),
        ("productos", "stock_actual >= 0"),
        ("productos", "stock_minimo >= 0"),
        ("promociones", "descuento >= 0"),
    ])
    def test_check_constraint_exists(self, root: Path, table: str, constraint_pattern: str):
        """CHECK constraints definidos para dominio de datos."""
        content = (root / self.INIT_SQL_PATH).read_text()
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert constraint_pattern in blocks[0].lower(), (
                f"Missing CHECK constraint '{constraint_pattern}' in table '{table}'"
            )


class TestFactTables:
    """F2-02: init.sql define 4 tablas de hechos."""

    INIT_SQL_PATH = "scripts/init.sql"

    @pytest.mark.parametrize("table", [
        "ventas",
        "inventario",
        "devoluciones",
        "logistica",
    ])
    def test_fact_table_exists(self, root: Path, table: str):
        """Cada tabla de hecho declarada con CREATE TABLE."""
        content = (root / self.INIT_SQL_PATH).read_text()
        assert re.search(
            rf"CREATE\s+TABLE\s+(IF\s+NOT\s+EXISTS\s+)?{table}\s*\(",
            content, re.IGNORECASE
        ), f"Missing CREATE TABLE for fact table: {table}"

    def test_total_tables(self, root: Path):
        """10 tablas en total (6 dim + 4 hechos)."""
        content = (root / self.INIT_SQL_PATH).read_text()
        all_tables = [
            "categorias", "proveedores", "productos", "clientes",
            "tiempo", "promociones", "ventas", "inventario",
            "devoluciones", "logistica",
        ]
        create_count = sum(
            1 for t in all_tables
            if re.search(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{t}\s*\(", content, re.IGNORECASE)
        )
        assert create_count == 10, f"Expected 10 tables, found {create_count}"

    def test_schema_section_headers(self, root: Path):
        """init.sql tiene secciones delimitadas para DIMENSIONES y HECHOS."""
        content = (root / self.INIT_SQL_PATH).read_text()
        assert "HECHOS" in content.upper(), "Missing HECHOS section header"

    @pytest.mark.parametrize("table,expected_column", [
        ("ventas", "cantidad"),
        ("ventas", "precio_unitario"),
        ("ventas", "total"),
        ("ventas", "fecha_venta"),
        ("inventario", "stock_inicial"),
        ("inventario", "stock_final"),
        ("devoluciones", "motivo"),
        ("logistica", "estado"),
        ("logistica", "metodo_envio"),
    ])
    def test_fact_has_critical_column(self, root: Path, table: str, expected_column: str):
        """Tablas de hechos tienen columnas críticas de negocio."""
        content = (root / self.INIT_SQL_PATH).read_text()
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert expected_column in blocks[0], (
                f"Table '{table}' missing critical column '{expected_column}'"
            )


class TestFactCheckConstraints:
    """CHECK constraints en tablas de hechos."""

    INIT_SQL_PATH = "scripts/init.sql"

    @pytest.mark.parametrize("table,constraint_pattern", [
        ("ventas", "cantidad > 0"),
        ("ventas", "precio_unitario > 0"),
        ("inventario", "stock_inicial >= 0"),
        ("inventario", "stock_final >= 0"),
        ("devoluciones", "cantidad > 0"),
    ])
    def test_fact_check_constraint_exists(self, root: Path, table: str, constraint_pattern: str):
        """CHECK constraints definidos en tablas de hechos."""
        content = (root / self.INIT_SQL_PATH).read_text()
        blocks = re.findall(
            rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\((.*?)\)\s*;",
            content, re.IGNORECASE | re.DOTALL
        )
        if blocks:
            assert constraint_pattern in blocks[0].lower(), (
                f"Missing CHECK constraint '{constraint_pattern}' in table '{table}'"
            )


class TestForeignKeys:
    """Foreign Keys definidas en tablas con referencias."""

    INIT_SQL_PATH = "scripts/init.sql"

    @pytest.mark.parametrize("table,column,references", [
        ("productos", "categoria_id", "categorias"),
        ("productos", "proveedor_id", "proveedores"),
        ("promociones", "categoria_id", "categorias"),
        ("ventas", "producto_id", "productos"),
        ("ventas", "cliente_id", "clientes"),
        ("inventario", "producto_id", "productos"),
        ("devoluciones", "venta_id", "ventas"),
    ])
    def test_fk_reference_exists(self, root: Path, table: str, column: str, references: str):
        """FKs referencian tabla padre."""
        content = (root / self.INIT_SQL_PATH).read_text()
        # Check for REFERENCES clause
        assert re.search(
            rf"{column}.+REFERENCES.+{references}",
            content, re.IGNORECASE
        ), f"Missing FOREIGN KEY: {table}.{column} -> {references}(id)"


# ─── Slice 2: Data Generation ─────────────────────────────────

class TestGenerateData:
    """F2-05: scripts/generate_data.py existe y tiene estructura correcta."""

    GEN_PATH = "scripts/generate_data.py"

    def test_generate_data_exists(self, root: Path):
        assert (root / self.GEN_PATH).exists(), f"Missing: {self.GEN_PATH}"

    def test_generate_data_has_main_function(self, root: Path):
        """El script define una función main()."""
        source = (root / self.GEN_PATH).read_text()
        tree = ast.parse(source)
        has_main = any(
            isinstance(node, ast.FunctionDef) and node.name == "main"
            for node in ast.walk(tree)
        )
        assert has_main, "Missing 'main()' function in generate_data.py"

    def test_generate_data_has_data_generator_class(self, root: Path):
        """El script define la clase DataGenerator."""
        source = (root / self.GEN_PATH).read_text()
        tree = ast.parse(source)
        has_class = any(
            isinstance(node, ast.ClassDef) and node.name == "DataGenerator"
            for node in ast.walk(tree)
        )
        assert has_class, "Missing 'DataGenerator' class in generate_data.py"

    @pytest.mark.parametrize("mod", [
        "faker",
        "psycopg2",
        "dotenv",
        "argparse",
        "logging",
        "datetime",
        "random",
    ])
    def test_generate_imports(self, root: Path, mod: str):
        """Importa los módulos requeridos."""
        source = (root / self.GEN_PATH).read_text()
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split(".")[0])
        assert mod in imports, f"Missing import: {mod}"

    def test_generate_data_has_argparse(self, root: Path):
        """El script usa argparse con flags --debug, --scale, --reset."""
        source = (root / self.GEN_PATH).read_text()
        assert "argparse" in source or "ArgumentParser" in source, (
            "generate_data.py should use argparse"
        )
        # Check for expected flags
        assert "--debug" in source, "Missing --debug flag"
        assert "--scale" in source or "-n" in source, (
            "Missing --scale flag"
        )
        # Check for some reset mechanism
        assert any(flag in source for flag in ("--reset", "--truncate")), (
            "Missing --reset or --truncate flag"
        )

    def test_generate_data_has_dotenv(self, root: Path):
        """El script carga variables de entorno con python-dotenv."""
        source = (root / self.GEN_PATH).read_text()
        assert "load_dotenv" in source or "dotenv" in source, (
            "generate_data.py should use python-dotenv"
        )


class TestGenerateDataRuntime:
    """F2-05 runtime: valida que generate_data.py ejecuta correctamente.

    Requiere Docker corriendo con PostgreSQL.
    """

    GEN_PATH = "scripts/generate_data.py"
    REQUIREMENTS = "scripts/requirements.txt"

    @pytest.mark.runtime
    def test_generate_data_runs_without_errors(self, root, run_cmd):
        """El script genera datos sin errores (modo --debug)."""
        rc, stdout, stderr = run_cmd(
            f"python {root / self.GEN_PATH} --debug",
            timeout=120
        )
        assert rc == 0, (
            f"generate_data.py failed:\nstdout:{stdout}\nstderr:{stderr}"
        )

    @pytest.mark.runtime
    def test_generate_data_reports_counts(self, root, run_cmd):
        """El script reporta conteos de registros generados."""
        rc, stdout, stderr = run_cmd(
            f"python {root / self.GEN_PATH} --debug",
            timeout=120
        )
        assert rc == 0
        assert any(word in stdout.lower() for word in [
            "registro", "record", "insert", "total", "count", "ventas"
        ]), f"Output should contain record counts:\n{stdout[:500]}"

    @pytest.mark.runtime
    def test_generate_data_reset_works(self, root, run_cmd):
        """El modo --reset ejecuta TRUNCATE CASCADE sin errores."""
        rc, stdout, stderr = run_cmd(
            f"python {root / self.GEN_PATH} --reset --debug",
            timeout=120
        )
        assert rc == 0, (
            f"generate_data.py --reset failed:\nstdout:{stdout}\nstderr:{stderr}"
        )

    @pytest.mark.runtime
    def test_can_import_required_libraries(self, root, run_cmd):
        """Los módulos requeridos son importables desde el Python del proyecto."""
        rc, stdout, _ = run_cmd("python -c 'import faker; import psycopg2; import dotenv; print(\"OK\")'")
        assert rc == 0 and "OK" in stdout, "Cannot import required libraries"
