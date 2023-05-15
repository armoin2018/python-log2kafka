import subprocess
import concurrent.futures
import json
import yaml
import logging
from confluent_kafka import Producer, KafkaError
import argparse


def produce_record(record, topic, producer, key_field):
    try:
        key = record.get(key_field, None)
        value = json.dumps(record).encode('utf-8')
        producer.produce(topic, key=key, value=value)
        producer.flush()
    except KafkaError as e:
        logging.error('Failed to send record: %s', e)

def process_log_file(file_path, record_pattern, field_delimiter, field_labels, topic, producer, key_field):
    process = subprocess.Popen(['tail', '-F', '-n', '0', file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    current_record = {}

    while True:
        line = process.stdout.readline()
        if line:
            decoded_line = line.decode().strip()

            # Check if the line matches the record pattern
            if decoded_line.startswith(record_pattern):
                if current_record:
                    produce_record(current_record, topic, producer, key_field)

                current_record = {}

            # Split the line by the field delimiter and assign labels to each field
            fields = decoded_line.split(field_delimiter)
            for index, label in enumerate(field_labels):
                if index < len(fields):
                    current_record[label] = fields[index]

def process_log_files(log_files, record_pattern, field_delimiter, field_labels, topic, producer, key_field):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for file_path in log_files:
            future = executor.submit(
                process_log_file,
                file_path,
                record_pattern,
                field_delimiter,
                field_labels,
                topic,
                producer,
                key_field
            )
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error('An error occurred while processing a log file: %s', e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process log file and produce records to Kafka.')
    parser.add_argument('config', help='Path to the configuration YAML file')
    args = parser.parse_args()

    # Load configuration from YAML file
    with open(args.config, 'r') as config_file:
        config = yaml.safe_load(config_file)

    tail_files_in = config['tail_files_in']
    pattern = config['record_pattern']
    delimiter = config['field_delimiter']
    labels = config['field_labels']
    topic = config['kafka_topic']
    key_field = config['key_field']
    log_file_path = config['log_file_path']

    logging.basicConfig(
        filename=log_file_path,
        level=logging.ERROR,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Kafka configuration
    kafka_conf = config['kafka_config']
    producer = Producer(kafka_conf)

    tail_file(tail_files_in, pattern, delimiter, labels, topic, producer, key_field)
