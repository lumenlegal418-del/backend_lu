from datetime import datetime

from sqlalchemy import DateTime, Float, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Prediccion(Base):
    """Predicciones precalculadas (Holt-Winters) por clasificación, año y mes.
    Se recalcula bajo demanda vía /predicciones/recalcular, no en cada lectura."""

    __tablename__ = "prediccion"
    __table_args__ = (UniqueConstraint("clasificacion", "ano", "mes", name="uq_prediccion_clasificacion_ano_mes"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    clasificacion: Mapped[str] = mapped_column(String(100))
    ano: Mapped[str] = mapped_column(String(4))
    mes: Mapped[str] = mapped_column(String(50))
    valor_predicho: Mapped[float] = mapped_column(Float)
    fecha_calculo: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
