from fastmcp import Context, FastMCP

class WeaviatePodcastMCP(FastMCP):
    def __init__(self):
        super().__init__()

    def setup_tools(self):
        """
        Resgiter the tools in the MCP server.
        """