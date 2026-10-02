# Tests Automatizados - Huella Forense

Esta carpeta centraliza los tests automatizados desarrollados con `pytest` para verificar la robustez funcional del sistema:

- [test_huella_forense.py](file:///home/wisrovi/Documents/demo/tests/test_huella_forense.py):
  1. `test_case_manager_loads_canonical_cases`: Carga y validación de esquemas JSON con Pydantic de los casos piloto.
  2. `test_audiencia_simulation_flow`: Apertura de sala por el Juez, turno pericial y respuesta del tribunal.
  3. `test_evaluation_engine_gives_positive_feedback_on_proper_terms`: Rúbrica y scoring de vocabulario probatorio y hashes.
  4. `test_reunion_cliente_scenario`: Simulación de comité de crisis tras ransomware.
  5. `test_rd_ia_estimation_blocks`: Verificación de los 14 bloques técnicos y rango de horas.

```bash
python3 -m pytest tests/ -v
```
