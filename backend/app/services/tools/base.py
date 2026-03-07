"""
Base class for all PhantomAI OSINT tools
"""
import time
from abc import ABC, abstractmethod
from app.models.schemas import ToolResult

class BaseTool(ABC):
    name: str = "base"
    description: str = ""

    async def run(self, target: str, target_type: str) -> ToolResult:
        """Execute tool and return result with timing."""
        start = time.time()
        try:
            data = await self.execute(target, target_type)
            duration = (time.time() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                status="success",
                data=data,
                duration_ms=round(duration, 2)
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return ToolResult(
                tool_name=self.name,
                status="error",
                error=str(e),
                duration_ms=round(duration, 2)
            )

    @abstractmethod
    async def execute(self, target: str, target_type: str) -> dict:
        """Each tool implements this method."""
        pass
