"""Main entry point for Python LSP-MCP Server."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from .config import Config, LSPServerConfig, create_default_config, load_config
from .server import run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,  # MCP uses stdout for protocol, log to stderr
)
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Python LSP-MCP Server - MCP server for Language Server Protocol integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default configuration (pylsp)
  python-lsp-mcp

  # Use configuration file
  python-lsp-mcp --config config.toml

  # Single LSP server with custom workspace
  python-lsp-mcp --lsp-command pylsp --workspace /path/to/project

  # Inline LSP configuration
  python-lsp-mcp --lsp-command "pyright-langserver --stdio" --workspace .
        """,
    )

    parser.add_argument(
        "--config",
        "-c",
        type=Path,
        help="Path to TOML configuration file",
    )

    parser.add_argument(
        "--workspace",
        "-w",
        type=Path,
        default=Path.cwd(),
        help="Workspace root path (default: current directory)",
    )

    parser.add_argument(
        "--lsp-command",
        help="Single LSP command to run (e.g., 'pylsp' or 'pyright-langserver --stdio')",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> Config:
    """Create configuration from command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Config object
    """
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        # Override workspace if provided
        if args.workspace != Path.cwd():
            config.workspace = args.workspace
        return config

    if args.lsp_command:
        # Parse command and args
        parts = args.lsp_command.split()
        command = parts[0]
        command_args = parts[1:] if len(parts) > 1 else []

        logger.info(f"Using inline LSP configuration: {command} {command_args}")
        return Config(
            lsps=[
                LSPServerConfig(
                    id="inline",
                    command=command,
                    args=command_args,
                    extensions=[".py", ".pyi"],
                    languages=["python"],
                )
            ],
            workspace=args.workspace,
        )

    # Use default configuration
    logger.info("Using default configuration (pylsp)")
    config = create_default_config()
    config.workspace = args.workspace
    return config


def main() -> None:
    """Main entry point."""
    args = parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    try:
        config = create_config_from_args(args)
        logger.info(f"Starting Python LSP-MCP Server with workspace: {config.workspace}")
        logger.info(f"Configured LSP servers: {[lsp.id for lsp in config.lsps]}")

        # Run the server
        asyncio.run(run_server(config))

    except KeyboardInterrupt:
        logger.info("Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
