from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

from src.core.config import settings


def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=settings.service_settings.jaeger_host,
                agent_port=settings.service_settings.jaeger_port,
            )
        )
    )
    if settings.service_settings.jaeger_console_output:
        # Чтобы видеть трейсы в консоли
        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(ConsoleSpanExporter())
        )


configure_tracer()