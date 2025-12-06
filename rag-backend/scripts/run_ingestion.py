"""Script to run the chapter ingestion pipeline."""
import sys
import os
import asyncio
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.embeddings.ingestion import IngestionPipeline
from src.config.settings import settings
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Run the ingestion pipeline."""
    parser = argparse.ArgumentParser(
        description="Ingest book chapters and generate embeddings"
    )
    parser.add_argument(
        "--docs-dir",
        type=str,
        default="../docs",
        help="Path to docs directory containing markdown files"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="**/*.md",
        help="Glob pattern for markdown files (default: **/*.md)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-ingestion of all chapters (deletes existing embeddings)"
    )
    parser.add_argument(
        "--single-file",
        type=str,
        help="Ingest a single file instead of entire directory"
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=5,
        help="Maximum number of concurrent chapters to process"
    )

    args = parser.parse_args()

    logger.info("Starting ingestion pipeline", args=vars(args))

    # Initialize pipeline
    pipeline = IngestionPipeline()

    # Verify Qdrant is accessible
    if not pipeline.vector_store.health_check():
        logger.error("Qdrant health check failed. Please run setup_qdrant.py first.")
        sys.exit(1)

    try:
        if args.single_file:
            # Ingest single file
            logger.info("Ingesting single file", file=args.single_file)
            result = await pipeline.ingest_chapter(
                args.single_file,
                force_update=args.force
            )

            if result["success"]:
                print(f"\n[SUCCESS] Successfully ingested: {args.single_file}")
                print(f"  Chunks generated: {result['chunks_count']}")
                print(f"  Total tokens: {result['tokens_total']}")
                print(f"  Estimated cost: ${result['estimated_cost_usd']:.4f}")
            else:
                print(f"\n[FAILED] Failed to ingest: {args.single_file}")
                print(f"  Error: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        else:
            # Ingest entire directory
            logger.info("Ingesting directory", docs_dir=args.docs_dir)
            result = await pipeline.ingest_directory(
                docs_dir=args.docs_dir,
                pattern=args.pattern,
                force_update=args.force,
                max_concurrent=args.max_concurrent
            )

            # Print summary
            print("\n" + "=" * 60)
            print("INGESTION SUMMARY")
            print("=" * 60)
            print(f"Total files found:        {result['total_files']}")
            print(f"Successfully processed:   {result['successful']}")
            print(f"Failed:                   {result['failed']}")
            print(f"Total chunks generated:   {result['total_chunks_generated']}")
            print(f"Total embeddings stored:  {result['total_embeddings_stored']}")
            print(f"Estimated total cost:     ${result['total_cost_usd']:.4f}")
            print("=" * 60)

            if result['failed_chapters']:
                print("\nFailed chapters:")
                for failed in result['failed_chapters']:
                    print(f"  [X] {failed['chapter']}: {failed['error']}")

            if result['failed'] > 0:
                sys.exit(1)

    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error("Ingestion pipeline failed", error=str(e))
        print(f"\n[ERROR] Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
