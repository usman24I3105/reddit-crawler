"""
APScheduler service for running scheduled crawler jobs.
"""
import os
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from src.pipeline.crawler_pipeline import CrawlerPipeline
from src.config.settings import CrawlerConfig
from src.automation import AutoExpireService, AutoUnassignService
from src.utils.logging import get_logger

logger = get_logger(__name__)


class SchedulerService:
    """
    APScheduler service for managing scheduled crawler jobs.
    Provides job locking to prevent concurrent executions.
    """
    
    def __init__(self):
        """Initialize the scheduler service"""
        # Get interval from environment variable (default: 12 hours)
        self.interval_hours = int(os.getenv('CRAWLER_INTERVAL_HOURS', '12'))
        
        # Job locking mechanism
        self._job_lock = threading.Lock()
        self._job_running = False
        self._last_run_time: Optional[datetime] = None
        self._next_run_time: Optional[datetime] = None
        
        # Initialize scheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': ThreadPoolExecutor(max_workers=1)  # Single worker to prevent overlap
        }
        job_defaults = {
            'coalesce': True,  # Combine multiple pending executions into one
            'max_instances': 1,  # Only one instance can run at a time
            'misfire_grace_time': 3600  # 1 hour grace time for missed jobs
        }
        
        self.scheduler = BackgroundScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        
        # Add event listeners for logging
        self.scheduler.add_listener(self._job_executed_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        
        logger.info(f"SchedulerService initialized with interval: {self.interval_hours} hours")
    
    def start(self):
        """Start the scheduler and add the crawler job"""
        if self.scheduler.running:
            logger.warning("Scheduler is already running")
            return
        
        # Add the scheduled crawler job
        self.scheduler.add_job(
            func=self._run_crawler_sync,
            trigger='interval',
            hours=self.interval_hours,
            id='crawl_reddit_posts',
            name='Crawl Reddit Posts',
            replace_existing=True
        )
        
        # Add auto-expire task (run daily)
        expire_days = int(os.getenv('AUTO_EXPIRE_DAYS', '7'))
        self.scheduler.add_job(
            func=self._run_auto_expire,
            trigger='interval',
            hours=24,  # Run daily
            id='auto_expire_pending',
            name='Auto-Expire Pending Posts',
            replace_existing=True
        )
        
        # Add auto-unassign task (run every 6 hours)
        unassign_hours = int(os.getenv('AUTO_UNASSIGN_HOURS', '24'))
        self.scheduler.add_job(
            func=self._run_auto_unassign,
            trigger='interval',
            hours=6,  # Run every 6 hours
            id='auto_unassign_assigned',
            name='Auto-Unassign Assigned Posts',
            replace_existing=True
        )
        
        # Start the scheduler
        self.scheduler.start()
        
        # Calculate next run time
        self._next_run_time = datetime.now() + timedelta(hours=self.interval_hours)
        
        logger.info(
            f"Scheduler started. Next crawl scheduled in {self.interval_hours} hours "
            f"at {self._next_run_time.isoformat()}"
        )
    
    def shutdown(self, wait: bool = True):
        """Shutdown the scheduler gracefully"""
        if not self.scheduler.running:
            logger.warning("Scheduler is not running")
            return
        
        logger.info("Shutting down scheduler...")
        
        # Wait for any running job to complete if requested
        if wait and self._job_running:
            logger.info("Waiting for current job to complete...")
            timeout = 300  # 5 minutes max wait
            start_time = datetime.now()
            while self._job_running:
                if (datetime.now() - start_time).total_seconds() > timeout:
                    logger.warning("Timeout waiting for job to complete")
                    break
                threading.Event().wait(1)
        
        self.scheduler.shutdown(wait=wait)
        logger.info("Scheduler shut down")
    
    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running
    
    def is_job_running(self) -> bool:
        """Check if a crawler job is currently running"""
        return self._job_running
    
    def get_next_run_time(self) -> Optional[str]:
        """Get the next scheduled run time as ISO string"""
        if self._next_run_time:
            return self._next_run_time.isoformat()
        return None
    
    def get_interval_hours(self) -> int:
        """Get the configured interval in hours"""
        return self.interval_hours
    
    async def run_crawler_job(self) -> Dict[str, Any]:
        """
        Run the crawler job asynchronously.
        This is used by the manual trigger endpoint.
        """
        # Run in thread pool to avoid blocking the event loop
        try:
            # Try to get running loop (Python 3.7+)
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # Fallback to get_event_loop if no running loop
            loop = asyncio.get_event_loop()
        
        result = await loop.run_in_executor(None, self._run_crawler_sync)
        return result
    
    def _run_crawler_sync(self) -> Dict[str, Any]:
        """
        Synchronous wrapper for the crawler job.
        This is called by APScheduler.
        """
        # Check if job is already running (double-check with lock)
        if not self._job_lock.acquire(blocking=False):
            logger.warning("Crawler job is already running, skipping this execution")
            return {
                'status': 'skipped',
                'reason': 'Job already running'
            }
        
        try:
            self._job_running = True
            self._last_run_time = datetime.now()
            
            logger.info("=" * 60)
            logger.info("Starting scheduled Reddit crawl job")
            logger.info(f"Started at: {self._last_run_time.isoformat()}")
            logger.info(f"Interval: {self.interval_hours} hours")
            logger.info("=" * 60)
            
            # Run the crawler pipeline
            pipeline = CrawlerPipeline()
            results = pipeline.run()
            
            # Update next run time
            self._next_run_time = datetime.now() + timedelta(hours=self.interval_hours)
            
            logger.info("=" * 60)
            logger.info("Crawl job completed successfully")
            logger.info(f"Total fetched: {results['total_fetched']}")
            logger.info(f"Total saved: {results['total_saved']}")
            logger.info(f"Duplicates skipped: {results['duplicates_skipped']}")
            if results.get('old_posts_deleted', 0) > 0:
                logger.info(f"Old posts deleted: {results['old_posts_deleted']}")
            logger.info(f"Completed at: {datetime.now().isoformat()}")
            logger.info(f"Next run scheduled at: {self._next_run_time.isoformat()}")
            logger.info("=" * 60)
            
            return {
                'status': 'success',
                'total_fetched': results['total_fetched'],
                'total_saved': results['total_saved'],
                'duplicates_skipped': results['duplicates_skipped'],
                'old_posts_deleted': results.get('old_posts_deleted', 0),
                'started_at': self._last_run_time.isoformat(),
                'completed_at': datetime.now().isoformat(),
                'next_run': self._next_run_time.isoformat()
            }
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"Crawl job failed: {str(e)}", exc_info=True)
            logger.error("=" * 60)
            
            # Update next run time even on failure
            self._next_run_time = datetime.now() + timedelta(hours=self.interval_hours)
            
            return {
                'status': 'failed',
                'error': str(e),
                'started_at': self._last_run_time.isoformat() if self._last_run_time else None,
                'completed_at': datetime.now().isoformat(),
                'next_run': self._next_run_time.isoformat()
            }
        
        finally:
            self._job_running = False
            self._job_lock.release()
    
    def _run_auto_expire(self):
        """Run auto-expire task for pending posts"""
        try:
            expire_days = int(os.getenv('AUTO_EXPIRE_DAYS', '7'))
            service = AutoExpireService(expire_days=expire_days)
            count = service.expire_old_pending_posts()
            if count > 0:
                logger.info(f"Auto-expire task completed: {count} posts expired")
        except Exception as e:
            logger.error(f"Auto-expire task failed: {str(e)}", exc_info=True)
    
    def _run_auto_unassign(self):
        """Run auto-unassign task for assigned posts"""
        try:
            unassign_hours = int(os.getenv('AUTO_UNASSIGN_HOURS', '24'))
            service = AutoUnassignService(unassign_hours=unassign_hours)
            count = service.unassign_old_assigned_posts()
            if count > 0:
                logger.info(f"Auto-unassign task completed: {count} posts unassigned")
        except Exception as e:
            logger.error(f"Auto-unassign task failed: {str(e)}", exc_info=True)
    
    def _job_executed_listener(self, event):
        """Event listener for job execution"""
        if event.exception:
            logger.error(f"Job {event.job_id} raised an exception: {event.exception}")
        else:
            logger.debug(f"Job {event.job_id} executed successfully")

