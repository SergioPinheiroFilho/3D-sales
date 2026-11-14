"""Cálculos financeiros em ienes inteiros."""

from dataclasses import dataclass, fields


@dataclass(frozen=True)
class UnitEconomics:
    price_jpy: int
    material_jpy: int
    energy_jpy: int
    consumables_jpy: int
    packaging_jpy: int
    shipping_jpy: int
    commission_jpy: int
    variable_losses_jpy: int

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{field.name} deve ser um inteiro não negativo em JPY.")

    @property
    def contribution_jpy(self) -> int:
        costs = (
            self.material_jpy + self.energy_jpy + self.consumables_jpy
            + self.packaging_jpy + self.shipping_jpy + self.commission_jpy
            + self.variable_losses_jpy
        )
        return self.price_jpy - costs
