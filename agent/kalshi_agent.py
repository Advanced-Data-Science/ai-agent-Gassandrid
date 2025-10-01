import requests
import time
import json
import random
from datetime import datetime
import logging
import os


class KalshiDataAgent:
    """
    AI-powered data collection agent for Kalshi prediction markets.
    Includes: Configuration management, adaptive strategy, quality assessment,
    rate limiting, and automated documentation.
    """

    def __init__(self, config_file=None):
        """Initialize agent with configuration from DMP"""
        self.config = self.load_config(config_file) if config_file else self._default_config()
        self.setup_logging()
        self.data_store = []
        self.collection_stats = {
            'start_time': datetime.now(),
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
        }
        self.delay_multiplier = 1.0

        self.base_url = "https://demo-api.kalshi.co/trade-api/v2"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    def _default_config(self):
        """Default configuration"""
        return {'base_delay': 1.0, 'num_markets': 5, 'status_filter': 'open'}

    def load_config(self, config_file):
        """Load collection parameters from DMP"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except:
            return self._default_config()

    def setup_logging(self):
        """Setup logging for the agent"""
        os.makedirs("../logs", exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/data_collection.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def run_collection(self):
        """Main execution method"""
        self.logger.info("Starting data collection agent")

        try:
            while not self.collection_complete():
                data = self.collect_batch()
                if data:
                    self.process_and_store(data)
                self.assess_performance()
                self.respectful_delay()
        except Exception as e:
            self.logger.error(f"Collection failed: {e}")
        finally:
            self.generate_final_report()

    def collection_complete(self):
        """Check if collection is complete"""
        return len(self.data_store) >= self.config.get('num_markets', 5)

    def collect_batch(self):
        """Collect a batch of data with adaptive strategy"""
        if self.get_success_rate() < 0.8:
            self.adjust_strategy()

        return self.make_api_request()

    def make_api_request(self):
        """Make API calls with rate limiting"""
        self.collection_stats['total_requests'] += 1

        try:
            response = self.session.get(
                f"{self.base_url}/markets",
                params={'limit': 1, 'status': self.config.get('status_filter', 'open')},
                timeout=10
            )

            if response.status_code == 200:
                self.collection_stats['successful_requests'] += 1
                markets = response.json().get('markets', [])
                return markets[0] if markets else None
            else:
                self.collection_stats['failed_requests'] += 1
                self.logger.error(f"API request failed: {response.status_code}")
                return None
        except Exception as e:
            self.collection_stats['failed_requests'] += 1
            self.logger.error(f"Request error: {e}")
            return None

    def process_and_store(self, data):
        """Process and validate data before storing"""
        processed = self.process_data(data)
        if self.validate_data(processed):
            self.data_store.append(processed)
            self.logger.info(f"Stored data point {len(self.data_store)}/{self.config.get('num_markets', 5)}")

    def process_data(self, data):
        """Clean and process collected data"""
        return {
            'ticker': data.get('ticker', 'N/A'),
            'title': data.get('title', 'N/A'),
            'category': data.get('category', 'Unknown'),
            'status': data.get('status', 'Unknown'),
            'last_price': data.get('last_price', 0),
            'volume': data.get('volume', 0),
            'collection_timestamp': datetime.now().isoformat()
        }

    def validate_data(self, data):
        """Validate data quality"""
        for field in ['ticker', 'title', 'category']:
            if not data.get(field) or data.get(field) == 'N/A':
                return False
        return True

    def assess_data_quality(self):
        """Evaluate the quality of collected data"""
        if not self.data_store:
            return 0

        quality_metrics = {
            'completeness': self.check_completeness(),
            'accuracy': self.check_accuracy(),
            'consistency': self.check_consistency(),
            'timeliness': 1.0
        }
        return sum(quality_metrics.values()) / len(quality_metrics)

    def check_completeness(self):
        """Check data completeness"""
        if not self.data_store:
            return 0
        total_fields = sum(len(item) for item in self.data_store)
        filled_fields = sum(sum(1 for v in item.values() if v and v != 'N/A') for item in self.data_store)
        return filled_fields / total_fields if total_fields > 0 else 0

    def check_accuracy(self):
        """Check data accuracy (type validation)"""
        if not self.data_store:
            return 0
        accurate = sum(1 for item in self.data_store
                      if isinstance(item.get('last_price'), (int, float)) and
                         isinstance(item.get('volume'), (int, float)))
        return accurate / len(self.data_store)

    def check_consistency(self):
        """Check data consistency"""
        if len(self.data_store) < 2:
            return 1.0
        first_keys = set(self.data_store[0].keys())
        consistent = sum(1 for item in self.data_store if set(item.keys()) == first_keys)
        return consistent / len(self.data_store)

    def get_success_rate(self):
        """Calculate current success rate"""
        total = self.collection_stats['total_requests']
        return self.collection_stats['successful_requests'] / total if total > 0 else 1.0

    def adjust_strategy(self):
        """Modify collection approach based on performance"""
        success_rate = self.get_success_rate()
        if success_rate < 0.5:
            self.delay_multiplier *= 2
            self.logger.warning(f"Low success rate, increasing delay to {self.delay_multiplier:.2f}x")
        elif success_rate > 0.9:
            self.delay_multiplier *= 0.8
            self.logger.info(f"High success rate, decreasing delay to {self.delay_multiplier:.2f}x")

    def assess_performance(self):
        """Assess overall performance"""
        quality = self.assess_data_quality()
        success = self.get_success_rate()
        self.logger.info(f"Performance - Quality: {quality:.2f}, Success: {success:.2f}")

    def respectful_delay(self):
        """Implement respectful rate limiting"""
        base_delay = self.config.get('base_delay', 1.0)
        jitter = random.uniform(0.5, 1.5)
        time.sleep(base_delay * self.delay_multiplier * jitter)

    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.logger.info("Generating final report")

        duration = (datetime.now() - self.collection_stats['start_time']).total_seconds()

        # Generate all reports
        summary = {
            'total_records': len(self.data_store),
            'success_rate': self.get_success_rate(),
            'quality_score': self.assess_data_quality(),
            'duration_seconds': duration,
            'total_requests': self.collection_stats['total_requests'],
            'successful_requests': self.collection_stats['successful_requests'],
            'failed_requests': self.collection_stats['failed_requests'],
        }

        quality_report = {
            'completeness': self.check_completeness(),
            'accuracy': self.check_accuracy(),
            'consistency': self.check_consistency(),
            'timeliness': 1.0,
            'recommendations': self.generate_recommendations()
        }

        metadata = {
            'collection_date': datetime.now().isoformat(),
            'agent_version': '1.0',
            'data_source': 'Kalshi Markets API',
            'total_records': len(self.data_store),
            'quality_metrics': quality_report,
            'variables': {
                'ticker': 'Market identifier',
                'title': 'Market description',
                'category': 'Market category',
                'status': 'Market status',
                'last_price': 'Last traded price',
                'volume': 'Trading volume',
                'collection_timestamp': 'Collection time'
            }
        }

        # Save all reports
        self.save_reports(summary, quality_report, metadata)

    def generate_recommendations(self):
        """Generate recommendations"""
        recs = []
        if self.get_success_rate() < 0.8:
            recs.append("Increase delay between requests")
        if self.assess_data_quality() < 0.7:
            recs.append("Add validation steps")
        if not recs:
            recs.append("Collection performed well")
        return recs

    def save_reports(self, summary, quality_report, metadata):
        """Save all reports to files"""
        os.makedirs("../json-outputs", exist_ok=True)

        with open('../json-outputs/kalshi_collected_data.json', 'w') as f:
            json.dump(self.data_store, f, indent=2)
        with open('../json-outputs/kalshi_collection_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        with open('../json-outputs/kalshi_quality_report.json', 'w') as f:
            json.dump(quality_report, f, indent=2)
        with open('../json-outputs/kalshi_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        self.logger.info("All reports saved successfully")


def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("KALSHI AI DATA COLLECTION AGENT")
    print("="*60 + "\n")

    agent = KalshiDataAgent()
    agent.run_collection()

    # Display final summary
    print("\n" + "="*60)
    print("COLLECTION COMPLETE - FINAL SUMMARY")
    print("="*60)

    print(f"\nTotal Records Collected: {len(agent.data_store)}")
    print(f"Success Rate: {agent.get_success_rate():.1%}")
    print(f"Quality Score: {agent.assess_data_quality():.1%}")

    print("\n" + "="*60)
    print("\nReports saved to json-outputs/:")
    print("  - kalshi_collected_data.json")
    print("  - kalshi_metadata.json")
    print("  - kalshi_quality_report.json")
    print("  - kalshi_collection_summary.json")
    print("\nLogs saved to logs/data_collection.log")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
