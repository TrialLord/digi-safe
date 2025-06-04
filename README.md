# Digital Safe

A secure password and file management application built with Python and PyQt6.

## Features

- 🔐 Secure password storage with encryption
- 📁 File encryption and secure storage
- 🎨 Modern, intuitive user interface
- 🔄 Real-time data synchronization
- 🔑 Password generation with customizable options
- 🔍 Search functionality for passwords and files
- 📱 Responsive design with smooth animations

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/digital-safe.git
cd digital-safe
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. On first run, you'll be prompted to:
   - Set up a master password
   - Choose a storage location for encrypted data

3. After setup, you can:
   - Add and manage passwords
   - Store and encrypt files
   - Generate secure passwords
   - Search through your stored items
   - Access settings and preferences

## Security Features

- AES-256 encryption for all stored data
- Secure password hashing using PBKDF2
- Automatic clipboard clearing for copied passwords
- Master password protection
- Secure file encryption

## Project Structure

```
digital-safe/
├── icons/                 # Application icons
├── data/                  # Encrypted data storage
├── main.py               # Application entry point
├── main_window.py        # Main application window
├── dashboard.py          # Dashboard view
├── passwords_view.py     # Password management view
├── files_view.py         # File management view
├── settings_view.py      # Settings view
├── data_manager.py       # Data management and encryption
├── crypto.py            # Cryptographic operations
└── requirements.txt      # Project dependencies
```

## Dependencies

- Python 3.8+
- PyQt6
- cryptography
- pyperclip

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Icons designed with a modern, minimalist style
- UI inspired by Material Design principles
- Security features based on industry best practices 