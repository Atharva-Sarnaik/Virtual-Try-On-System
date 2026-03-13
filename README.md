# Virtual Try-On System (IDM-VTON)

A web-based application that allows users to virtually try on clothing items using the IDM-VTON (Improved Diffusion Models for Virtual Try-On) model via Replicate API.

## 🚀 Features

- **Interactive UI**: Simple and modern web interface for uploading images.
- **Virtual Try-On**: Process images using state-of-the-art diffusion models to see how clothes look on a person.
- **Demo Mode**: Test the system with pre-configured example images.
- **FastAPI Backend**: Efficient and scalable backend handling API requests and file management.

## 🛠️ Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **AI Model**: [IDM-VTON](https://replicate.com/cuuupid/idm-vton) via [Replicate](https://replicate.com/)
- **Template Engine**: [Jinja2](https://jinja.palletsprojects.com/)
- **Frontend**: Vanilla HTML5, CSS3 (Inter font), and JavaScript (ES6+)

## 📋 Prerequisites

- Python 3.8+
- A Replicate API Token ([Get it here](https://replicate.com/account/api-tokens))

## ⚙️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Atharva-Sarnaik/Virtual-Try-On-System.git
   cd Virtual-Try-On-System
   ```

2. **Navigate to the project directory**:
   ```bash
   cd "Project Using IDM-VTON API"
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   The application requires a Replicate API token. Currently, it's set in `main.py` directly, but it's recommended to use an environment variable:
   ```python
   # In main.py
   os.environ["REPLICATE_API_TOKEN"] = "your_token_here"
   ```

## 🏃 Running the Application

Start the development server:
```bash
python main.py
```
The application will be available at `http://localhost:8000`.

## 📖 Usage Guide

1. **Home Page**: Open your browser and navigate to the local URL.
2. **Upload Images**:
   - **Person Image**: Upload a high-quality photo of the person.
   - **Clothing Image**: Upload the garment you want to try on.
3. **Process**: Click the **"Try On"** button and wait for the AI to generate the result.
4. **Demo**: Use the **"Try Demo"** button to quickly see the system in action using default images.

## 📂 Project Structure

```text
Virtual-Try-On-System/
├── Project Using IDM-VTON API/
│   ├── main.py              # FastAPI application & API integration
│   ├── requirements.txt      # Project dependencies
│   ├── templates/
│   │   └── index.html       # Web interface
│   ├── resources/           # Local assets (models, garments)
│   └── test_tryon.py        # Independent testing script
└── README.md                # Project documentation
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details (if available).
