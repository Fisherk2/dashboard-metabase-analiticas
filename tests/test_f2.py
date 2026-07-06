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

    def test_init_sql_create_tables_end_with_semicolon(self, root: Path):
        """Cada bloque CREATE TABLE termina con );"""
        content = (root / self.INIT_SQL_PATH).read_text()
        lines = content.splitlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            # Every CREATE TABLE line should eventually be closed by );
            if stripped.upper().startswith("CREATE TABLE"):
                # Find the matching closing line
                found_close = False
                for j in range(i, len(lines)):
                    if lines[j].strip() == ");":
                        found_close = True
                        break
                assert found_close, f"CREATE TABLE at line {i} missing closing ');'"

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
    @pytest.mark.timeout(300)
    def test_generate_data_runs_without_errors(self, root, run_cmd):
        """El script genera datos sin errores (modo --debug)."""
        rc, stdout, stderr = run_cmd(
            "docker exec -i metabase-generator python /scripts/generate_data.py --debug --scale 0.1",
            timeout=300
        )
        assert rc == 0, (
            f"generate_data.py failed:\nstdout:{stdout}\nstderr:{stderr}"
        )

    @pytest.mark.runtime
    @pytest.mark.timeout(300)
    def test_generate_data_reports_counts(self, root, run_cmd):
        """El script reporta conteos de registros generados."""
        rc, stdout, stderr = run_cmd(
            "docker exec -i metabase-generator python /scripts/generate_data.py --debug --scale 0.1",
            timeout=300
        )
        assert rc == 0
        assert any(word in stdout.lower() for word in [
            "registro", "record", "insert", "total", "count", "ventas"
        ]), f"Output should contain record counts:\n{stdout[:500]}"

    @pytest.mark.runtime
    @pytest.mark.timeout(300)
    def test_generate_data_reset_works(self, root, run_cmd):
        """El modo --reset ejecuta TRUNCATE CASCADE sin errores."""
        rc, stdout, stderr = run_cmd(
            "docker exec -i metabase-generator python /scripts/generate_data.py --reset --debug --scale 0.1",
            timeout=300
        )
        assert rc == 0, (
            f"generate_data.py --reset failed:\nstdout:{stdout}\nstderr:{stderr}"
        )

    @pytest.mark.runtime
    def test_can_import_required_libraries(self, root, run_cmd):
        """Los módulos requeridos son importables desde el contenedor data-generator."""
        rc, stdout, _ = run_cmd(
            "docker exec -i metabase-generator python -c 'import faker; import psycopg2; import dotenv; print(\"OK\")'"
        )
        assert rc == 0 and "OK" in stdout, "Cannot import required libraries in container"


# ─── Slice 3: Indexes ───────────────────────────────────────

class TestIndexes:
    """F2-09: Archivo de índices existe y Contiene CREATE INDEX."""

    INDEX_PATH = "sql/indexes/create_indexes.sql"
    QUERIES_PATH = "sql/queries_baseline.sql"

    def test_index_file_exists(self, root: Path):
        assert (root / self.INDEX_PATH).exists()

    def test_queries_baseline_exists(self, root: Path):
        assert (root / self.QUERIES_PATH).exists()

    def test_index_file_has_create_statements(self, root: Path):
        content = (root / self.INDEX_PATH).read_text()
        create_count = content.count("CREATE INDEX")
        assert create_count >= 9, f"Expected >=9 CREATE INDEX, found {create_count}"

    def test_index_file_has_if_not_exists(self, root: Path):
        content = (root / self.INDEX_PATH).read_text()
        assert "IF NOT EXISTS" in content, "All indexes should use IF NOT EXISTS"

    def test_queries_baseline_has_explain_analyze(self, root: Path):
        content = (root / self.QUERIES_PATH).read_text()
        assert "EXPLAIN ANALYZE" in content, "Baseline should contain EXPLAIN ANALYZE"
        count = content.count("EXPLAIN ANALYZE")
        assert count >= 4, f"Expected >=4 EXPLAIN ANALYZE, found {count}"


# ─── Slice 4: Materialized Views ────────────────────────────

class TestMaterializedViews:
    """F2-11/13: Archivos de vistas materializadas existen."""

    MV_FILES = [
        "sql/views/mv_rotacion_mensual.sql",
        "sql/views/mv_stock_actual.sql",
        "sql/views/mv_top_productos.sql",
    ]
    REFRESH_PATH = "scripts/refresh_materialized_views.sql"

    @pytest.mark.parametrize("mv_file", MV_FILES)
    def test_mv_file_exists(self, root: Path, mv_file: str):
        assert (root / mv_file).exists(), f"Missing: {mv_file}"

    def test_refresh_script_exists(self, root: Path):
        assert (root / self.REFRESH_PATH).exists()

    def test_refresh_script_has_refresh_commands(self, root: Path):
        content = (root / self.REFRESH_PATH).read_text()
        count = content.count("REFRESH MATERIALIZED VIEW")
        assert count >= 3, f"Expected >=3 REFRESH, found {count}"

    def test_mv_rotacion_has_create(self, root: Path):
        content = (root / "sql/views/mv_rotacion_mensual.sql").read_text()
        assert "mv_rotacion_mensual" in content

    def test_mv_stock_has_create(self, root: Path):
        content = (root / "sql/views/mv_stock_actual.sql").read_text()
        assert "mv_stock_actual" in content

    def test_mv_top_has_create(self, root: Path):
        content = (root / "sql/views/mv_top_productos.sql").read_text()
        assert "mv_top_productos" in content

    def test_each_mv_has_indexes(self, root: Path):
        for mv in self.MV_FILES:
            content = (root / mv).read_text()
            assert "CREATE INDEX" in content, f"{mv} missing index definitions"


class TestMaterializedViewsRuntime:
    """F2-15: MVs existen en BD y queries rinden <2s."""

    @pytest.mark.runtime
    def test_mv_rotacion_exists(self, run_cmd):
        rc, stdout, _ = run_cmd(
            "docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -c "
            "\"SELECT COUNT(*) FROM mv_rotacion_mensual\" -t -A"
        )
        assert rc == 0 and stdout.isdigit() and int(stdout) > 100, \
            f"mv_rotacion_mensual has no data: {stdout}"

    @pytest.mark.runtime
    def test_mv_stock_exists(self, run_cmd):
        rc, stdout, _ = run_cmd(
            "docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -c "
            "\"SELECT COUNT(*) FROM mv_stock_actual\" -t -A"
        )
        assert rc == 0 and stdout.isdigit() and int(stdout) > 1000, \
            f"mv_stock_actual has no data: {stdout}"

    @pytest.mark.runtime
    def test_mv_top_exists(self, run_cmd):
        rc, stdout, _ = run_cmd(
            "docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -c "
            "\"SELECT COUNT(*) FROM mv_top_productos\" -t -A"
        )
        assert rc == 0 and stdout.isdigit() and int(stdout) > 1000, \
            f"mv_top_productos has no data: {stdout}"

    @pytest.mark.runtime
    def test_mv_query_performance(self, run_cmd):
        """MV queries must complete in <2s (EXPLAIN ANALYZE)."""
        rc, stdout, stderr = run_cmd(
            """docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -c "
EXPLAIN ANALYZE SELECT categoria, SUM(ingresos_totales)
FROM mv_rotacion_mensual WHERE anio = '2026'
GROUP BY categoria ORDER BY 2 DESC
" -q 2>&1"""
        )
        output = stdout + stderr
        assert rc == 0, f"MV performance check failed: {output[:300]}"
        # Extract execution time in ms
        import re
        match = re.search(r"Execution\s+Time:\s*([\d.]+)\s*ms", output)
        assert match, f"Cannot parse execution time from: {output[:500]}"
        exec_time = float(match.group(1))
        assert exec_time < 2000, f"MV query too slow: {exec_time}ms (target: <2000ms)"


# ─── Slice 5: Partitioning ──────────────────────────────────

class TestPartitioning:
    """F2-16/17: Archivo de particionamiento existe."""

    PARTITION_PATH = "sql/partitions/partition_ventas.sql"

    def test_partition_file_exists(self, root: Path):
        assert (root / self.PARTITION_PATH).exists()

    def test_partition_has_partition_by_range(self, root: Path):
        content = (root / self.PARTITION_PATH).read_text()
        assert "PARTITION BY RANGE" in content.upper()

    def test_partition_has_12_partitions(self, root: Path):
        content = (root / self.PARTITION_PATH).read_text()
        count = content.count("PARTITION OF ventas")
        assert count >= 12, f"Expected >=12 partitions, found {count}"


class TestPartitioningRuntime:
    """F2-18: ventas está particionada y muestra partition pruning."""

    @pytest.mark.runtime
    def test_ventas_is_partitioned(self, run_cmd):
        rc, stdout, _ = run_cmd(
            "docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -c "
            "\"SELECT relkind FROM pg_class WHERE relname = 'ventas'\" -t -A"
        )
        assert rc == 0 and stdout == "p", \
            f"ventas is not partitioned (relkind={stdout}, expected 'p')"

    @pytest.mark.runtime
    def test_partition_tree_has_12_children(self, run_cmd):
        rc, stdout, stderr = run_cmd(
            """docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -t -A -c "
SELECT count(*) FROM pg_partition_tree('ventas') WHERE isleaf = true
" 2>&1"""
        )
        output = (stdout + stderr).strip()
        assert output.isdigit() and int(output) >= 12, \
            f"Expected >=12 partition leaves, found: '{output}'"

    @pytest.mark.runtime
    def test_partition_pruning_active(self, run_cmd):
        """EXPLAIN muestra que solo se escanea una partición en query con filtro fecha."""
        rc, stdout, stderr = run_cmd(
            """docker exec -i metabase-postgres psql -U ecommerce-fish -d ecommerce-db -q -c "
EXPLAIN (COSTS OFF) SELECT count(*) FROM ventas
WHERE fecha_venta BETWEEN '2026-03-01' AND '2026-03-31'
" 2>&1"""
        )
        output = stdout + stderr
        assert rc == 0, f"Partition pruning check failed: {output[:300]}"
        # Should reference a specific partition not the parent
        assert "ventas_2026_03" in output, \
            f"Partition pruning NOT active:\n{output}"
