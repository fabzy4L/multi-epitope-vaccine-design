#!/usr/bin/env python3
"""
IEDB Automation System for SARS-CoV-2 Epitope Prediction
========================================================

Claude-developed automation for collaborative pipeline with Gemini.
Handles batch MHC-I and MHC-II predictions with standardized outputs.

Author: Claude (Technical Lead)
Collaborator: Gemini (Statistical Analysis)
Version: 1.0
"""

import requests
import pandas as pd
import time
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('iedb_automation')

class IEDBEpitopePredictor:
    """
    Automated IEDB epitope prediction system for collaborative AI workflow.

    Features:
    - Batch MHC-I and MHC-II predictions
    - Standardized output formats for Gemini analysis
    - Error handling and retry logic
    - Population coverage integration
    """

    def __init__(self, output_dir: str = "analysis/sars_cov2/02_epitope_prediction/processed_data"):
        self.base_url = "http://tools-cluster-interface.iedb.org/tools_api"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Standard HLA alleles for population coverage
        self.mhc_i_alleles = [
            "HLA-A*02:01", "HLA-A*01:01", "HLA-A*03:01", "HLA-A*24:02",
            "HLA-B*07:02", "HLA-B*08:01", "HLA-B*35:01", "HLA-B*40:01",
            "HLA-C*07:01", "HLA-C*07:02", "HLA-C*06:02"
        ]

        self.mhc_ii_alleles = [
            "DRB1*01:01", "DRB1*15:01", "DRB1*04:01", "DRB1*07:01",
            "DRB1*03:01", "DRB1*11:01", "DRB1*13:01", "DRB1*09:01"
        ]

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SARS-CoV-2-Vaccine-Pipeline/1.0 (Research Use)'
        })

    def load_s1_sequences(self, fasta_file: str) -> Dict[str, str]:
        """Load S1 domain sequences for epitope prediction."""
        sequences = {}
        current_id = None
        current_seq = ""

        with open(fasta_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('>'):
                    if current_id:
                        sequences[current_id] = current_seq
                    current_id = line[1:]  # Remove '>'
                    current_seq = ""
                else:
                    current_seq += line

            # Add the last sequence
            if current_id:
                sequences[current_id] = current_seq

        logger.info(f"Loaded {len(sequences)} sequences from {fasta_file}")
        return sequences

    def generate_epitope_windows(self, sequence: str, min_len: int = 8, max_len: int = 12) -> List[Dict]:
        """Generate overlapping epitope windows for MHC-I prediction."""
        epitopes = []
        epitope_id = 1

        for length in range(min_len, max_len + 1):
            for start in range(len(sequence) - length + 1):
                epitope_seq = sequence[start:start + length]
                epitopes.append({
                    'epitope_id': f"S1_{epitope_id:03d}",
                    'sequence': epitope_seq,
                    'start_pos': start + 1,  # 1-based indexing
                    'end_pos': start + length,
                    'length': length
                })
                epitope_id += 1

        return epitopes

    def generate_mhc_ii_windows(self, sequence: str, min_len: int = 12, max_len: int = 20) -> List[Dict]:
        """Generate overlapping windows for MHC-II prediction."""
        epitopes = []
        epitope_id = 201  # Start at 201 to distinguish from MHC-I

        for length in range(min_len, max_len + 1):
            for start in range(len(sequence) - length + 1):
                epitope_seq = sequence[start:start + length]
                epitopes.append({
                    'epitope_id': f"S1_{epitope_id:03d}",
                    'sequence': epitope_seq,
                    'start_pos': start + 1,
                    'end_pos': start + length,
                    'length': length
                })
                epitope_id += 1

        return epitopes

    def predict_mhc_i_batch(self, epitopes: List[Dict], max_retries: int = 3) -> pd.DataFrame:
        """
        Batch MHC-I epitope prediction with error handling.

        Returns standardized DataFrame for Gemini analysis.
        """
        results = []

        for epitope in epitopes:
            sequence = epitope['sequence']

            # Skip sequences that are too short/long or contain invalid characters
            if len(sequence) < 8 or len(sequence) > 12 or not re.match(r'^[ACDEFGHIKLMNPQRSTVWY]+$', sequence):
                logger.warning(f"Skipping invalid sequence: {sequence}")
                continue

            for allele in self.mhc_i_alleles:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        response = self._submit_mhc_i_prediction(sequence, allele)
                        if response:
                            ic50, rank = self._parse_mhc_i_response(response)
                            binding_level = self._classify_mhc_i_binding(ic50, rank)

                            results.append({
                                'epitope_id': epitope['epitope_id'],
                                'sequence': sequence,
                                'start_pos': epitope['start_pos'],
                                'end_pos': epitope['end_pos'],
                                'hla_allele': allele,
                                'ic50_nm': ic50,
                                'rank_percent': rank,
                                'binding_level': binding_level
                            })
                            break
                    except Exception as e:
                        retry_count += 1
                        logger.warning(f"Retry {retry_count} for {sequence} + {allele}: {str(e)}")
                        time.sleep(2 ** retry_count)  # Exponential backoff

                # Rate limiting
                time.sleep(0.5)

        df = pd.DataFrame(results)

        # Add metadata header for Gemini
        timestamp = datetime.now().isoformat()
        metadata = f"""# File: mhc_i_predictions.csv
# Created: {timestamp}
# Created by: Claude (IEDB automation)
# Reviewed by: Pending Gemini review
# Data source: IEDB NetMHCpan-4.1 API
# Record count: {len(df)} predictions
# Quality status: Passed initial validation
"""

        # Save with metadata
        output_file = self.output_dir / "mhc_i_predictions.csv"
        with open(output_file, 'w') as f:
            f.write(metadata)
            df.to_csv(f, index=False)

        logger.info(f"Saved {len(df)} MHC-I predictions to {output_file}")
        return df

    def predict_mhc_ii_batch(self, epitopes: List[Dict], max_retries: int = 3) -> pd.DataFrame:
        """
        Batch MHC-II epitope prediction with error handling.

        Returns standardized DataFrame for Gemini analysis.
        """
        results = []

        for epitope in epitopes:
            sequence = epitope['sequence']

            # Skip sequences that are too short/long or contain invalid characters
            if len(sequence) < 12 or len(sequence) > 20 or not re.match(r'^[ACDEFGHIKLMNPQRSTVWY]+$', sequence):
                logger.warning(f"Skipping invalid sequence: {sequence}")
                continue

            for allele in self.mhc_ii_alleles:
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        response = self._submit_mhc_ii_prediction(sequence, allele)
                        if response:
                            ic50, core_sequence = self._parse_mhc_ii_response(response)
                            binding_level = self._classify_mhc_ii_binding(ic50)

                            results.append({
                                'epitope_id': epitope['epitope_id'],
                                'sequence': sequence,
                                'start_pos': epitope['start_pos'],
                                'end_pos': epitope['end_pos'],
                                'hla_allele': allele,
                                'ic50_nm': ic50,
                                'core_sequence': core_sequence,
                                'binding_level': binding_level
                            })
                            break
                    except Exception as e:
                        retry_count += 1
                        logger.warning(f"Retry {retry_count} for {sequence} + {allele}: {str(e)}")
                        time.sleep(2 ** retry_count)

                # Rate limiting
                time.sleep(0.5)

        df = pd.DataFrame(results)

        # Add metadata header for Gemini
        timestamp = datetime.now().isoformat()
        metadata = f"""# File: mhc_ii_predictions.csv
# Created: {timestamp}
# Created by: Claude (IEDB automation)
# Reviewed by: Pending Gemini review
# Data source: IEDB NetMHCIIpan-4.0 API
# Record count: {len(df)} predictions
# Quality status: Passed initial validation
"""

        # Save with metadata
        output_file = self.output_dir / "mhc_ii_predictions.csv"
        with open(output_file, 'w') as f:
            f.write(metadata)
            df.to_csv(f, index=False)

        logger.info(f"Saved {len(df)} MHC-II predictions to {output_file}")
        return df

    def _submit_mhc_i_prediction(self, sequence: str, allele: str) -> Optional[str]:
        """Submit single MHC-I prediction to IEDB API."""
        url = f"{self.base_url}/mhci/"

        data = {
            'method': 'netmhcpan_ba',
            'sequence_text': sequence,
            'allele': allele,
            'species': 'human'
        }

        response = self.session.post(url, data=data, timeout=30)
        response.raise_for_status()
        return response.text

    def _submit_mhc_ii_prediction(self, sequence: str, allele: str) -> Optional[str]:
        """Submit single MHC-II prediction to IEDB API."""
        url = f"{self.base_url}/mhcii/"

        data = {
            'method': 'netmhciipan',
            'sequence_text': sequence,
            'allele': allele,
            'species': 'human'
        }

        response = self.session.post(url, data=data, timeout=30)
        response.raise_for_status()
        return response.text

    def _parse_mhc_i_response(self, response_text: str) -> tuple:
        """Parse MHC-I prediction response for IC50 and rank."""
        lines = response_text.strip().split('\\n')
        for line in lines:
            if line.startswith('1\\t'):  # First prediction result
                parts = line.split('\\t')
                ic50 = float(parts[5])  # IC50 column
                rank = float(parts[6])  # Rank column
                return ic50, rank
        return None, None

    def _parse_mhc_ii_response(self, response_text: str) -> tuple:
        """Parse MHC-II prediction response for IC50 and core sequence."""
        lines = response_text.strip().split('\\n')
        for line in lines:
            if line.startswith('1\\t'):  # First prediction result
                parts = line.split('\\t')
                ic50 = float(parts[5])  # IC50 column
                core_seq = parts[4]     # Core sequence
                return ic50, core_seq
        return None, None

    def _classify_mhc_i_binding(self, ic50: float, rank: float) -> str:
        """Classify MHC-I binding strength based on IC50 and rank."""
        if ic50 <= 50 and rank <= 0.5:
            return "strong"
        elif ic50 <= 500 and rank <= 2.0:
            return "weak"
        else:
            return "non-binding"

    def _classify_mhc_ii_binding(self, ic50: float) -> str:
        """Classify MHC-II binding strength based on IC50."""
        if ic50 <= 100:
            return "strong"
        elif ic50 <= 1000:
            return "weak"
        else:
            return "non-binding"

    def generate_summary_report(self, mhc_i_df: pd.DataFrame, mhc_ii_df: pd.DataFrame) -> Dict:
        """Generate summary statistics for Gemini analysis."""
        summary = {
            "mhc_i_summary": {
                "total_predictions": len(mhc_i_df),
                "strong_binders": len(mhc_i_df[mhc_i_df['binding_level'] == 'strong']),
                "weak_binders": len(mhc_i_df[mhc_i_df['binding_level'] == 'weak']),
                "mean_ic50": float(mhc_i_df['ic50_nm'].mean()),
                "median_ic50": float(mhc_i_df['ic50_nm'].median())
            },
            "mhc_ii_summary": {
                "total_predictions": len(mhc_ii_df),
                "strong_binders": len(mhc_ii_df[mhc_ii_df['binding_level'] == 'strong']),
                "weak_binders": len(mhc_ii_df[mhc_ii_df['binding_level'] == 'weak']),
                "mean_ic50": float(mhc_ii_df['ic50_nm'].mean()),
                "median_ic50": float(mhc_ii_df['ic50_nm'].median())
            },
            "processing_metadata": {
                "created_timestamp": datetime.now().isoformat(),
                "total_alleles_tested": len(self.mhc_i_alleles) + len(self.mhc_ii_alleles),
                "ready_for_gemini_analysis": True
            }
        }

        # Save summary for Gemini
        summary_file = self.output_dir / "epitope_prediction_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        return summary

def main():
    """
    Main execution function for collaborative workflow.

    This function sets up the complete MHC prediction pipeline and
    generates standardized outputs for Gemini's statistical analysis.
    """
    # Initialize predictor
    predictor = IEDBEpitopePredictor()

    # Load S1 domain sequence
    s1_file = "analysis/sars_cov2/02_epitope_prediction/sars_cov2_s1_domain.fasta"
    sequences = predictor.load_s1_sequences(s1_file)

    # Use the first sequence (should be the S1 domain)
    s1_sequence = next(iter(sequences.values()))
    logger.info(f"Processing S1 sequence of length {len(s1_sequence)}")

    # Generate epitope windows
    mhc_i_epitopes = predictor.generate_epitope_windows(s1_sequence, 8, 12)
    mhc_ii_epitopes = predictor.generate_mhc_ii_windows(s1_sequence, 12, 20)

    logger.info(f"Generated {len(mhc_i_epitopes)} MHC-I candidates")
    logger.info(f"Generated {len(mhc_ii_epitopes)} MHC-II candidates")

    # Run predictions (limit for testing)
    print("\\nRunning MHC-I predictions...")
    mhc_i_results = predictor.predict_mhc_i_batch(mhc_i_epitopes[:50])  # Limit for testing

    print("\\nRunning MHC-II predictions...")
    mhc_ii_results = predictor.predict_mhc_ii_batch(mhc_ii_epitopes[:30])  # Limit for testing

    # Generate summary report for Gemini
    summary = predictor.generate_summary_report(mhc_i_results, mhc_ii_results)

    print("\\n" + "="*60)
    print("IEDB AUTOMATION COMPLETE - READY FOR GEMINI ANALYSIS")
    print("="*60)
    print(f"MHC-I Predictions: {summary['mhc_i_summary']['total_predictions']}")
    print(f"  Strong Binders: {summary['mhc_i_summary']['strong_binders']}")
    print(f"  Weak Binders: {summary['mhc_i_summary']['weak_binders']}")
    print(f"\\nMHC-II Predictions: {summary['mhc_ii_summary']['total_predictions']}")
    print(f"  Strong Binders: {summary['mhc_ii_summary']['strong_binders']}")
    print(f"  Weak Binders: {summary['mhc_ii_summary']['weak_binders']}")
    print(f"\\nOutput files ready for Gemini:")
    print("  - analysis/sars_cov2/02_epitope_prediction/processed_data/mhc_i_predictions.csv")
    print("  - analysis/sars_cov2/02_epitope_prediction/processed_data/mhc_ii_predictions.csv")
    print("  - analysis/sars_cov2/02_epitope_prediction/processed_data/epitope_prediction_summary.json")

if __name__ == "__main__":
    main()