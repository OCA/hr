import logging
import random
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


def populate_wellness_history(env):
    """
    Populates the wellness.check model with historical data for the last 14 days
    based on the current number of employees in the system.
    """
    WellnessCheck = env["wellness.check"]
    Employee = env["hr.employee"]

    # Get the count of employees to simulate a realistic daily response rate
    emp_count = Employee.search_count([])
    if emp_count == 0:
        emp_count = 10  # Default to 10 if no employees are set up yet

    _logger.info("--- Starting Data Population for %s employees ---", emp_count)

    # Example answers for different moods
    pools = {
        "happy": [
            "Great day! Feeling very productive.",
            "The team collaboration was excellent today.",
            "I love the new project roadmap.",
            "Feeling very motivated after the morning meeting.",
        ],
        "neutral": [
            "A normal day at the office.",
            "A bit busy, but I'm managing my tasks.",
            "The workload is okay today.",
            "Routine tasks completed as planned.",
        ],
        "sad": [
            "Feeling a bit overwhelmed with the deadlines.",
            "I'm quite tired today, need to rest.",
            "Found some technical roadblocks that are frustrating.",
            "The communication on the project could be clearer.",
        ],
    }

    today = datetime.now().date()
    total_created = 0

    # Generate records for the last 14 days
    for day_offset in range(14):
        check_date = today - timedelta(days=day_offset)

        # Simulate a 70% to 90% response rate each day
        responsive_count = int(emp_count * random.uniform(0.7, 0.9))

        for _ in range(responsive_count):
            # Weighted distribution: 60% Happy, 30% Neutral, 10% Sad
            rand = random.random()
            if rand < 0.60:
                mood = random.randint(7, 10)
                ans = random.choice(pools["happy"])
            elif rand < 0.90:
                mood = random.randint(4, 6)
                ans = random.choice(pools["neutral"])
            else:
                mood = random.randint(1, 3)
                ans = random.choice(pools["sad"])

            WellnessCheck.create(
                {
                    "date": check_date,
                    "q1_answer": ans,
                    "q2_answer": ans,
                    "q3_answer": ans,
                    "mood_score": mood,
                }
            )
            total_created += 1

    # Commit changes manually since we are in the shell
    env.cr.commit()
    _logger.info("--- Success: %s wellness records created! ---", total_created)


if __name__ == "__main__":
    # "env" is globally available when running this via "odoo shell"
    # We use a try/except to avoid "undefined name" errors in static analysis
    try:
        populate_wellness_history(env)  # noqa: F821
    except NameError:
        _logger.error("This script must be run via 'odoo shell'")
