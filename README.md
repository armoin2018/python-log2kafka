# python-log2kafka
Tail log files to Kafka Topic using Python

## Log Processing and Kafka Producer

This Python script reads a log file, splits the records based on a delimiter, assigns labels to each field, converts the record into a JSON object, and produces it to a Kafka topic. It supports log files that get rolled by date without interrupting the process.

### Prerequisites

- Python 3.x
- `confluent-kafka` library: Install it using `pip install confluent-kafka`
- `PyYAML` library: Install it using `pip install pyyaml`

## Dependencies
* **subprocess:** To execute the tail command and read the log file.
* **json:** To serialize records as JSON objects.
* **confluent_kafka:** To create a Kafka producer and produce messages.
* **yaml:** To parse the configuration YAML file.
* **argparse:** To handle command-line arguments.

### Usage

1. Create a YAML configuration file (e.g., `config.yaml`) with the following structure:

```yaml
tail_files_in: 
  - /path/to/logfile1.log
  - /path/to/logfile2.log
  - /path/to/logfile3.log
record_pattern: "[START]"
field_delimiter: ","
field_labels:
  - field1
  - field2
  - field3
kafka_topic: logs_topic
key_field: field1
kafka_config:
  bootstrap.servers: kafka_broker1:9093,kafka_broker2:9093
  security.protocol: ssl
  ssl.ca.location: /path/to/ca_certificate.pem
  ssl.certificate.location: /path/to/client_certificate.pem
  ssl.key.location: /path/to/client_key.pem
  ssl.key.password: password
  message.send.max.retries: 5
```


2. Run the script providing the path to the configuration YAML file as an argument:

```bash
$ python log2kafka.py config.yaml
```

## Code Explanation
* The script loads the configuration from the YAML file specified as a command-line argument.
* It reads a log file (log_file) and follows it as new lines are added.
* Each line that matches the record_pattern is treated as a new record, and the script splits it using the field_delimiter.
* The script assigns the field_labels to the respective fields, constructing a dictionary for each record.
* The records are converted to JSON objects and produced to the Kafka topic (kafka_topic) using the specified Kafka configuration (kafka_config).
* The key_field determines the field or combination of fields used as the message key in Kafka.

