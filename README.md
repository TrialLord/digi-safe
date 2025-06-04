# Digital Safe

A secure desktop application for storing and managing sensitive information like passwords, notes, and files.

## Features

- Secure user authentication with master password
- AES-256 encryption for all stored data
- Password management with strong password generation
- Modern and intuitive user interface
- Auto-lock functionality
- Secure clipboard handling
- Cross-platform compatibility

## Installation

1. Ensure you have Python 3.8 or higher installed
2. Clone this repository
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python main.py
```

### First-time Setup
1. Launch the application
2. Create a master password when prompted
3. Keep your master password safe - it cannot be recovered if lost

### Security Features
- All data is encrypted using AES-256
- Master password is never stored in plaintext
- Auto-lock after configurable inactivity period
- Secure clipboard handling (clears after 30 seconds)

## Security Notes
- Never share your master password
- Keep your encrypted data file secure
- Regularly backup your encrypted data
- Use strong, unique passwords for all entries

## License
MIT License 