import time
from datetime import datetime
from typing import Optional


class MainLoop:
    
    def __init__(self):
        self.running = False
        self.cycle_count = 0
        self.start_time: Optional[datetime] = None
        
    def cycle(self) -> None:
        pass
    
    def run(self) -> None:
        self.running = True
        self.start_time = datetime.now()
        self.cycle_count = 0
        
        while self.running:
            cycle_start = time.time()
            
            self.cycle()
            self.cycle_count += 1
            elapsed = time.time() - cycle_start
            sleep_time = max(0, 1.0 - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    def stop(self) -> None:
        """Stop the main loop gracefully."""
        self.running = False