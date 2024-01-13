import os
import shutil
import argparse
import logging
import time

def setup_logger(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def synchronize_folders(source_dir, replica_dir, sync_interval, log_file):
    while True:
        # Check source folder exists
        if not os.path.exists(source_dir):
            logging.error(f"Source folder '{source_dir}' does not exist.")
            return

        # Check replica folder exists, create if not
        if not os.path.exists(replica_dir):
            os.makedirs(replica_dir)
            logging.info(f"Replica folder '{replica_dir}' created.")

        # Iterate over files in source folder
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                source_path = os.path.join(root, file)
                replica_path = os.path.join(replica_dir, os.path.relpath(source_path, source_dir))

                # Check parent directories of replica_path exist
                os.makedirs(os.path.dirname(replica_path), exist_ok=True)

                # Check if the file in the source folder is newer or not present in the replica folder
                if not os.path.exists(replica_path) or os.path.getmtime(source_path) > os.path.getmtime(replica_path):
                    shutil.copy2(source_path, replica_path)
                    logging.info(f"Copied: {source_path} -> {replica_path}")

        # Remove files and directories in the replica folder that are not present in the source folder
        for root, dirs, files in os.walk(replica_dir):
            # Remove files
            for file in files:
                replica_path = os.path.join(root, file)
                source_path = os.path.join(source_dir, os.path.relpath(replica_path, replica_dir))

                if not os.path.exists(source_path):
                    os.remove(replica_path)
                    logging.info(f"Removed: {replica_path}")

            # Remove directories
            for dir in dirs:
                replica_path = os.path.join(root, dir)
                source_path = os.path.join(source_dir, os.path.relpath(replica_path, replica_dir))

                if not os.path.exists(source_path):
                    shutil.rmtree(replica_path)
                    logging.info(f"Removed: {replica_path}")

        logging.info("Synchronization complete.")

        # Sleep for the specified sync interval
        time.sleep(sync_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder Synchronization Program")
    parser.add_argument("source_dir", help="Path to the source folder")
    parser.add_argument("replica_dir", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    args = parser.parse_args()

    setup_logger(args.log_file)

    synchronize_folders(args.source_dir, args.replica_dir, args.sync_interval, args.log_file)