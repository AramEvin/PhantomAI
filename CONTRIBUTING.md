# Contributing to PhantomAI

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

Follow the [Installation](README.md#installation) guide to get the project running locally.

## Adding a New OSINT Tool

1. Create a new file in `backend/app/services/tools/your_tool.py`:

```python
from app.models.schemas import ToolResult, TargetType

class YourTool:
    name = "your_tool"

    async def run(self, target: str, target_type: TargetType) -> ToolResult:
        try:
            # your logic here
            return ToolResult(tool_name=self.name, status="success", data={...})
        except Exception as e:
            return ToolResult(tool_name=self.name, status="error", error=str(e))
```

2. Register it in `backend/app/services/orchestrator.py`:
```python
from app.services.tools.your_tool import YourTool
ALL_TOOLS = [..., YourTool()]
```

3. Add its metadata in `frontend/src/components/tools/ToolCard.tsx` and `ScanProgress.tsx`.

## Adding a New AI Provider

Add a `call_yourprovider()` function in `backend/app/services/ai/analyzer.py` following the same pattern as the existing providers, then add it to the `tasks` list in `MultiAIAnalyzer.analyze()`.

## Code Style

- **Python:** Follow PEP 8. Use `loguru` for logging, not `print`.
- **TypeScript:** Use functional components and hooks. All styles are inline (no CSS framework).
- **Commits:** Use conventional commits — `feat:`, `fix:`, `docs:`, `refactor:`.

## Submitting a PR

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Test manually — run a scan against `8.8.8.8` and verify it completes
5. Open a pull request with a clear description

## Reporting Issues

Please include:
- Your OS and Python version
- The full error traceback
- Which AI providers you have configured
