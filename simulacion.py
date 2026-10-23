"""Simulacion de una linea de espera M/M/1 mediante eventos discretos."""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass

import simpy


@dataclass
class SimulationResult:
    """Metricas observadas durante la simulacion."""

    arrivals: int
    completed: int
    average_wait: float
    average_system_time: float
    average_queue_length: float
    server_utilization: float


class MM1Queue:
    """Modelo de una fila M/M/1 implementado como procesos SimPy."""

    def __init__(self, env: simpy.Environment, lambd: float, mu: float) -> None:
        if lambd <= 0 or mu <= 0:
            raise ValueError("Las tasas lambda y mu deben ser mayores que cero.")
        if lambd >= mu:
            raise ValueError(
                "Para una M/M/1 estable se requiere lambda < mu "
                "(la utilizacion debe ser menor que 1)."
            )

        self.env = env
        self.lambd = lambd
        self.mu = mu
        self.server = simpy.Resource(env, capacity=1)

        self.arrivals = 0
        self.completed = 0
        self.total_wait = 0.0
        self.total_system_time = 0.0

        self._last_event_time = 0.0
        self._queue_area = 0.0
        self._busy_area = 0.0
        self._busy = False

    def _update_areas(self) -> None:
        """Acumula las areas bajo Lq y el estado ocupado del servidor."""

        elapsed = self.env.now - self._last_event_time
        self._queue_area += len(self.server.queue) * elapsed
        self._busy_area += int(self._busy) * elapsed
        self._last_event_time = self.env.now

    def customer(self, customer_id: int):
        """Proceso de un cliente: llega, espera, recibe servicio y sale."""

        arrival_time = self.env.now
        self._update_areas()
        self.arrivals += 1

        with self.server.request() as request:
            yield request

            self._update_areas()
            wait = self.env.now - arrival_time
            self.total_wait += wait
            self._busy = True

            service_time = random.expovariate(self.mu)
            yield self.env.timeout(service_time)

            self._update_areas()
            self._busy = False
            self.completed += 1
            self.total_system_time += self.env.now - arrival_time

    def arrivals_process(self):
        """Genera llegadas Poisson hasta que la simulacion sea detenida."""

        customer_id = 0
        while True:
            yield self.env.timeout(random.expovariate(self.lambd))
            customer_id += 1
            self.env.process(self.customer(customer_id))


def run_simulation(
    lambd: float = 8.0,
    mu: float = 10.0,
    simulation_time: float = 10_000.0,
    seed: int | None = 42,
) -> SimulationResult:
    """Ejecuta la simulacion y devuelve las metricas observadas."""

    if simulation_time <= 0:
        raise ValueError("El tiempo de simulacion debe ser mayor que cero.")

    if seed is not None:
        random.seed(seed)

    env = simpy.Environment()
    queue = MM1Queue(env, lambd, mu)
    env.process(queue.arrivals_process())
    env.run(until=simulation_time)
    queue._update_areas()

    completed = queue.completed
    return SimulationResult(
        arrivals=queue.arrivals,
        completed=completed,
        average_wait=queue.total_wait / completed if completed else 0.0,
        average_system_time=(
            queue.total_system_time / completed if completed else 0.0
        ),
        average_queue_length=queue._queue_area / simulation_time,
        server_utilization=queue._busy_area / simulation_time,
    )


def theoretical_values(lambd: float, mu: float) -> dict[str, float]:
    """Calcula valores teoricos de una M/M/1 estable."""

    if lambd <= 0 or mu <= 0 or lambd >= mu:
        raise ValueError("Se requiere 0 < lambda < mu.")

    rho = lambd / mu
    return {
        "rho": rho,
        "Lq": rho**2 / (1 - rho),
        "Wq": rho / (mu - lambd),
        "W": 1 / (mu - lambd),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Simulacion de una fila bancaria M/M/1 con SimPy."
    )
    parser.add_argument(
        "--llegadas",
        type=float,
        default=8.0,
        help="Tasa de llegadas lambda (clientes por unidad de tiempo).",
    )
    parser.add_argument(
        "--servicio",
        type=float,
        default=10.0,
        help="Tasa de servicio mu (clientes por unidad de tiempo).",
    )
    parser.add_argument(
        "--tiempo",
        type=float,
        default=10_000.0,
        help="Duracion de la simulacion.",
    )
    parser.add_argument("--semilla", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = run_simulation(
        lambd=args.llegadas,
        mu=args.servicio,
        simulation_time=args.tiempo,
        seed=args.semilla,
    )
    theory = theoretical_values(args.llegadas, args.servicio)

    print("Fila bancaria M/M/1 (eventos discretos)")
    print(f"Clientes llegados:             {result.arrivals}")
    print(f"Clientes atendidos:            {result.completed}")
    print(f"Espera promedio observada:     {result.average_wait:.4f}")
    print(f"Tiempo en sistema observado:   {result.average_system_time:.4f}")
    print(f"Longitud media de fila:         {result.average_queue_length:.4f}")
    print(f"Utilizacion observada:          {result.server_utilization:.4f}")
    print("\nValores teoricos M/M/1")
    print(f"Utilizacion rho:                {theory['rho']:.4f}")
    print(f"Espera promedio Wq:             {theory['Wq']:.4f}")
    print(f"Tiempo en sistema W:            {theory['W']:.4f}")
    print(f"Longitud media de fila Lq:      {theory['Lq']:.4f}")


if __name__ == "__main__":
    main()