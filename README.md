To set up your GitHub **README.md**, you can use the following content which accurately reflects the architecture and functionality of the multi-agent system in your notebook.

---

# Multi-Agent Healthcare Appointment System

A robust, AI-driven healthcare management system built with **LangGraph** and **LangChain**. This system utilizes a **Supervisor-Worker architecture** to automate doctor inquiries and appointment scheduling through natural language.

## 🚀 Key Features

* **Intelligent Orchestration**: A central Supervisor node (GPT-4o) determines user intent and routes tasks to specialized worker agents.
* **Specialized Agents**:
* **Information Agent**: Queries doctor availability and specializations.
* **Booking Agent**: Handles high-stakes operations like scheduling, canceling, and rescheduling.


* **Integrated Toolset**: Direct interface with a CSV-based database for real-time doctor slot management.
* **Strict Validation**: Uses **Pydantic** models to ensure dates (`DD-MM-YYYY HH:MM`) and identification numbers are formatted correctly before processing.
* **Complex Workflows**: The system can intelligently "Reschedule" by chaining "Cancel" and "Set" operations together seamlessly.

## 🏗️ Architecture


The system is modeled as a state machine using **LangGraph**, featuring a supervisor-worker pattern for efficient task delegation.

![System Architecture](System%20Architecture/System%20Architecture.png)
1. **START** → **Supervisor**: Analyzes the query.
2. **Supervisor** → **Information Node**: If the user asks "When is Dr. Smith available?"
3. **Supervisor** → **Booking Node**: If the user asks "Book an appointment for me."
4. **Worker** → **Supervisor**: Reports results, allowing for follow-up questions.
5. **Supervisor** → **END**: When the query is successfully resolved.

## 🛠️ Tech Stack

* **Frameworks**: LangChain, LangGraph
* **LLMs**: OpenAI (GPT-4o)
* **Data Handling**: Pandas (Database simulation via CSV)
* **Validation**: Pydantic

## 📋 Prerequisites

* Python 3.9+
* OpenAI API Key
* A `doctor_availability.csv` file in the `../data/` directory

for automated service workflows.*
