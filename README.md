# AssignTrack: Personalized Academic Deadline Manager

A customizable notification system helping students stay on top of their assignments and deadlines.

## Overview

AssignTrack is a web-based application designed to help students manage their academic workload by providing personalized notifications for upcoming assignments. The system allows students to customize when and how they receive notifications based on their individual preferences and study habits.

## Features

- **Customizable Notification Timeframes**: Set alerts for assignments due within a custom timeframe (e.g., 5 days before deadline)
- **Flexible Notification Scheduling**: Choose when notifications are sent to align with your study schedule
- **Assignment Filtering**: View assignments due on specific days or within a selected timeframe
- **User Account System**: Secure login to manage your courses and assignments
- **Intuitive Interface**: Clean, responsive design for ease of use on any device

## Technology Stack

- **Backend**: Python with Flask framework
- **Database**: PostgreSQL for data storage
- **Frontend**: HTML, CSS for responsive interface
- **Authentication**: Flask-Bcrypt for secure password handling
- **Notifications**: Custom notification system 

## Installation

```bash
# Clone the repository
git clone https://github.com/coolfrancy/AssignTrack-Personalized-Academic-Deadline-Manager.git

# Navigate to project directory
cd AssignTrack

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
# Make sure PostgreSQL is installed and running
# Create a database for the application
# Update database configuration in config.py or .env file

# Run the application
python web/app.py
```

## Usage

1. Register for an account or log in
2. Add your courses and assignments with their due dates
3. Configure your notification preferences:
   - How many days before deadlines you want to be notified
   - What time of day you want to receive notifications
4. Use the filtering system to view assignments due on specific dates

## Future Enhancements

- Browser extension for easier access
- Mobile app version
- Calendar sync options
- Study time recommendations based on assignment complexity

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - francyromelus@gmail.com

Project Link: https://github.com/coolfrancy/AssignTrack-Personalized-Academic-Deadline-Manager.git