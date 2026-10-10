<br/>
<p align="center">
  <h1 align="center">🎓 AI-Powered Course Registration & Advising System</h1>

  <p align="center">
    An intelligent, rule-based expert system designed to automate academic advising, manage course knowledge bases, and generate optimized semester schedules for students.
    <br/>
    <br/>
  </p>
</p>

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=Streamlit&logoColor=white)
![Experta](https://img.shields.io/badge/Experta-Expert_System-brightgreen)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 📖 Table of Contents
- [About the Project](#-about-the-project)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Technologies Built With](#-technologies-built-with)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#-usage)
  - [1. Knowledge Base Editor (Web UI)](#1-knowledge-base-editor-web-ui)
  - [2. Academic Course Adviser (CLI)](#2-academic-course-adviser-cli)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 About the Project

Academic advising can be a complex and time-consuming process. Advisors need to verify a student's passed/failed courses, check complex prerequisite/corequisite chains, ensure CGPA credit limits are not exceeded, and pick the right electives. 

**This project solves that problem** by providing an automated **Expert System** built with Python and `experta`. 
It consists of two main components:
1. **The Knowledge Base Editor**: A sleek web interface (built with Streamlit) for administrators to manage course data without touching code or CSVs directly.
2. **The Course Adviser Engine**: An AI rules engine that analyzes student data and applies academic logic to generate a personalized, rule-compliant course schedule.

---

## ✨ Key Features

* **🧠 Rule-Based Intelligence**: Automatically calculates maximum allowed credit hours based on the student's current CGPA (e.g., Probation vs. Honor roll limits).
* **🛡️ Prerequisite Enforcement**: Scans student transcripts to ensure foundational courses are passed before advanced courses are recommended.
* **⚠️ Failure Priority Engine**: Automatically prioritizes courses a student has failed so they can retake them in the earliest available semester.
* **📊 Knowledge Base Management UI**: A fully interactive web application to perform CRUD (Create, Read, Update, Delete) operations on Core, Elective, and University Requirement courses.
* **📂 Automated CSV Syncing**: All updates made in the Editor UI are dynamically read and parsed by the Adviser Engine in real-time.

---

## 🏗️ System Architecture

1. **Knowledge Base (CSVs)**: Stores all institutional course data (Core courses, Electives, University Requirements).
2. **Editor (Streamlit)**: Reads and writes to the Knowledge Base. 
3. **Adviser (Experta)**: Consumes the Knowledge Base and the Student's input (CGPA, Transcripts, Semester plan) to run facts against defined logical rules and output a final schedule.

---

## 💻 Technologies Built With

* **[Python](https://www.python.org/)** - Core programming language.
* **[Experta](https://github.com/nilp0inter/experta)** - A Python library for building expert systems based on the Rete algorithm (inspired by CLIPS).
* **[Streamlit](https://streamlit.io/)** - For building the rapid and interactive Data/Knowledge Base UI.
* **[Pandas](https://pandas.pydata.org/)** - For efficient data manipulation and querying of the CSV backend.

---

## 🛠️ Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You need Python 3.8 or higher installed on your system.

### Installation

1. **Clone the repository**
   ```sh
   git clone https://github.com/your-username/Course_Registration_System.git
   cd Course_Registration_System
   ```

2. **Install required dependencies**
   ```sh
   pip install pandas streamlit experta
   ```

---

## 💡 Usage

### 1. Knowledge Base Editor (Web UI)

This interface is meant for **Admins or Academic Coordinators** to manage the curriculum.

1. Launch the Streamlit app:
   ```sh
   streamlit run knowledge_base_editor.py
   ```
2. Navigate to `http://localhost:8501` in your browser.
3. You can view all categorized courses, add new curriculum items, and edit or delete existing entries. Changes automatically sync to the underlying `.csv` files.

> **Note:** *(Placeholder for a screenshot of your beautiful Streamlit app)*
> 
> `<img src="link_to_screenshot.png" alt="App UI" width="600"/>`

### 2. Academic Course Adviser (CLI)

This interface is meant for **Students or Advisors** running course generation.

1. Run the rules engine script:
   ```sh
   python rules.py
   ```
2. The terminal will prompt you for:
   - Your **Semester Plan** (e.g., `1`, `2`, `3`...).
   - Your **Current Semester** (`Fall` or `Spring`).
   - Your **CGPA** (to calculate max credit limits).
   - Any **Passed Courses** (Comma separated, e.g., `CS101, MATH101`).
   - Any **Failed Courses** (Comma separated).
3. The AI will output a **📋 Final Recommended Courses** list, your total credit hours, and any **🚫 Excluded Courses** (with the exact reason they were excluded, such as unmet prerequisites).

---

## 🗺️ Roadmap

- [x] Streamlit UI for KB management.
- [x] Experta Rules Engine for advising logic.
- [ ] Migrate Knowledge Base from CSVs to a SQL/NoSQL Database (e.g., PostgreSQL or MongoDB).
- [ ] Build a Web UI for the Student Adviser side (currently CLI).
- [ ] Support for varied Major/Minor degree plans.

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## Author

Tasneem Ibrahim - Rana Sakr - Marc Ihab - Shams abdelaliem - Mortada Mohamed
