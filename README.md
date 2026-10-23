# Simulación de una línea de espera M/M/1

## Proceso modelado

Se modela una ventanilla bancaria: los clientes llegan al banco, esperan en
una sola fila y son atendidos por un único cajero. El orden de atención es
FCFS (*first come, first served*).

## Propiedades de Kendall

La notación es **M/M/1**:

- Primer `M`: las llegadas siguen un proceso de Poisson, con tiempos entre
  llegadas exponenciales de tasa `lambda`.
- Segundo `M`: los tiempos de servicio son exponenciales de tasa `mu`.
- `1`: existe un solo servidor (el cajero).
- La disciplina es FCFS, con capacidad de fila ilimitada y población de
  clientes potencialmente infinita.

Cada llegada, solicitud de servicio, inicio de servicio y salida es un evento
discreto gestionado por SimPy.

## Instalación

```powershell
python -m pip install simpy
```

## Ejecución

```powershell
python simulacion.py --llegadas 8 --servicio 10 --tiempo 10000 --semilla 42
```
