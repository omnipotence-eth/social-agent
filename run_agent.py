import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

def run_agent():
    """Run the social agent continuously with error handling."""
    while True:
        try:
            logging.info("Starting social agent...")
            # Run the agent in a subprocess
            process = subprocess.Popen(
                ['python', 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitor the process
            while True:
                output = process.stdout.readline()
                if output:
                    logging.info(output.strip())
                
                error = process.stderr.readline()
                if error:
                    logging.error(error.strip())
                
                # Check if process has ended
                if process.poll() is not None:
                    break
                    
                time.sleep(1)
            
            # If we get here, the process has ended
            logging.error(f"Agent process ended with return code: {process.returncode}")
            
        except Exception as e:
            logging.error(f"Error running agent: {str(e)}")
        
        # Wait before restarting
        logging.info("Waiting 60 seconds before restarting...")
        time.sleep(60)

if __name__ == "__main__":
    run_agent() 