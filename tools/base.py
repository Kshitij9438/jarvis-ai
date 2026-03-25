from pydantic import BaseModel


class BaseTool:
    name: str
    description: str
    args_schema: type[BaseModel]

    def run(self, **kwargs):
        raise NotImplementedError