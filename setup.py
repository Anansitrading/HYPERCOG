from setuptools import setup, find_packages

setup(
    name="hypercog-mcp",
    version="0.1.0",
    description="HyperCog MCP - Advanced context enrichment orchestration with Cognee & FalkorDB",
    packages=find_packages(),
    install_requires=[
        "cognee>=0.1.0",
        "cognee-community-hybrid-adapter-falkor>=0.1.0",
        "mcp>=0.9.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
        "httpx>=0.25.0",
        "aiofiles>=23.0.0",
        "pydantic>=2.0.0",
    ],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "hypercog=hypercog_mcp.cli:cli",
        ],
    },
)
