# 🩺 Doctor Appointment AI Assistant (Multi-Agent System)

A **multi-agent AI hospital appointment system** built using **LangGraph**, **LangChain**, **Groq LLM**, and **Streamlit**.  
It supports **doctor availability checks**, **appointment booking**, **cancellation**, and **rescheduling** using a **CSV-based hospital dataset** with strict validation and human-in-the-loop control.

---

## 🚀 Features
- Check doctor availability by **doctor name** or **specialization**
- Book appointments with **date & time validation**
- Cancel and reschedule appointments
- Multi-agent orchestration using **LangGraph**
- No web search / no external tools
- Human confirmation before booking
- Streamlit UI
- CSV as single source of truth

---

## 🧠 Architecture

```
User (Streamlit UI)
        |
        v
LangGraph Supervisor Agent
        |
        +------------------+
        |                  |
        v                  v
Information Agent     Booking Agent
(Availability)        (Book/Cancel)
        |                  |
        v                  v
availability.csv   availability.csv
```

---

## 🧩 Agents
### Supervisor Agent
- Routes queries to correct agent
- No tool calls
- JSON-only decision making

### Information Agent (Deterministic)
- Uses hospital tools only
- No hallucination
- Handles availability queries

### Booking Agent (Tool-Restricted)
- Handles booking/cancel/reschedule
- Enforces `DD-MM-YYYY HH:MM`
- Uses fixed user ID
- Requires human confirmation

---

## 📁 Project Structure
```
multi-agent-appointment-system/
├── frontend.py
├── ai_agent.py
├── tools.py
├── availability.csv
├── backend.py (optional)
├── workflow.py
├── nodes.py
├── .env
├── requirements.txt
└── README.md
```

---

## 📊 Dataset
**availability.csv**
- doctor_name
- specialization
- date_slot
- is_available
- patient_to_attend

---

## ⚙️ Installation
```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variable
```
GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Run
```bash
streamlit run frontend.py
```

---

## 🧪 Example Inputs
**ID**
```
1000082
```

**Availability**
```
Is Dr John Doe available on 05-08-2024?
```

**Booking**
```
Book an appointment with Dr John Doe on 05-08-2024 08:00
```

---

## 🛡️ Safety Rules
- No web search
- No external APIs
- CSV-only data
- Strict validation
- Human-in-the-loop booking

---

## 🎯 Key Concepts Demonstrated
- Multi-agent architecture
- Tool-grounded LLMs
- LangGraph workflows
- Deterministic + reactive agents
- Real-world system design

---

## 👨‍💻 Author
Doctor Appointment AI Assistant  
Built using LangGraph, LangChain, Groq & Streamlit
