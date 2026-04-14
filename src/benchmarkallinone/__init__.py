from __future__ import annotations

__all__ = ["MultiDatasetCleaningPipeline", "PipelineConfig", "main"]


def __getattr__(name: str):
    if name in __all__:
        from .pipeline import MultiDatasetCleaningPipeline, PipelineConfig, main

        exports = {
            "MultiDatasetCleaningPipeline": MultiDatasetCleaningPipeline,
            "PipelineConfig": PipelineConfig,
            "main": main,
        }
        return exports[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
