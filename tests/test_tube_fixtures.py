"""
Tests parametrizados para importación CSV de tubería conduit.

Cubre los 6 tipos de tubería × diámetros representativos para:
  - LDM: description, unit, qty, catalog_item_id linkeo
  - COT: description, unit, qty, price=vacío, total=0.0, catalog_item_id

Los nombres de los conceptos replican exactamente la salida de
crt-tube-commercial-description en CedulaRecTables.lsp para que este
test actúe como contrato entre el LISP y el parser Python.
"""

import csv
import os
import tempfile
import unittest

from tracker.csv_import import parse_ldm_csv
from tracker.quote_csv_import import parse_quote_csv


# ---------------------------------------------------------------------------
# Catálogo mínimo — subset de los nombres que genera el LISP
# ---------------------------------------------------------------------------

SAMPLE_CATALOG = [
    # Galvanizado Pared Delgada
    {"id": "56A13CED", "nombre": 'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 27 [mm] (1")'},
    {"id": "AA000001", "nombre": 'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 41 [mm] (1 1/2")'},
    {"id": "AA000002", "nombre": 'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 63 [mm] (2 1/2")'},
    # Galvanizado Pared Gruesa
    {"id": "BB000001", "nombre": 'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 27 [mm] (1")'},
    {"id": "3E6A5776", "nombre": 'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 63 [mm] (2 1/2")'},
    # PVC SP
    {"id": "CC000001", "nombre": 'Metro Lineal de Tubería Conduit PVC SP | 27 [mm] (1")'},
    {"id": "846D8E87", "nombre": 'Metro Lineal de Tubería Conduit PVC SP | 63 [mm] (2 1/2")'},
    # PAD Flexible Corrugado
    {"id": "490E6DE2", "nombre": 'Metro Lineal de Tubería Conduit PAD Flexible Corrugado | 35 [mm] (1 1/4")'},
    {"id": "A0CB20A9", "nombre": 'Metro Lineal de Tubería Conduit PAD Flexible Corrugado | 63 [mm] (2 1/2")'},
    # Metálico Flexible
    {"id": "C61F3E26", "nombre": 'Metro Lineal de Tubería Conduit Metálico Flexible | 35 [mm] (1 1/4")'},
    {"id": "35B36A01", "nombre": 'Metro Lineal de Tubería Conduit Metálico Flexible | 63 [mm] (2 1/2")'},
    # Flexible Licuatite
    {"id": "5529E709", "nombre": 'Metro Lineal de Tubería Conduit Flexible Licuatite | 35 [mm] (1 1/4")'},
    {"id": "CE2F93DF", "nombre": 'Metro Lineal de Tubería Conduit Flexible Licuatite | 63 [mm] (2 1/2")'},
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_ldm(path, rows, meta_rows=None):
    """Escribe un CSV LDM con header estándar y filas dadas.

    meta_rows: lista de tuplas (key, value) que se escriben como filas #key DESPUÉS del header,
    replicando el formato real del LISP (metadata post-header).
    """
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["description", "unit", "qty"])
        for key, value in (meta_rows or []):
            writer.writerow([f"#{key}", value, ""])
        for desc, unit, qty in rows:
            writer.writerow([desc, unit, qty])


def _write_cot(path, rows, meta=""):
    """Escribe un CSV COT con header estándar y filas dadas (price vacío = LISP sin cotizar)."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        if meta:
            f.write(meta)
        writer = csv.writer(f)
        writer.writerow(["description", "unit", "qty", "price"])
        for desc, unit, qty, price in rows:
            writer.writerow([desc, unit, qty, price])


# ---------------------------------------------------------------------------
# LDM parametrized tests
# ---------------------------------------------------------------------------

# (description, unit, qty_str, expected_qty, expected_catalog_id)
LDM_TUBE_CASES = [
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 27 [mm] (1")',
        "ML", "47", 47.0, "56A13CED",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 41 [mm] (1 1/2")',
        "ML", "120", 120.0, "AA000001",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 63 [mm] (2 1/2")',
        "ML", "8", 8.0, "AA000002",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 27 [mm] (1")',
        "ML", "33", 33.0, "BB000001",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 63 [mm] (2 1/2")',
        "ML", "15", 15.0, "3E6A5776",
    ),
    (
        'Metro Lineal de Tubería Conduit PVC SP | 27 [mm] (1")',
        "ML", "60", 60.0, "CC000001",
    ),
    (
        'Metro Lineal de Tubería Conduit PVC SP | 63 [mm] (2 1/2")',
        "ML", "22", 22.0, "846D8E87",
    ),
    (
        'Metro Lineal de Tubería Conduit PAD Flexible Corrugado | 35 [mm] (1 1/4")',
        "ML", "5", 5.0, "490E6DE2",
    ),
    (
        'Metro Lineal de Tubería Conduit PAD Flexible Corrugado | 63 [mm] (2 1/2")',
        "ML", "3", 3.0, "A0CB20A9",
    ),
    (
        'Metro Lineal de Tubería Conduit Metálico Flexible | 35 [mm] (1 1/4")',
        "ML", "10", 10.0, "C61F3E26",
    ),
    (
        'Metro Lineal de Tubería Conduit Metálico Flexible | 63 [mm] (2 1/2")',
        "ML", "4", 4.0, "35B36A01",
    ),
    (
        'Metro Lineal de Tubería Conduit Flexible Licuatite | 35 [mm] (1 1/4")',
        "ML", "7", 7.0, "5529E709",
    ),
    (
        'Metro Lineal de Tubería Conduit Flexible Licuatite | 63 [mm] (2 1/2")',
        "ML", "2", 2.0, "CE2F93DF",
    ),
]


class LdmTubeFixturesTest(unittest.TestCase):

    def _run_ldm_case(self, description, unit, qty_str, expected_qty, expected_catalog_id):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v1-i1-20260523.csv")
            _write_ldm(path, [(description, unit, qty_str)])
            result = parse_ldm_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [], msg=f"Errors for: {description}")
        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["description"], description)
        self.assertEqual(item["qty"], expected_qty, msg=f"qty mismatch for: {description}")
        self.assertEqual(item["catalog_item_id"], expected_catalog_id,
                         msg=f"catalog_item_id mismatch for: {description}")
        self.assertEqual(item["origen"], "csv")

    def test_ldm_galvanizado_pared_delgada_27mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[0])

    def test_ldm_galvanizado_pared_delgada_41mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[1])

    def test_ldm_galvanizado_pared_delgada_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[2])

    def test_ldm_galvanizado_pared_gruesa_27mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[3])

    def test_ldm_galvanizado_pared_gruesa_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[4])

    def test_ldm_pvc_sp_27mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[5])

    def test_ldm_pvc_sp_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[6])

    def test_ldm_pad_flexible_corrugado_35mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[7])

    def test_ldm_pad_flexible_corrugado_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[8])

    def test_ldm_metalico_flexible_35mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[9])

    def test_ldm_metalico_flexible_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[10])

    def test_ldm_flexible_licuatite_35mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[11])

    def test_ldm_flexible_licuatite_63mm(self):
        self._run_ldm_case(*LDM_TUBE_CASES[12])

    def test_ldm_mixed_tubes_single_file(self):
        """Múltiples tipos de tubería en un mismo archivo LDM."""
        rows = [
            (LDM_TUBE_CASES[0][0], "ML", "47"),
            (LDM_TUBE_CASES[5][0], "ML", "60"),
            (LDM_TUBE_CASES[9][0], "ML", "10"),
        ]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v1-i1-20260523.csv")
            _write_ldm(path, rows)
            result = parse_ldm_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["items"]), 3)
        self.assertEqual(result["items"][0]["catalog_item_id"], "56A13CED")
        self.assertEqual(result["items"][1]["catalog_item_id"], "CC000001")
        self.assertEqual(result["items"][2]["catalog_item_id"], "C61F3E26")

    def test_ldm_with_metadata_proveedor_fecha(self):
        """Metadata #proveedor y #fecha post-header (formato real del LISP)."""
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM002-v2-i1-20260523.csv")
            _write_ldm(
                path,
                [('Metro Lineal de Tubería Conduit PVC SP | 27 [mm] (1")', "ML", "30")],
                meta_rows=[("proveedor", "Procables de Mexico"), ("fecha", "2026-05-23")],
            )
            result = parse_ldm_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["metadata"]["proveedor"], "Procables de Mexico")
        self.assertEqual(result["metadata"]["fecha"], "2026-05-23")


# ---------------------------------------------------------------------------
# COT parametrized tests
# ---------------------------------------------------------------------------

# (description, unit, qty_str, price_str, expected_qty, expected_price, expected_total, catalog_id)
COT_TUBE_CASES = [
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 27 [mm] (1")',
        "ML", "47", "", 47.0, 0.0, 0.0, "56A13CED",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 63 [mm] (2 1/2")',
        "ML", "8", "350", 8.0, 350.0, 2800.0, "AA000002",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 27 [mm] (1")',
        "ML", "33", "", 33.0, 0.0, 0.0, "BB000001",
    ),
    (
        'Metro Lineal de Tubería Conduit Galvanizado Pared Gruesa | 63 [mm] (2 1/2")',
        "ML", "15", "520", 15.0, 520.0, 7800.0, "3E6A5776",
    ),
    (
        'Metro Lineal de Tubería Conduit PVC SP | 27 [mm] (1")',
        "ML", "60", "180", 60.0, 180.0, 10800.0, "CC000001",
    ),
    (
        'Metro Lineal de Tubería Conduit PVC SP | 63 [mm] (2 1/2")',
        "ML", "22", "", 22.0, 0.0, 0.0, "846D8E87",
    ),
    (
        'Metro Lineal de Tubería Conduit PAD Flexible Corrugado | 63 [mm] (2 1/2")',
        "ML", "3", "900", 3.0, 900.0, 2700.0, "A0CB20A9",
    ),
    (
        'Metro Lineal de Tubería Conduit Metálico Flexible | 35 [mm] (1 1/4")',
        "ML", "10", "250", 10.0, 250.0, 2500.0, "C61F3E26",
    ),
    (
        'Metro Lineal de Tubería Conduit Metálico Flexible | 63 [mm] (2 1/2")',
        "ML", "4", "", 4.0, 0.0, 0.0, "35B36A01",
    ),
    (
        'Metro Lineal de Tubería Conduit Flexible Licuatite | 35 [mm] (1 1/4")',
        "ML", "7", "420", 7.0, 420.0, 2940.0, "5529E709",
    ),
    (
        'Metro Lineal de Tubería Conduit Flexible Licuatite | 63 [mm] (2 1/2")',
        "ML", "2", "1100", 2.0, 1100.0, 2200.0, "CE2F93DF",
    ),
]


class CotTubeFixturesTest(unittest.TestCase):

    def _run_cot_case(self, description, unit, qty_str, price_str,
                      expected_qty, expected_price, expected_total, expected_catalog_id):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-COT-20260523.csv")
            _write_cot(path, [(description, unit, qty_str, price_str)])
            result = parse_quote_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [], msg=f"Errors for: {description}")
        self.assertEqual(len(result["items"]), 1)
        item = result["items"][0]
        self.assertEqual(item["description"], description)
        self.assertEqual(item["qty"], expected_qty, msg=f"qty mismatch for: {description}")
        self.assertAlmostEqual(item["price"], expected_price, places=2,
                               msg=f"price mismatch for: {description}")
        self.assertAlmostEqual(item["total"], expected_total, places=2,
                               msg=f"total mismatch for: {description}")
        self.assertEqual(item["catalog_item_id"], expected_catalog_id,
                         msg=f"catalog_item_id mismatch for: {description}")
        self.assertEqual(item["origen"], "csv")

    def test_cot_galvanizado_pared_delgada_27mm_sin_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[0])

    def test_cot_galvanizado_pared_delgada_63mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[1])

    def test_cot_galvanizado_pared_gruesa_27mm_sin_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[2])

    def test_cot_galvanizado_pared_gruesa_63mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[3])

    def test_cot_pvc_sp_27mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[4])

    def test_cot_pvc_sp_63mm_sin_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[5])

    def test_cot_pad_flexible_corrugado_63mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[6])

    def test_cot_metalico_flexible_35mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[7])

    def test_cot_metalico_flexible_63mm_sin_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[8])

    def test_cot_flexible_licuatite_35mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[9])

    def test_cot_flexible_licuatite_63mm_con_precio(self):
        self._run_cot_case(*COT_TUBE_CASES[10])

    def test_cot_with_metadata_proyecto_clave_and_quote_type(self):
        """Metadata #proyecto_clave y #quote_type del archivo COT LISP."""
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM002-V1-I1-COT-20260523.csv")
            _write_cot(
                path,
                [('Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 27 [mm] (1")', "ML", "47", "")],
                meta="#proyecto_clave,OM002,,\n#quote_type,General,,\n#fecha,2026-05-23,,\n",
            )
            result = parse_quote_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["metadata"]["proyecto_clave"], "OM002")
        self.assertEqual(result["metadata"]["quote_type"], "General")
        self.assertEqual(result["metadata"]["fecha"], "2026-05-23")

    def test_cot_mixed_tubes_single_file(self):
        """Múltiples tipos y diámetros en un solo archivo COT."""
        rows = [
            ('Metro Lineal de Tubería Conduit Galvanizado Pared Delgada | 27 [mm] (1")', "ML", "47", ""),
            ('Metro Lineal de Tubería Conduit PVC SP | 27 [mm] (1")', "ML", "60", "180"),
            ('Metro Lineal de Tubería Conduit Metálico Flexible | 35 [mm] (1 1/4")', "ML", "10", "250"),
            ('Metro Lineal de Tubería Conduit Flexible Licuatite | 63 [mm] (2 1/2")', "ML", "2", "1100"),
        ]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-COT-20260523.csv")
            _write_cot(path, rows)
            result = parse_quote_csv(path, catalog=SAMPLE_CATALOG)

        self.assertEqual(result["errors"], [])
        self.assertEqual(len(result["items"]), 4)
        totals = [item["total"] for item in result["items"]]
        self.assertEqual(totals, [0.0, 10800.0, 2500.0, 2200.0])
        catalog_ids = [item["catalog_item_id"] for item in result["items"]]
        self.assertEqual(catalog_ids, ["56A13CED", "CC000001", "C61F3E26", "CE2F93DF"])

    def test_cot_total_rounding_two_decimals(self):
        """total = round(qty * price, 2) — sin acumulación de error flotante."""
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "cot.csv")
            # 3 * 150.333... → 451.0 (not 451.000000001)
            _write_cot(path, [('Concepto Cualquiera', "pza", "3", "150.33")])
            result = parse_quote_csv(path)

        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["items"][0]["total"], 450.99, places=2)


if __name__ == "__main__":
    unittest.main()
