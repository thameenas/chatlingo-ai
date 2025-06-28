from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from twilio.rest import Client
from datetime import datetime
import os
import json
from models import SessionLocal, LastDayNumber

class NudgeScheduler:
    def __init__(self, twilio_client, twilio_phone_number, build_prompt_func):
        """
        Initialize the nudge scheduler
        
        Args:
            twilio_client: Twilio client instance
            twilio_phone_number: Twilio phone number for sending messages
            build_prompt_func: Function to build prompts for different days
        """
        self.twilio_client = twilio_client
        self.twilio_phone_number = twilio_phone_number
        self.build_prompt_func = build_prompt_func
        self.scheduler = BackgroundScheduler()
        
    def send_daily_nudges(self):
        """Send daily nudges to all users at 9:00 AM IST"""
        try:
            print(f"Starting daily nudge job at {datetime.now()}")
            
            # Get all users from the database
            db = SessionLocal()
            
            try:
                users = db.query(LastDayNumber).all()
                print(f"Found {len(users)} users to send nudges to")
                
                for user_record in users:
                    try:
                        # Get user's current day number and original phone
                        day_number = user_record.day_number
                        original_phone = user_record.original_phone
                        
                        # Generate the first prompt for this day
                        prompt = self.build_prompt_func(day_number)
                        if not prompt:
                            print(f"Invalid day number {day_number} for user {user_record.phone}")
                            continue
                        
                        # Send the prompt via WhatsApp
                        print(f"Sending nudge to user {original_phone} for day {day_number}")
                        print(f"Message: {prompt[:100]}...")  # Show first 100 chars
                        
                        # Send WhatsApp message via Twilio
                        message = self.twilio_client.messages.create(
                            body=prompt,
                            from_=f"whatsapp:{self.twilio_phone_number}",
                            to=f"whatsapp:{original_phone}"
                        )
                        
                        print(f"Message sent successfully. SID: {message.sid}")
                        
                    except Exception as e:
                        print(f"Error sending nudge to user {user_record.phone}: {str(e)}")
                        continue
                        
            finally:
                db.close()
                
            print(f"Daily nudge job completed at {datetime.now()}")
            
        except Exception as e:
            print(f"Error in daily nudge job: {str(e)}")
    
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