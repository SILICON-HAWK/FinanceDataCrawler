from backend.pipeline.main import FinanceDataPipeline


def get_pipeline() -> FinanceDataPipeline:
    return FinanceDataPipeline()
