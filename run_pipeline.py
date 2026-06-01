#!/usr/bin/env python3
"""
Multi-Epitope Vaccine Design Pipeline - Main Runner
=================================================

Complete automated pipeline for SARS-CoV-2 multi-epitope vaccine design.
Executes all stages from epitope generation to structural validation.

Usage:
    python run_pipeline.py [--stage STAGE] [--config CONFIG]

Author: Fabian Alvarez-Primo, PhD
Date: 2026-06-01
"""

import os
import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('pipeline.log')
        ]
    )
    return logging.getLogger(__name__)

class VaccinePipeline:
    """Main pipeline orchestrator for multi-epitope vaccine design."""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize pipeline with configuration."""
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(__file__).parent
        self.results_dir = self.base_dir / "results" / "sars_cov2"
        self.config = self.load_config(config_file)

        # Create output directories
        self.setup_directories()

    def load_config(self, config_file: Optional[str]) -> Dict:
        """Load pipeline configuration."""
        default_config = {
            'target_protein': 'SARS-CoV-2 S1 domain',
            'protein_length': 685,
            'epitope_lengths': {
                'mhc_i': [8, 9, 10, 11, 12],
                'mhc_ii': [12, 15, 18, 20]
            },
            'binding_thresholds': {
                'mhc_i': {'ic50': 50, 'rank': 0.5},
                'mhc_ii': {'ic50': 50, 'rank': 1.0}
            },
            'construct_variants': 3,
            'validation_enabled': True,
            'structural_analysis': True
        }

        if config_file and os.path.exists(config_file):
            import yaml
            with open(config_file, 'r') as f:
                user_config = yaml.safe_load(f)
            default_config.update(user_config)

        return default_config

    def setup_directories(self):
        """Create necessary directory structure."""
        directories = [
            self.results_dir / "epitope_predictions",
            self.results_dir / "construct_design",
            self.results_dir / "validation",
            self.results_dir / "structural_analysis",
            self.results_dir / "figures"
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Directory structure created at {self.results_dir}")

    def stage_01_epitope_generation(self) -> bool:
        """Stage 01: Generate epitope candidates from S1 protein."""
        self.logger.info("=== STAGE 01: EPITOPE GENERATION ===")

        try:
            from epitope_prediction.create_epitope_files import main as epitope_main

            self.logger.info("Generating epitope candidates...")
            epitope_main()

            self.logger.info("Stage 01 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 01 failed: {str(e)}")
            return False

    def stage_02_iedb_analysis(self) -> bool:
        """Stage 02: Process IEDB results and statistical analysis."""
        self.logger.info("=== STAGE 02: IEDB STATISTICAL ANALYSIS ===")

        try:
            from statistical_analysis.iedb_results_analyzer import main as analyzer_main

            self.logger.info("Processing IEDB binding predictions...")
            analyzer_main()

            self.logger.info("Stage 02 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 02 failed: {str(e)}")
            return False

    def stage_03_epitope_selection(self) -> bool:
        """Stage 03: Select optimal epitopes for construct design."""
        self.logger.info("=== STAGE 03: EPITOPE SELECTION ===")

        try:
            from construct_design.epitope_selector import main as selector_main

            self.logger.info("Selecting optimal epitope combination...")
            selector_main()

            self.logger.info("Stage 03 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 03 failed: {str(e)}")
            return False

    def stage_04_construct_design(self) -> bool:
        """Stage 04: Design multi-epitope vaccine constructs."""
        self.logger.info("=== STAGE 04: CONSTRUCT DESIGN ===")

        try:
            from construct_design.vaccine_constructor import main as constructor_main

            self.logger.info("Designing multi-epitope vaccine constructs...")
            constructor_main()

            self.logger.info("Stage 04 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 04 failed: {str(e)}")
            return False

    def stage_05_validation(self) -> bool:
        """Stage 05: Validate construct properties."""
        self.logger.info("=== STAGE 05: CONSTRUCT VALIDATION ===")

        try:
            from validation.construct_validator import main as validator_main

            self.logger.info("Validating vaccine construct properties...")
            validator_main()

            self.logger.info("Stage 05 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 05 failed: {str(e)}")
            return False

    def stage_06_structural_analysis(self) -> bool:
        """Stage 06: Setup structural analysis framework."""
        self.logger.info("=== STAGE 06: STRUCTURAL ANALYSIS FRAMEWORK ===")

        try:
            from structural_analysis.structural_validator import main as structural_main

            self.logger.info("Setting up structural analysis framework...")
            structural_main()

            self.logger.info("Stage 06 completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Stage 06 failed: {str(e)}")
            return False

    def run_complete_pipeline(self) -> bool:
        """Execute the complete vaccine design pipeline."""
        self.logger.info("🧬 STARTING MULTI-EPITOPE VACCINE DESIGN PIPELINE")
        start_time = time.time()

        stages = [
            ("Epitope Generation", self.stage_01_epitope_generation),
            ("IEDB Analysis", self.stage_02_iedb_analysis),
            ("Epitope Selection", self.stage_03_epitope_selection),
            ("Construct Design", self.stage_04_construct_design),
            ("Validation", self.stage_05_validation),
            ("Structural Framework", self.stage_06_structural_analysis)
        ]

        completed_stages = 0

        for stage_name, stage_func in stages:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Executing: {stage_name}")
            self.logger.info(f"{'='*60}")

            if stage_func():
                completed_stages += 1
                self.logger.info(f"✅ {stage_name} completed successfully")
            else:
                self.logger.error(f"❌ {stage_name} failed")
                break

        # Final summary
        total_time = time.time() - start_time
        success = completed_stages == len(stages)

        self.logger.info(f"\n{'='*60}")
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Completed Stages: {completed_stages}/{len(stages)}")
        self.logger.info(f"Total Runtime: {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
        self.logger.info(f"Status: {'SUCCESS' if success else 'FAILED'}")

        if success:
            self.logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            self.print_results_summary()
        else:
            self.logger.error("💥 PIPELINE EXECUTION FAILED")

        return success

    def run_stage(self, stage_number: int) -> bool:
        """Run a specific pipeline stage."""
        stage_map = {
            1: ("Epitope Generation", self.stage_01_epitope_generation),
            2: ("IEDB Analysis", self.stage_02_iedb_analysis),
            3: ("Epitope Selection", self.stage_03_epitope_selection),
            4: ("Construct Design", self.stage_04_construct_design),
            5: ("Validation", self.stage_05_validation),
            6: ("Structural Framework", self.stage_06_structural_analysis)
        }

        if stage_number not in stage_map:
            self.logger.error(f"Invalid stage number: {stage_number}")
            return False

        stage_name, stage_func = stage_map[stage_number]
        self.logger.info(f"Running Stage {stage_number}: {stage_name}")

        return stage_func()

    def print_results_summary(self):
        """Print summary of pipeline results."""
        self.logger.info(f"\n📊 RESULTS SUMMARY")
        self.logger.info(f"Results directory: {self.results_dir}")

        # Check for key output files
        key_files = [
            "construct_design/selected_epitopes.json",
            "construct_design/version_3_optimized.fasta",
            "validation/construct_validation_report.md",
            "structural_analysis/colabfold_inputs/"
        ]

        for file_path in key_files:
            full_path = self.results_dir / file_path
            status = "✅" if full_path.exists() else "❌"
            self.logger.info(f"{status} {file_path}")

        self.logger.info(f"\n📚 Next Steps:")
        self.logger.info(f"1. Review construct validation report")
        self.logger.info(f"2. Execute ColabFold structure predictions")
        self.logger.info(f"3. Submit to VaxiJen/AllerTop for external validation")
        self.logger.info(f"4. Consider experimental validation of top epitopes")

def main():
    """Main entry point for pipeline execution."""
    parser = argparse.ArgumentParser(
        description='Multi-Epitope Vaccine Design Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--stage', '-s',
        type=int,
        help='Run specific stage (1-6). If not specified, runs complete pipeline.'
    )

    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Configuration file path (YAML format)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        # Initialize pipeline
        pipeline = VaccinePipeline(args.config)

        if args.stage:
            success = pipeline.run_stage(args.stage)
        else:
            success = pipeline.run_complete_pipeline()

        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("Pipeline execution interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())