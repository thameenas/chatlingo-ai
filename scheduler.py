from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from services.chat_service import ChatService

class NudgeScheduler:
    def __init__(self):
        """Initialize the nudge scheduler"""
        self.chat_service = ChatService()
        self.scheduler = BackgroundScheduler()
        
    def send_daily_nudges(self):
        """Send daily nudges to all users at 9:00 AM IST"""
        self.chat_service.send_daily_nudges()
    
    def start_scheduler(self):
        """Start the scheduler and add the daily nudge job"""
        # Schedule daily nudges at 9:00 AM IST (3:30 AM UTC)
        self.scheduler.add_job(
            func=self.send_daily_nudges,
            trigger=CronTrigger(hour=3, minute=30),  # 9:00 AM IST = 3:30 AM UTC
            id='daily_nudges',
            name='Send daily nudges to all users',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        print("Scheduler started - daily nudges will run at 9:00 AM IST")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("Scheduler stopped") 