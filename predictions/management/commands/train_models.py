"""
Management Command: train_models
================================
Usage: python manage.py train_models
       python manage.py train_models --dataset path/to/data.csv

Trains all ML models and saves them to ml_module/trained_models/
"""

from django.core.management.base import BaseCommand
from ml_module.predictor import HealthcarePredictionEngine
import time


class Command(BaseCommand):
    help = 'Train all ML models for disease prediction'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dataset',
            type=str,
            default=None,
            help='Path to CSV dataset. If not provided, synthetic data is generated.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('   Healthcare Disease Prediction - ML Training'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))

        engine = HealthcarePredictionEngine()
        dataset_path = options.get('dataset')

        if dataset_path:
            self.stdout.write(f'📂 Using dataset: {dataset_path}')
        else:
            self.stdout.write('🔄 No dataset provided. Generating synthetic training data...')
            self.stdout.write('   (For production, download from: https://www.kaggle.com/datasets/itachi9604/disease-symptom-description-dataset)\n')

        self.stdout.write('🏋️  Training models...\n')
        start_time = time.time()

        try:
            results = engine.train_and_evaluate(csv_path=dataset_path)

            self.stdout.write('\n' + '─'*60)
            self.stdout.write(self.style.SUCCESS('📊 Model Accuracy Results:'))
            self.stdout.write('─'*60)

            for model_name, result in results.items():
                if 'error' not in result:
                    self.stdout.write(
                        f"  {model_name:20s} | "
                        f"Test: {result['test_accuracy']*100:.2f}% | "
                        f"CV: {result['cv_mean']*100:.2f}% ± {result['cv_std']*100:.2f}%"
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"  {model_name:20s} | ERROR: {result['error']}")
                    )

            elapsed = time.time() - start_time
            self.stdout.write('─'*60)
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Best Model: {engine.best_model_name}')
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'   CV Accuracy: {results[engine.best_model_name]["cv_mean"]*100:.2f}%'
                )
            )
            self.stdout.write(f'\n⏱️  Training completed in {elapsed:.1f} seconds')
            self.stdout.write(self.style.SUCCESS('\n💾 Models saved to ml_module/trained_models/'))
            self.stdout.write('='*60 + '\n')

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Training failed: {str(e)}'))
            raise
