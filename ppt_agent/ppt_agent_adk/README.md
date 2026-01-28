# PPT Creation Agent (Google ADK)

A multi-agent system for creating PowerPoint presentations using Google ADK (Agent Development Kit).

## 🏗️ Architecture

This system consists of 4 specialized agents that work together to create presentations:

### 🤖 Agents

1. **PPT Initiator** (`agents/ppt_initiator.py`)
   - Analyzes and cleans user requirements
   - Creates initial PPT state
   - Generates file names and titles

2. **PPT Planner** (`agents/ppt_planner.py`)
   - Plans presentation structure
   - Creates key messages and slide outlines
   - Handles content addition and restructuring

3. **PPT Refiner** (`agents/ppt_refiner.py`)
   - Modifies existing presentations
   - Applies user feedback
   - Improves content quality

4. **PPTX Coder** (`agents/pptx_coder.py`)
   - Generates Python code for PowerPoint creation
   - Executes the code to create actual PPTX files
   - Handles file generation and saving

### 🎯 Orchestrator

- **PPT Orchestrator** (`ppt_orchestrator.py`)
  - Routes user input to appropriate agents
  - Coordinates workflow between agents
  - Maintains conversation history and state

## 📁 File Structure

```
ppt_agent_adk/
├── agents/
│   ├── __init__.py
│   ├── ppt_initiator.py
│   ├── ppt_planner.py
│   ├── ppt_refiner.py
│   └── pptx_coder.py
├── ppt_state.py          # State management
├── ppt_orchestrator.py   # Main orchestrator
├── streamlit_app.py      # Web interface
├── test_system.py        # Test script
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Google ADK

Make sure you have Google ADK credentials configured.

### 3. Test the System

```bash
python test_system.py
```

### 4. Run the Web Interface

```bash
streamlit run streamlit_app.py
```

## 💬 Usage Examples

### Basic Workflow

1. **Initial Request**
   ```
   User: "Create a presentation about artificial intelligence"
   Agent: ppt_initiator (analyzes requirement)
   ```

2. **Add Content**
   ```
   User: "Add slides about machine learning applications"
   Agent: ppt_planner (plans new content)
   ```

3. **Modify Content**
   ```
   User: "Change the title to be more specific"
   Agent: ppt_refiner (applies modifications)
   ```

4. **Download**
   ```
   User: "Download the presentation"
   Agent: pptx_coder (generates PPTX file)
   ```

### Routing Logic

The orchestrator routes user input based on keywords:

- **First time**: → `ppt_initiator`
- **"download", "save", "get"**: → `pptx_coder`
- **"add", "more", "include"**: → `ppt_planner`
- **"change", "modify", "improve"**: → `ppt_refiner`
- **"build", "generate", "create"**: → `ppt_planner`

## 🔧 State Management

The system uses a `PPTState` class to manage:

- **Basic Info**: Title, filename, slide count
- **Key Messages**: Main points with milestone slides
- **Slides**: Individual slide content and layout
- **Conversation History**: Track of all interactions
- **Current Agent**: Which agent last processed the state

### State Serialization

States can be saved/loaded as JSON files:

```python
from ppt_state import save_state_to_file, load_state_from_file

# Save state
save_state_to_file(state, "my_presentation.json")

# Load state
state = load_state_from_file("my_presentation.json")
```

## 🧪 Testing

The `test_system.py` script demonstrates:

- **Routing Logic**: How user input is routed to agents
- **State Management**: Creating and manipulating PPT state
- **Agent Simulation**: Simulated agent responses

Run tests:
```bash
python test_system.py
```

## 🔄 Comparison with LangGraph Version

| Feature | LangGraph Version | ADK Version |
|---------|------------------|-------------|
| **Framework** | LangGraph | Google ADK |
| **State Management** | TypedDict | Dataclass |
| **Workflow** | Graph-based | Orchestrator-based |
| **Streaming** | Built-in | Manual |
| **Progress Tracking** | Native | Custom |
| **Complexity** | Higher | Lower |

## 🎯 Key Features

- ✅ **Multi-agent coordination**
- ✅ **Intent-based routing**
- ✅ **State persistence**
- ✅ **Web interface**
- ✅ **PowerPoint generation**
- ✅ **Conversation history**
- ✅ **Error handling**

## 🚧 Limitations

- **Simplified Logic**: Current implementation uses basic keyword matching
- **No LLM Integration**: Agents use simplified logic instead of actual LLM calls
- **Basic PowerPoint**: Limited slide layouts and formatting
- **No Real-time Streaming**: Unlike LangGraph version

## 🔮 Future Improvements

1. **Enhanced LLM Integration**: Use actual LLM calls in agents
2. **Advanced Routing**: Implement more sophisticated intent detection
3. **Rich PowerPoint Features**: Support for images, charts, animations
4. **Real-time Progress**: Add progress tracking and streaming
5. **Template Support**: Pre-built presentation templates
6. **Collaboration**: Multi-user editing capabilities

## 📝 License

This project is part of the PPT Agent learning system. 