import asyncio
from datetime import datetime, timedelta

class Ticker:
    """Tick sincronizado con el reloj del sistema"""
    def __init__(self):
        self._next_tick = datetime.now()
    async def run(self, callback):
        """Ejecuta callback cada segundo exacto del reloj"""
        while True:
            now = datetime.now()
            self._next_tick = now.replace(microsecond=0) + timedelta(seconds=1)
            await callback()
            sleep_duration = (self._next_tick - datetime.now()).total_seconds()
            if sleep_duration > 0:
                await asyncio.sleep(sleep_duration)
            else:
                print(f"Warning: tick took longer than 1s")
